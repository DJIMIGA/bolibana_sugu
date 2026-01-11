import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useAppSelector } from '../store/hooks';
import { COLORS } from '../utils/constants';
import Logo from './Logo';
import { Category } from '../types';
import { useConnectivity } from '../hooks/useConnectivity';
import { connectivityService } from '../services/connectivityService';
import { fetchProducts, fetchCategories } from '../store/slices/productSlice';
import { fetchProfileAsync } from '../store/slices/authSlice';
import { useAppDispatch } from '../store/hooks';
import { Alert, ActivityIndicator } from 'react-native';
import { offlineCacheService } from '../services/offlineCacheService';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { networkMonitor } from '../utils/networkMonitor';

interface HeaderProps {
  searchQuery: string;
  onSearchChange: (text: string) => void;
  onClearSearch?: () => void;
  showCategories?: boolean;
  categories?: Category[];
  onCategoryPress?: (categoryId: number) => void;
  onExplorePress?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  searchQuery,
  onSearchChange,
  onClearSearch,
  showCategories = false,
  categories = [],
  onCategoryPress,
  onExplorePress,
}) => {
  const navigation = useNavigation();
  const dispatch = useAppDispatch();
  const { isOnline } = useConnectivity();
  const { isAuthenticated } = useAppSelector((state) => state.auth);
  const [isDownloading, setIsDownloading] = React.useState(false);
  const [downloadProgress, setDownloadProgress] = React.useState(0);
  const [forceOffline, setForceOffline] = React.useState(false);

  // Charger l'état du mode forcé hors ligne au démarrage depuis le service
  React.useEffect(() => {
    const loadForceOffline = async () => {
      // Attendre que le service soit complètement initialisé
      await connectivityService.waitForInitialization();
      // Utiliser l'état du service plutôt que de charger directement depuis AsyncStorage
      const isForcedOffline = connectivityService.isForceOffline();
      setForceOffline(isForcedOffline);
    };
    loadForceOffline();
  }, []);

  const toggleOfflineMode = async () => {
    const newValue = !forceOffline;
    setForceOffline(newValue);
    await connectivityService.setForceOfflineMode(newValue);
    
    // Pas besoin d'alerte, le changement est visuel via le switch
  };

  // Afficher uniquement les catégories sans parent (catégories principales)
  const displayCategories = categories.filter((c: Category) => !c.parent).slice(0, 8);

  const handlePrepareOffline = async () => {
    // Vérifier la vraie connexion (ignorant le mode forcé)
    if (!connectivityService.getRealConnectionStatus()) {
      Alert.alert('Erreur', 'Vous devez être en ligne pour préparer le mode hors ligne.');
      return;
    }

    Alert.alert(
      'Préparer le mode hors ligne',
      'L\'application va télécharger le catalogue actuel et vos informations pour une utilisation sans connexion. Cela peut consommer des données mobiles.',
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Télécharger',
          onPress: async () => {
            setIsDownloading(true);
            setDownloadProgress(0);
            try {
              console.log('[Offline Prep] 📥 Début du téléchargement...');
              
              // 1. Télécharger les catégories
              setDownloadProgress(10);
              console.log('[Offline Prep] 📥 Téléchargement des catégories...');
              try {
                await dispatch(fetchCategories() as any).unwrap();
                console.log('[Offline Prep] ✅ Catégories téléchargées');
                setDownloadProgress(25);
              } catch (catError: any) {
                console.error('[Offline Prep] ❌ Erreur catégories:', catError);
                throw new Error(`Erreur lors du téléchargement des catégories: ${catError?.message || 'Erreur inconnue'}`);
              }

              // 2. Télécharger les produits (plusieurs pages si nécessaire)
              setDownloadProgress(40);
              console.log('[Offline Prep] 📥 Téléchargement des produits...');
              try {
                let page = 1;
                let hasMore = true;
                let totalProducts = 0;
                
                // Télécharger au moins les 3 premières pages de produits
                while (hasMore && page <= 3) {
                  const result = await dispatch(fetchProducts({ page, append: page > 1 }) as any).unwrap();
                  const products = result.results || [];
                  totalProducts += products.length;
                  console.log(`[Offline Prep] 📥 Page ${page}: ${products.length} produits téléchargés`);
                  
                  // Vérifier s'il y a une page suivante
                  hasMore = result.hasNext !== false && products.length > 0;
                  page++;
                  
                  // Mettre à jour la progression (40% à 75% pour les produits)
                  const progress = 40 + Math.floor((page - 1) * 35 / 3);
                  setDownloadProgress(Math.min(progress, 75));
                }
                
                console.log(`[Offline Prep] ✅ ${totalProducts} produits téléchargés au total`);
                setDownloadProgress(75);
              } catch (prodError: any) {
                console.error('[Offline Prep] ❌ Erreur produits:', prodError);
                // Si on a au moins quelques produits en cache, continuer
                const cached = await offlineCacheService.get('cache_products');
                if (cached && Array.isArray(cached) && cached.length > 0) {
                  console.log('[Offline Prep] ⚠️ Utilisation des produits en cache');
                  setDownloadProgress(75);
                } else {
                  throw new Error(`Erreur lors du téléchargement des produits: ${prodError?.message || prodError || 'Erreur inconnue'}`);
                }
              }

              // 3. Télécharger le profil (optionnel - seulement si connecté)
              if (isAuthenticated) {
                setDownloadProgress(85);
                console.log('[Offline Prep] 📥 Téléchargement du profil...');
                try {
                  await dispatch(fetchProfileAsync() as any).unwrap();
                  console.log('[Offline Prep] ✅ Profil téléchargé');
                } catch (profileError: any) {
                  console.warn('[Offline Prep] ⚠️ Erreur profil (non bloquant):', profileError);
                  // Ne pas bloquer si le profil échoue
                }
              }
              
              setDownloadProgress(100);
              console.log('[Offline Prep] ✅ Téléchargement terminé avec succès');
              
              // Basculer automatiquement en mode hors ligne après le téléchargement
              console.log('[Offline Prep] 🔴 Activation du mode hors ligne après téléchargement...');
              setForceOffline(true);
              await connectivityService.setForceOfflineMode(true);
              
              // Vérifier que le mode est bien activé
              const isNowOffline = connectivityService.getIsOnline();
              console.log('[Offline Prep] ✅ Mode hors ligne activé - getIsOnline():', isNowOffline);
              
              Alert.alert('Succès', 'Données téléchargées ! Mode hors ligne activé.');
            } catch (error: any) {
              console.error('[Offline Prep] ❌ Erreur globale:', error);
              const errorMessage = error?.message || error?.toString() || 'Erreur inconnue';
              Alert.alert(
                'Erreur de téléchargement', 
                `Échec du téléchargement des données hors ligne.\n\n${errorMessage}\n\nVérifiez votre connexion internet et réessayez.`
              );
            } finally {
              setIsDownloading(false);
              setDownloadProgress(0);
            }
          }
        }
      ]
    );
  };

  return (
    <View style={styles.header}>
      <View style={styles.headerTop}>
        <View style={styles.logoContainer}>
          <Logo size="medium" showText={false} />
        </View>
        <View style={styles.offlineControls}>
          {/* Bouton combiné : Indicateur + Switch */}
          <TouchableOpacity
            style={[styles.offlineIndicator, !isOnline && styles.offlineIndicatorActive]}
            onPress={() => {
              const stats = networkMonitor.getStats();
              const report = networkMonitor.getReport();
              
              Alert.alert(
                'État de connexion',
                `Statut: ${isOnline ? 'En ligne' : 'Hors ligne'}\n` +
                `Mode forcé: ${forceOffline ? 'Oui' : 'Non'}\n\n` +
                `📊 Monitoring réseau:\n` +
                `Total: ${stats.total}\n` +
                `✅ Autorisées: ${stats.allowed}\n` +
                `🚫 Bloquées: ${stats.blocked}\n\n` +
                `${forceOffline ? '✅ Mode hors ligne actif - Aucune consommation de données' : '⚠️ Mode en ligne - Consommation de données active'}`,
                [
                  { text: 'OK' },
                  {
                    text: 'Rapport détaillé',
                    onPress: () => {
                      Alert.alert('Rapport détaillé', report);
                    }
                  }
                ]
              );
            }}
            activeOpacity={0.7}
          >
            <Ionicons 
              name={isOnline ? "cloud" : "cloud-offline"} 
              size={18} 
              color={isOnline ? COLORS.PRIMARY : COLORS.WARNING} 
            />
            <Text style={[styles.offlineText, !isOnline && styles.offlineTextActive]}>
              {isOnline ? 'En ligne' : 'Hors ligne'}
            </Text>
            {isDownloading ? (
              <>
                <ActivityIndicator size="small" color={isOnline ? COLORS.PRIMARY : COLORS.WARNING} style={{ marginLeft: 6 }} />
                {downloadProgress > 0 && downloadProgress < 100 && (
                  <Text style={styles.progressText}>{downloadProgress}%</Text>
                )}
              </>
            ) : (
              <TouchableOpacity
                style={[styles.toggleButton, forceOffline && styles.toggleButtonOffline]}
                onPress={async () => {
                  if (forceOffline) {
                    // Actuellement hors ligne → passer en ligne
                    setForceOffline(false);
                    await connectivityService.setForceOfflineMode(false);
                  } else {
                    // Actuellement en ligne → passer en hors ligne (télécharger puis basculer)
                    handlePrepareOffline();
                  }
                }}
                activeOpacity={0.7}
              >
                <View style={[styles.toggleIndicator, forceOffline && styles.toggleIndicatorOffline]} />
              </TouchableOpacity>
            )}
          </TouchableOpacity>
        </View>
      </View>
      <View style={styles.searchContainer}>
        <View style={styles.searchInputContainer}>
          <Ionicons name="search" size={20} color={COLORS.TEXT_SECONDARY} style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder="Rechercher un produit..."
            placeholderTextColor={COLORS.TEXT_SECONDARY}
            value={searchQuery}
            onChangeText={onSearchChange}
          />
          {searchQuery.length > 0 && onClearSearch && (
            <TouchableOpacity
              onPress={onClearSearch}
              style={styles.clearButton}
            >
              <Ionicons name="close-circle" size={20} color={COLORS.TEXT_SECONDARY} />
            </TouchableOpacity>
          )}
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  header: {
    padding: 12, // Réduit de 16 à 12
    paddingTop: 16, // Ajout d'un padding en haut
    paddingBottom: 10, // Padding en bas réduit
    backgroundColor: '#FFFFFF',
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: -4, // Espace négatif pour rapprocher le logo et le champ de recherche
  },
  logoContainer: {
    alignSelf: 'flex-start',
  },
  offlineControls: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  offlineIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: '#F0FDF4',
    borderWidth: 1,
    borderColor: COLORS.PRIMARY,
    gap: 6,
    height: 36, // Hauteur fixe pour alignement
  },
  toggleButton: {
    width: 44,
    height: 24,
    borderRadius: 12,
    backgroundColor: COLORS.PRIMARY,
    padding: 2,
    marginLeft: 8,
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  toggleButtonOffline: {
    backgroundColor: COLORS.WARNING,
  },
  toggleIndicator: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#FFFFFF',
    alignSelf: 'flex-end',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
    elevation: 3,
  },
  toggleIndicatorOffline: {
    alignSelf: 'flex-start',
  },
  offlineIndicatorActive: {
    backgroundColor: '#FEF3C7',
    borderColor: COLORS.WARNING,
  },
  offlineText: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.PRIMARY,
  },
  offlineTextActive: {
    color: COLORS.WARNING,
  },
  prepareButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: '#FFFFFF',
    borderWidth: 1.5,
    borderColor: COLORS.PRIMARY,
    gap: 6,
    minWidth: 44,
    justifyContent: 'center',
    height: 36, // Même hauteur que l'indicateur pour alignement parfait
  },
  prepareButtonDisabled: {
    opacity: 0.6,
  },
  progressText: {
    fontSize: 11,
    fontWeight: '700',
    color: COLORS.PRIMARY,
    marginLeft: 4,
  },
  searchContainer: {
    width: '100%',
    marginTop: -4, // Espace négatif pour rapprocher du logo
  },
  searchInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 10, // Réduit de 12 à 10
    borderWidth: 1.5,
    borderColor: '#D1D5DB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  searchIcon: {
    marginRight: 12,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: COLORS.TEXT,
    padding: 0,
  },
  clearButton: {
    padding: 4,
    marginLeft: 8,
  },
});


