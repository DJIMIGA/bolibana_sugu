import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, API_ENDPOINTS } from '../utils/constants';
import apiClient from '../services/api';
import type { ShippingAddress } from '../types';
import { LoadingScreen } from '../components/LoadingScreen';

const AddressesScreen: React.FC = () => {
  const navigation = useNavigation();
  const [addresses, setAddresses] = useState<ShippingAddress[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const loadAddresses = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }
      const response = await apiClient.get(API_ENDPOINTS.ADDRESSES);
      const raw = response.data;
      // Sécuriser le format de la réponse : tableau direct ou paginé (results)
      const list: ShippingAddress[] = Array.isArray(raw)
        ? raw
        : Array.isArray(raw?.results)
        ? raw.results
        : [];
      setAddresses(list);
    } catch (error: any) {
      // Si c'est une erreur de mode hors ligne, gérer silencieusement
      if (error.isOfflineBlocked || error.message === 'OFFLINE_MODE_FORCED') {
        console.log('[AddressesScreen] 🔌 Mode hors ligne - Aucune adresse chargée');
        return;
      }
      console.error('[AddressesScreen] Error loading addresses:', error);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    const unsubscribe = (navigation as any).addListener('focus', () => {
      loadAddresses(true);
    });
    // Chargement initial
    loadAddresses();
    return unsubscribe;
  }, [navigation]);

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => (navigation as any).goBack()}
        >
          <Ionicons name="arrow-back" size={24} color="#FFFFFF" />
        </TouchableOpacity>
        <Text style={styles.title}>Mes adresses</Text>
      </View>
      
      <View style={styles.content}>
        {isLoading ? (
          <LoadingScreen />
        ) : addresses.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Ionicons
              name="location-outline"
              size={64}
              color={COLORS.TEXT_SECONDARY}
            />
            <Text style={styles.emptyText}>
              Aucune adresse enregistrée
            </Text>
            <Text style={styles.emptySubtext}>
              Ajoutez une adresse pour faciliter vos commandes
            </Text>
            <TouchableOpacity
              style={styles.addButton}
              onPress={() => {
                (navigation as any).navigate('AddAddress');
              }}
            >
              <Ionicons name="add" size={20} color="#FFFFFF" />
              <Text style={styles.addButtonText}>Ajouter une adresse</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View>
            {addresses.map((address) => (
              <View
                key={address.id}
                style={[
                  styles.addressCard,
                  address.is_default ? styles.addressCardDefault : null,
                ]}
              >
                <View style={styles.addressHeader}>
                  <Text style={styles.addressName}>
                    {address.full_name || 'Sans nom'}
                  </Text>
                  {address.is_default && (
                    <View style={styles.defaultBadge}>
                      <Ionicons
                        name="checkmark-circle"
                        size={16}
                        color={COLORS.PRIMARY}
                      />
                      <Text style={styles.defaultBadgeText}>
                        Adresse par défaut
                      </Text>
                    </View>
                  )}
                </View>
                <Text style={styles.addressLine}>
                  {address.street_address}
                  {address.quarter ? `, ${address.quarter}` : ''}
                </Text>
                <Text style={styles.addressLine}>
                  {address.city}
                </Text>
                {address.additional_info ? (
                  <Text style={styles.addressInfo}>
                    {address.additional_info}
                  </Text>
                ) : null}

                <View style={styles.actionsRow}>
                  {!address.is_default && (
                    <TouchableOpacity
                      style={[styles.smallButton, styles.defaultButton]}
                      onPress={async () => {
                        try {
                          await apiClient.post(
                            `/addresses/${address.id}/set-default/`
                          );
                          loadAddresses(true);
                        } catch (error) {
                          console.error(
                            '[AddressesScreen] Error set default:',
                            error
                          );
                        }
                      }}
                    >
                      <Ionicons
                        name="star"
                        size={16}
                        color={COLORS.PRIMARY}
                      />
                      <Text style={styles.smallButtonText}>Par défaut</Text>
                    </TouchableOpacity>
                  )}

                  <TouchableOpacity
                    style={[styles.smallButton, styles.editButton]}
                    onPress={() =>
                      (navigation as any).navigate('AddAddress', {
                        mode: 'edit',
                        address,
                      })
                    }
                  >
                    <Ionicons name="create-outline" size={16} color="#92400E" />
                    <Text style={styles.smallButtonTextEdit}>Modifier</Text>
                  </TouchableOpacity>

                  <TouchableOpacity
                    style={[styles.smallButton, styles.deleteButton]}
                    onPress={() => {
                      Alert.alert(
                        'Supprimer cette adresse',
                        "Êtes-vous sûr de vouloir supprimer cette adresse ?",
                        [
                          { text: 'Annuler', style: 'cancel' },
                          {
                            text: 'Supprimer',
                            style: 'destructive',
                            onPress: async () => {
                              try {
                                await apiClient.delete(
                                  `${API_ENDPOINTS.ADDRESSES}${address.id}/delete/`
                                );
                                loadAddresses(true);
                              } catch (error: any) {
                                console.error(
                                  '[AddressesScreen] Error delete address:',
                                  error?.response?.data || error
                                );
                                const msg =
                                  error?.response?.data?.detail ||
                                  error?.response?.data?.error ||
                                  "Impossible de supprimer cette adresse.";
                                Alert.alert('Erreur', msg);
                              }
                            },
                          },
                        ]
                      );
                    }}
                  >
                    <Ionicons name="trash-outline" size={16} color="#FFFFFF" />
                    <Text style={styles.smallButtonTextDelete}>Supprimer</Text>
                  </TouchableOpacity>
                </View>
              </View>
            ))}

            <TouchableOpacity
              style={[styles.addButton, styles.addButtonFullWidth]}
              onPress={() => (navigation as any).navigate('AddAddress')}
            >
              <Ionicons name="add" size={20} color="#FFFFFF" />
              <Text style={styles.addButtonText}>Ajouter une adresse</Text>
            </TouchableOpacity>

            <View style={styles.infoBox}>
              <Ionicons name="information-circle-outline" size={18} color="#92400E" />
              <Text style={styles.infoText}>
                Une adresse liée à des commandes ne peut pas être supprimée. Vous devez aussi avoir au moins une adresse par défaut active.
              </Text>
            </View>
          </View>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.BACKGROUND,
  },
  header: {
    backgroundColor: COLORS.PRIMARY,
    padding: 24,
    paddingTop: 60,
    flexDirection: 'row',
    alignItems: 'center',
  },
  backButton: {
    marginRight: 12,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  content: {
    padding: 16,
  },
  loaderContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 40,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
    marginTop: 40,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    marginBottom: 24,
  },
  addButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.PRIMARY,
    paddingHorizontal: 24,
    paddingVertical: 14,
    borderRadius: 8,
  },
  addButtonFullWidth: {
    alignSelf: 'stretch',
    justifyContent: 'center',
    marginTop: 16,
  },
  addButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  addressCard: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  addressCardDefault: {
    backgroundColor: '#ECFDF5',
    borderColor: COLORS.PRIMARY,
  },
  addressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  addressName: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.TEXT,
  },
  defaultBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#D1FAE5',
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  defaultBadgeText: {
    marginLeft: 4,
    fontSize: 12,
    color: COLORS.PRIMARY,
    fontWeight: '600',
  },
  addressLine: {
    fontSize: 14,
    color: COLORS.TEXT,
  },
  addressInfo: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
    marginTop: 4,
  },
  actionsRow: {
    flexDirection: 'row',
    marginTop: 12,
    gap: 8,
  },
  smallButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 999,
  },
  defaultButton: {
    backgroundColor: '#D1FAE5',
  },
  editButton: {
    backgroundColor: '#FEF3C7',
  },
  deleteButton: {
    backgroundColor: COLORS.ERROR,
    marginLeft: 'auto',
  },
  smallButtonText: {
    marginLeft: 4,
    fontSize: 12,
    color: COLORS.PRIMARY,
    fontWeight: '600',
  },
  smallButtonTextEdit: {
    marginLeft: 4,
    fontSize: 12,
    color: '#92400E',
    fontWeight: '600',
  },
  smallButtonTextDelete: {
    marginLeft: 4,
    fontSize: 12,
    color: '#FFFFFF',
    fontWeight: '600',
  },
  infoBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF3C7',
    borderRadius: 10,
    padding: 12,
    marginTop: 12,
    borderWidth: 1,
    borderColor: '#FDE68A',
    gap: 8,
  },
  infoText: {
    flex: 1,
    fontSize: 13,
    color: '#92400E',
  },
});

export default AddressesScreen;

