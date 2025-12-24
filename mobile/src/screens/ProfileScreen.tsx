import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  RefreshControl,
  Alert,
  ActivityIndicator,
  TextInput,
  Modal,
} from 'react-native';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { logoutAsync, updateProfileAsync, fetchProfileAsync, fetchLoyaltyInfoAsync } from '../store/slices/authSlice';
import { useNavigation } from '@react-navigation/native';
import { COLORS } from '../utils/constants';
import { formatDate, formatPrice } from '../utils/helpers';
import { Ionicons } from '@expo/vector-icons';

const ProfileScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigation = useNavigation();
  const { user, isLoading, error, loyaltyInfo, isLoadingLoyalty } = useAppSelector((state) => state.auth);
  const [refreshing, setRefreshing] = useState(false);
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [editForm, setEditForm] = useState({
    full_name: '',
    phone: '',
    date_of_birth: '',
    password: '',
  });

  useEffect(() => {
    if (user) {
      // Charger les informations de fidélité
      dispatch(fetchLoyaltyInfoAsync());
    }
  }, [dispatch, user]);

  const handleLogout = () => {
    Alert.alert(
      'Déconnexion',
      'Êtes-vous sûr de vouloir vous déconnecter ?',
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Déconnexion',
          style: 'destructive',
          onPress: async () => {
            try {
              await dispatch(logoutAsync()).unwrap();
            } catch (error: any) {
              Alert.alert('Erreur', error || 'Impossible de se déconnecter');
            }
          },
        },
      ]
    );
  };

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      await dispatch(fetchProfileAsync()).unwrap();
      await dispatch(fetchLoyaltyInfoAsync()).unwrap();
    } catch (error) {
      // Erreur silencieuse
    }
    setRefreshing(false);
  };

  const handleEditProfile = () => {
    console.log('[ProfileScreen] handleEditProfile - User:', user);
    if (user) {
      // Mettre à jour le formulaire avec les données actuelles de l'utilisateur
      let dateOfBirth = '';
      if (user.date_of_birth) {
        // Convertir la date au format jj/mm/aaaa pour l'affichage
        const dateStr = user.date_of_birth.includes('T') 
          ? user.date_of_birth.split('T')[0] 
          : user.date_of_birth;
        
        // Si la date est au format YYYY-MM-DD, la convertir en jj/mm/aaaa
        if (dateStr && dateStr.length >= 10) {
          const [year, month, day] = dateStr.substring(0, 10).split('-');
          if (year && month && day) {
            dateOfBirth = `${day}/${month}/${year}`;
          } else {
            dateOfBirth = dateStr;
          }
        } else {
          dateOfBirth = dateStr;
        }
      }
      
      const formData = {
        full_name: user.full_name || '',
        phone: user.phone || '',
        date_of_birth: dateOfBirth,
        password: '', // Ne pas pré-remplir le mot de passe pour des raisons de sécurité
      };
      
      console.log('[ProfileScreen] handleEditProfile - Form data:', formData);
      setEditForm(formData);
      setShowPassword(false); // Réinitialiser l'état d'affichage du mot de passe
    }
    setIsEditModalVisible(true);
  };

  const handleSaveProfile = async () => {
    console.log('[ProfileScreen] handleSaveProfile - Edit form:', editForm);
    
    // Vérifier que le mot de passe est fourni
    if (!editForm.password || editForm.password.trim() === '') {
      console.log('[ProfileScreen] handleSaveProfile - Password missing');
      Alert.alert('Erreur', 'Veuillez entrer votre mot de passe actuel pour confirmer les modifications');
      return;
    }

    try {
      // Séparer le nom complet en prénom et nom
      const nameParts = editForm.full_name.trim().split(' ');
      const first_name = nameParts[0] || '';
      const last_name = nameParts.slice(1).join(' ') || '';

      // Convertir la date de jj/mm/aaaa vers YYYY-MM-DD pour l'API
      let cleanedDate = null;
      if (editForm.date_of_birth && editForm.date_of_birth.trim() !== '') {
        const dateStr = editForm.date_of_birth.trim();
        // Vérifier si c'est au format jj/mm/aaaa
        const dateMatch = dateStr.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
        if (dateMatch) {
          const [, day, month, year] = dateMatch;
          cleanedDate = `${year}-${month}-${day}`;
        } else {
          // Si ce n'est pas au format jj/mm/aaaa, essayer de le garder tel quel (pour compatibilité)
          cleanedDate = dateStr;
        }
      }

      const updateData = {
        first_name: first_name,
        last_name: last_name,
        phone: editForm.phone || undefined,
        // Si l'utilisateur vide le champ, on envoie explicitement null pour effacer la date
        date_of_birth: cleanedDate,
        password: editForm.password,
      };
      
      console.log('[ProfileScreen] handleSaveProfile - Update data:', {
        ...updateData,
        password: '***' // Ne pas logger le mot de passe en clair
      });
      
      const result = await dispatch(updateProfileAsync(updateData as any)).unwrap();
      console.log('[ProfileScreen] handleSaveProfile - Success, result:', result);
      
      // Réinitialiser le formulaire après succès
      setEditForm({
        full_name: '',
        phone: '',
        date_of_birth: '',
        password: '',
      });
      setIsEditModalVisible(false);
      Alert.alert('Succès', 'Profil mis à jour avec succès');
    } catch (error: any) {
      console.error('[ProfileScreen] handleSaveProfile - Error:', error);
      console.error('[ProfileScreen] handleSaveProfile - Error response:', error?.response);
      console.error('[ProfileScreen] handleSaveProfile - Error data:', error?.response?.data);
      Alert.alert('Erreur', error?.response?.data?.detail || error?.message || error || 'Impossible de mettre à jour le profil');
    }
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.PRIMARY} />
      </View>
    );
  }

  if (!user) {
    return (
      <View style={styles.container}>
        <View style={styles.notLoggedInContainer}>
          <View style={styles.notLoggedInContent}>
            <View style={styles.iconContainer}>
              <Ionicons name="person-circle-outline" size={100} color={COLORS.PRIMARY} />
            </View>
            <Text style={styles.notLoggedInTitle}>Connectez-vous</Text>
            <Text style={styles.notLoggedInSubtitle}>
              Connectez-vous pour accéder à votre profil, vos commandes et bénéficier du programme de fidélité
            </Text>
            
            <View style={styles.benefitsContainer}>
              <View style={styles.benefitItem}>
                <Ionicons name="checkmark-circle" size={24} color={COLORS.PRIMARY} />
                <Text style={styles.benefitText}>Suivez vos commandes</Text>
              </View>
              <View style={styles.benefitItem}>
                <Ionicons name="checkmark-circle" size={24} color={COLORS.PRIMARY} />
                <Text style={styles.benefitText}>Gérez vos adresses</Text>
              </View>
              <View style={styles.benefitItem}>
                <Ionicons name="checkmark-circle" size={24} color={COLORS.PRIMARY} />
                <Text style={styles.benefitText}>Gagnez des points de fidélité</Text>
              </View>
              <View style={styles.benefitItem}>
                <Ionicons name="checkmark-circle" size={24} color={COLORS.PRIMARY} />
                <Text style={styles.benefitText}>Accédez à des offres exclusives</Text>
              </View>
            </View>

            <TouchableOpacity
              style={styles.loginButton}
              onPress={() => {
                // Naviguer vers l'écran de connexion
                (navigation as any).navigate('Login');
              }}
            >
              <Text style={styles.loginButtonText}>Se connecter</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.registerButton}
              onPress={() => {
                (navigation as any).navigate('Signup');
              }}
            >
              <Text style={styles.registerButtonText}>Créer un compte</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.header}>
        <View style={styles.headerBackground} />
        <View style={styles.headerContent}>
          <View style={styles.avatarContainer}>
            {user.profile_picture ? (
              <Image source={{ uri: user.profile_picture }} style={styles.avatar} />
            ) : (
              <View style={styles.avatarPlaceholder}>
                <Text style={styles.avatarText}>
                  {user.full_name ? user.full_name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
                </Text>
              </View>
            )}
            <View style={styles.avatarBadge}>
              <Ionicons name="checkmark-circle" size={20} color="#FFFFFF" />
            </View>
          </View>
          
          <View style={styles.userInfo}>
            <Text style={styles.name}>{user.full_name || user.email}</Text>
            {user.fidelys_number && (
              <View style={styles.fidelysContainer}>
                <Ionicons name="star" size={16} color={COLORS.SECONDARY} />
                <Text style={styles.fidelysNumber}>N° {user.fidelys_number}</Text>
              </View>
            )}
          </View>

          <TouchableOpacity
            style={styles.editButton}
            onPress={handleEditProfile}
          >
            <Ionicons name="create-outline" size={18} color={COLORS.PRIMARY} />
            <Text style={styles.editButtonText}>Modifier</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Informations personnelles</Text>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Email:</Text>
          <Text style={styles.infoValue}>{user.email}</Text>
        </View>
        {user.phone && (
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Téléphone:</Text>
            <Text style={styles.infoValue}>{user.phone}</Text>
          </View>
        )}
        {user.date_of_birth && (
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Date de naissance:</Text>
            <Text style={styles.infoValue}>{formatDate(user.date_of_birth)}</Text>
          </View>
        )}
      </View>

      {/* Section Fidélité */}
      {loyaltyInfo && (
        <View style={styles.section}>
          <View style={styles.loyaltyHeader}>
            <Ionicons name="trophy" size={24} color={loyaltyInfo.loyalty_level_color} />
            <Text style={styles.sectionTitle}>Programme de Fidélité</Text>
          </View>
          
          <View style={[styles.loyaltyCard, { borderColor: loyaltyInfo.loyalty_level_color }]}>
            <View style={styles.loyaltyLevelContainer}>
              <View style={[styles.loyaltyBadge, { backgroundColor: loyaltyInfo.loyalty_level_color }]}>
                <Text style={styles.loyaltyLevelText}>{loyaltyInfo.loyalty_level}</Text>
              </View>
              <Text style={styles.loyaltyNumber}>N° {loyaltyInfo.fidelys_number}</Text>
            </View>
            
            <View style={styles.loyaltyStats}>
              <View style={styles.loyaltyStatItem}>
                <Text style={styles.loyaltyStatValue}>{loyaltyInfo.loyalty_points}</Text>
                <Text style={styles.loyaltyStatLabel}>Points</Text>
              </View>
              <View style={styles.loyaltyStatDivider} />
              <View style={styles.loyaltyStatItem}>
                <Text style={styles.loyaltyStatValue}>{loyaltyInfo.total_orders}</Text>
                <Text style={styles.loyaltyStatLabel}>Commandes</Text>
              </View>
              <View style={styles.loyaltyStatDivider} />
              <View style={styles.loyaltyStatItem}>
                <Text style={styles.loyaltyStatValue}>{formatPrice(loyaltyInfo.total_spent)}</Text>
                <Text style={styles.loyaltyStatLabel}>Total dépensé</Text>
              </View>
            </View>
            
            {loyaltyInfo.next_level && (
              <View style={styles.nextLevelContainer}>
                <Text style={styles.nextLevelText}>
                  {loyaltyInfo.points_needed} points pour atteindre le niveau {loyaltyInfo.next_level}
                </Text>
                <View style={styles.progressBar}>
                  <View 
                    style={[
                      styles.progressFill, 
                      { 
                        width: `${Math.min(100, (loyaltyInfo.loyalty_points / (loyaltyInfo.loyalty_points + loyaltyInfo.points_needed)) * 100)}%`,
                        backgroundColor: loyaltyInfo.loyalty_level_color 
                      }
                    ]} 
                  />
                </View>
              </View>
            )}
          </View>
        </View>
      )}

      <View style={styles.section}>
        <TouchableOpacity
          style={styles.menuItem}
          onPress={() => (navigation as any).navigate('Addresses')}
        >
          <Text style={styles.menuItemText}>Mes adresses</Text>
          <Text style={styles.menuItemArrow}>›</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.menuItem}
          onPress={() => (navigation as any).navigate('Orders')}
        >
          <Text style={styles.menuItemText}>Mes commandes</Text>
          <Text style={styles.menuItemArrow}>›</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.menuItem}
          onPress={() => (navigation as any).navigate('Settings')}
        >
          <Text style={styles.menuItemText}>Paramètres</Text>
          <Text style={styles.menuItemArrow}>›</Text>
        </TouchableOpacity>
      </View>

      {/* Section Informations légales */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Informations légales</Text>
        <TouchableOpacity
          style={styles.menuItem}
          onPress={() => {
            (navigation as any).navigate('WebView', {
              url: 'https://www.bolibana.com/core/cgv/',
              title: 'Conditions Générales de Vente',
            });
          }}
        >
          <Text style={styles.menuItemText}>Conditions Générales de Vente</Text>
          <Text style={styles.menuItemArrow}>›</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.menuItem}
          onPress={() => {
            (navigation as any).navigate('WebView', {
              url: 'https://www.bolibana.com/core/terms-conditions/',
              title: 'Mentions Légales',
            });
          }}
        >
          <Text style={styles.menuItemText}>Mentions Légales</Text>
          <Text style={styles.menuItemArrow}>›</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutButtonText}>Se déconnecter</Text>
      </TouchableOpacity>

      {/* Modal d'édition du profil */}
      <Modal
        visible={isEditModalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setIsEditModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Modifier le profil</Text>
            
            <Text style={styles.inputLabel}>Nom complet</Text>
            <TextInput
              key={`full_name_${isEditModalVisible}`}
              style={styles.input}
              value={editForm.full_name || ''}
              onChangeText={(text) => setEditForm({ ...editForm, full_name: text })}
              placeholder="Nom complet"
            />

            <Text style={styles.inputLabel}>Téléphone</Text>
            <TextInput
              key={`phone_${isEditModalVisible}`}
              style={styles.input}
              value={editForm.phone || ''}
              onChangeText={(text) => setEditForm({ ...editForm, phone: text })}
              placeholder="Téléphone"
              keyboardType="phone-pad"
            />

            <Text style={styles.inputLabel}>Date de naissance</Text>
            <TextInput
              key={`date_of_birth_${isEditModalVisible}`}
              style={styles.input}
              value={editForm.date_of_birth || ''}
              onChangeText={(text) => {
                // Valider et formater la date au format jj/mm/aaaa
                let formattedText = text;
                // Retirer tous les caractères non numériques sauf les slashes
                formattedText = formattedText.replace(/[^\d/]/g, '');
                // Limiter à 10 caractères (jj/mm/aaaa)
                if (formattedText.length > 10) {
                  formattedText = formattedText.substring(0, 10);
                }
                // Ajouter automatiquement les slashes
                if (formattedText.length === 2 && !formattedText.includes('/')) {
                  formattedText = formattedText + '/';
                } else if (formattedText.length === 5 && formattedText.split('/').length === 2) {
                  formattedText = formattedText + '/';
                }
                setEditForm({ ...editForm, date_of_birth: formattedText });
              }}
              placeholder="jj/mm/aaaa"
              keyboardType="numeric"
              maxLength={10}
            />

            <Text style={styles.inputLabel}>Mot de passe actuel *</Text>
            <View style={styles.passwordContainer}>
              <TextInput
                key={`password_${isEditModalVisible}`}
                style={styles.passwordInput}
                value={editForm.password || ''}
                onChangeText={(text) => setEditForm({ ...editForm, password: text })}
                placeholder="Entrez votre mot de passe actuel"
                secureTextEntry={!showPassword}
                autoCapitalize="none"
              />
              <TouchableOpacity
                style={styles.passwordToggle}
                onPress={() => setShowPassword((prev) => !prev)}
              >
                <Ionicons
                  name={showPassword ? 'eye-off-outline' : 'eye-outline'}
                  size={20}
                  color={COLORS.TEXT_SECONDARY}
                />
              </TouchableOpacity>
            </View>
            <Text style={styles.inputHelpText}>
              * Requis pour confirmer les modifications
            </Text>

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setIsEditModalVisible(false)}
              >
                <Text style={styles.cancelButtonText}>Annuler</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modalButton, styles.saveButton]}
                onPress={handleSaveProfile}
              >
                <Text style={styles.saveButtonText}>Enregistrer</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.BACKGROUND,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 16,
    color: COLORS.TEXT_SECONDARY,
  },
  header: {
    backgroundColor: COLORS.PRIMARY,
    paddingTop: 60,
    paddingBottom: 32,
    paddingHorizontal: 20,
    position: 'relative',
    overflow: 'hidden',
  },
  headerBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: COLORS.PRIMARY,
    opacity: 0.95,
  },
  headerContent: {
    alignItems: 'center',
    zIndex: 1,
  },
  avatarContainer: {
    position: 'relative',
    marginBottom: 16,
  },
  avatar: {
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 4,
    borderColor: '#FFFFFF',
    backgroundColor: '#FFFFFF',
  },
  avatarPlaceholder: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 4,
    borderColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 5,
  },
  avatarText: {
    fontSize: 48,
    fontWeight: 'bold',
    color: COLORS.PRIMARY,
  },
  avatarBadge: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: COLORS.PRIMARY,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 3,
    borderColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4,
  },
  userInfo: {
    alignItems: 'center',
    marginBottom: 20,
  },
  name: {
    fontSize: 26,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 8,
    textAlign: 'center',
    textShadowColor: 'rgba(0, 0, 0, 0.1)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
  },
  fidelysContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  fidelysNumber: {
    fontSize: 14,
    color: '#FFFFFF',
    fontWeight: '600',
    marginLeft: 6,
  },
  section: {
    backgroundColor: '#FFFFFF',
    marginTop: 16,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 16,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  infoLabel: {
    fontSize: 16,
    color: COLORS.TEXT_SECONDARY,
  },
  infoValue: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.TEXT,
  },
  menuItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  menuItemText: {
    fontSize: 16,
    color: COLORS.TEXT,
  },
  menuItemArrow: {
    fontSize: 24,
    color: COLORS.TEXT_SECONDARY,
  },
  logoutButton: {
    backgroundColor: COLORS.ERROR,
    borderRadius: 8,
    padding: 16,
    margin: 16,
    alignItems: 'center',
  },
  logoutButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  editButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 20,
    backgroundColor: '#FFFFFF',
    borderRadius: 25,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
    elevation: 3,
  },
  editButtonText: {
    color: COLORS.PRIMARY,
    fontSize: 15,
    fontWeight: '700',
    marginLeft: 6,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 24,
    width: '90%',
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.TEXT,
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 8,
    marginTop: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    color: COLORS.TEXT,
    backgroundColor: '#FFFFFF',
  },
  passwordContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    backgroundColor: '#FFFFFF',
  },
  passwordInput: {
    flex: 1,
    padding: 12,
    fontSize: 16,
    color: COLORS.TEXT,
    paddingRight: 8,
  },
  passwordToggle: {
    paddingHorizontal: 12,
    paddingVertical: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  inputHelpText: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
    marginTop: 4,
    marginBottom: 8,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 24,
  },
  modalButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#F3F4F6',
    marginRight: 8,
  },
  cancelButtonText: {
    color: COLORS.TEXT,
    fontSize: 16,
    fontWeight: '600',
  },
  saveButton: {
    backgroundColor: COLORS.PRIMARY,
    marginLeft: 8,
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  loyaltyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    gap: 8,
  },
  loyaltyCard: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 16,
    borderWidth: 2,
  },
  loyaltyLevelContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  loyaltyBadge: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  loyaltyLevelText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  loyaltyNumber: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
    fontWeight: '600',
  },
  loyaltyStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  loyaltyStatItem: {
    alignItems: 'center',
    flex: 1,
  },
  loyaltyStatValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.PRIMARY,
    marginBottom: 4,
  },
  loyaltyStatLabel: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
  },
  loyaltyStatDivider: {
    width: 1,
    backgroundColor: '#E5E7EB',
  },
  nextLevelContainer: {
    marginTop: 12,
  },
  nextLevelText: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
    marginBottom: 8,
    textAlign: 'center',
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E5E7EB',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 4,
  },
  notLoggedInContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  notLoggedInContent: {
    width: '100%',
    maxWidth: 400,
    alignItems: 'center',
  },
  iconContainer: {
    marginBottom: 24,
  },
  notLoggedInTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.TEXT,
    marginBottom: 12,
    textAlign: 'center',
  },
  notLoggedInSubtitle: {
    fontSize: 16,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    marginBottom: 32,
    lineHeight: 24,
  },
  benefitsContainer: {
    width: '100%',
    marginBottom: 32,
  },
  benefitItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    paddingHorizontal: 8,
  },
  benefitText: {
    fontSize: 16,
    color: COLORS.TEXT,
    marginLeft: 12,
  },
  loginButton: {
    backgroundColor: COLORS.PRIMARY,
    borderRadius: 8,
    padding: 16,
    width: '100%',
    alignItems: 'center',
    marginBottom: 12,
  },
  loginButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  registerButton: {
    backgroundColor: 'transparent',
    borderRadius: 8,
    padding: 16,
    width: '100%',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: COLORS.PRIMARY,
  },
  registerButtonText: {
    color: COLORS.PRIMARY,
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ProfileScreen;
