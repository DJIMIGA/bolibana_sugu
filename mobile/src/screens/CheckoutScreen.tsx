import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Image,
} from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { COLORS, API_ENDPOINTS } from '../utils/constants';
import { formatPrice } from '../utils/helpers';
import apiClient from '../services/api';
import type { ShippingAddress, CartItem } from '../types';
import * as WebBrowser from 'expo-web-browser';
import { LoadingScreen } from '../components/LoadingScreen';

const CheckoutScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const dispatch = useAppDispatch();
  const { items, total, itemsCount } = useAppSelector((state) => state.cart);
  
  const [addresses, setAddresses] = useState<ShippingAddress[]>([]);
  const [selectedAddress, setSelectedAddress] = useState<ShippingAddress | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<'stripe' | 'orange_money' | 'cash_on_delivery'>('stripe');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  useEffect(() => {
    loadAddresses();
  }, []);

  const loadAddresses = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get(API_ENDPOINTS.ADDRESSES);
      const list = Array.isArray(response.data) ? response.data : response.data?.results || [];
      setAddresses(list);
      
      // Sélectionner l'adresse par défaut
      const defaultAddr = list.find((a: ShippingAddress) => a.is_default) || list[0];
      if (defaultAddr) {
        setSelectedAddress(defaultAddr);
      }
    } catch (error: any) {
      // Si c'est une erreur de mode hors ligne, gérer silencieusement
      if (error.isOfflineBlocked || error.message === 'OFFLINE_MODE_FORCED') {
        console.log('[CheckoutScreen] 🔌 Mode hors ligne - Aucune adresse chargée');
        return;
      }
      console.error('[CheckoutScreen] Error loading addresses:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePlaceOrder = async () => {
    if (!selectedAddress) {
      Alert.alert('Erreur', 'Veuillez sélectionner une adresse de livraison');
      return;
    }

    try {
      setIsProcessing(true);
      const response = await apiClient.post(`${API_ENDPOINTS.CART}checkout/`, {
        payment_method: paymentMethod,
        shipping_address_id: selectedAddress.id,
        product_type: 'all',
      });

      const { checkout_url, payment_method, status } = response.data;

      if (payment_method === 'cash_on_delivery' || status === 'confirmed') {
        Alert.alert('Succès', 'Votre commande a été enregistrée avec succès !', [
          { 
            text: 'OK', 
            onPress: () => {
              // Naviguer vers l'onglet Profil puis vers l'écran Commandes
              (navigation as any).navigate('Profile', { screen: 'Orders' });
            } 
          }
        ]);
        return;
      }

      if (checkout_url) {
        // Ouvrir l'URL de paiement
        await WebBrowser.openBrowserAsync(checkout_url, {
          presentationStyle: WebBrowser.WebBrowserPresentationStyle.FULL_SCREEN,
          controlsColor: COLORS.PRIMARY,
        });
        
        // Au retour du navigateur, on redirige vers les commandes
        (navigation as any).navigate('Profile', { screen: 'Orders' });
      }
    } catch (error: any) {
      const msg = error?.response?.data?.error || 'Une erreur est survenue lors de la commande';
      Alert.alert('Erreur', msg);
    } finally {
      setIsProcessing(false);
    }
  };

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Ionicons name="arrow-back" size={24} color="#FFFFFF" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Paiement</Text>
      </View>

      <ScrollView style={styles.content}>
        {/* Résumé du panier */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Résumé de la commande</Text>
          <View style={styles.summaryCard}>
            {items.map((item) => (
              <View key={item.id} style={styles.itemRow}>
                <View style={styles.itemInfo}>
                  <Text style={styles.itemName} numberOfLines={1}>
                    {item.product.name}
                  </Text>
                  {item.product.selected_color_name || item.product.selected_size_name ? (
                    <Text style={styles.itemVariant}>
                      {[item.product.selected_color_name, item.product.selected_size_name]
                        .filter(Boolean)
                        .join(' / ')}
                    </Text>
                  ) : null}
                  <Text style={styles.itemQuantity}>
                    Quantité: {item.quantity} × {formatPrice(item.product.discount_price || item.product.price)}
                  </Text>
                </View>
                <Text style={styles.itemSubtotal}>
                  {formatPrice((item.product.discount_price || item.product.price) * item.quantity)}
                </Text>
              </View>
            ))}
            <View style={styles.summaryDivider} />
            <View style={styles.summaryFooter}>
              <Text style={styles.summaryText}>{itemsCount} article(s)</Text>
              <Text style={styles.summaryTotal}>{formatPrice(total)}</Text>
            </View>
          </View>
        </View>

        {/* Adresse de livraison */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Adresse de livraison</Text>
            <TouchableOpacity onPress={() => (navigation as any).navigate('Addresses')}>
              <Text style={styles.editLink}>Modifier</Text>
            </TouchableOpacity>
          </View>
          
          {selectedAddress ? (
            <View style={styles.addressCard}>
              <Text style={styles.addressName}>{selectedAddress.full_name}</Text>
              <Text style={styles.addressText}>{selectedAddress.street_address}, {selectedAddress.quarter}</Text>
              <Text style={styles.addressText}>{selectedAddress.city}</Text>
            </View>
          ) : (
            <TouchableOpacity 
              style={styles.addAddressButton}
              onPress={() => (navigation as any).navigate('AddAddress')}
            >
              <Ionicons name="add-circle-outline" size={24} color={COLORS.PRIMARY} />
              <Text style={styles.addAddressText}>Ajouter une adresse</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Méthode de paiement */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Méthode de paiement</Text>
          
          <TouchableOpacity 
            style={[styles.paymentCard, paymentMethod === 'stripe' && styles.paymentCardSelected]}
            onPress={() => setPaymentMethod('stripe')}
          >
            <Ionicons name="card-outline" size={24} color={paymentMethod === 'stripe' ? COLORS.PRIMARY : COLORS.TEXT} />
            <Text style={[styles.paymentText, paymentMethod === 'stripe' && styles.paymentTextSelected]}>Carte Bancaire (Stripe)</Text>
            {paymentMethod === 'stripe' && <Ionicons name="checkmark-circle" size={20} color={COLORS.PRIMARY} />}
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.paymentCard, paymentMethod === 'orange_money' && styles.paymentCardSelected]}
            onPress={() => setPaymentMethod('orange_money')}
          >
            <Ionicons name="phone-portrait-outline" size={24} color={paymentMethod === 'orange_money' ? '#FF6600' : COLORS.TEXT} />
            <Text style={[styles.paymentText, paymentMethod === 'orange_money' && styles.paymentTextSelected]}>Orange Money</Text>
            {paymentMethod === 'orange_money' && <Ionicons name="checkmark-circle" size={20} color={COLORS.PRIMARY} />}
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.paymentCard, paymentMethod === 'cash_on_delivery' && styles.paymentCardSelected]}
            onPress={() => setPaymentMethod('cash_on_delivery')}
          >
            <Ionicons name="cash-outline" size={24} color={paymentMethod === 'cash_on_delivery' ? '#059669' : COLORS.TEXT} />
            <Text style={[styles.paymentText, paymentMethod === 'cash_on_delivery' && styles.paymentTextSelected]}>Paiement à la livraison</Text>
            {paymentMethod === 'cash_on_delivery' && <Ionicons name="checkmark-circle" size={20} color={COLORS.PRIMARY} />}
          </TouchableOpacity>
        </View>

        <View style={styles.spacer} />
      </ScrollView>

      {/* Footer avec bouton de confirmation */}
      <View style={styles.footer}>
        <View style={styles.totalRow}>
          <Text style={styles.totalLabel}>Total à payer:</Text>
          <Text style={styles.totalValue}>{formatPrice(total)}</Text>
        </View>
        <TouchableOpacity 
          style={[styles.confirmButton, isProcessing && styles.confirmButtonDisabled]}
          onPress={handlePlaceOrder}
          disabled={isProcessing}
        >
          {isProcessing ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <Text style={styles.confirmButtonText}>
              {paymentMethod === 'cash_on_delivery' ? 'Confirmer la commande' : 'Payer maintenant'}
            </Text>
          )}
        </TouchableOpacity>
      </View>
    </View>
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
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  content: {
    padding: 16,
  },
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.TEXT,
    marginBottom: 12,
  },
  editLink: {
    color: COLORS.PRIMARY,
    fontWeight: '600',
  },
  summaryCard: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  itemRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  itemInfo: {
    flex: 1,
    marginRight: 12,
  },
  itemName: {
    fontSize: 15,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 2,
  },
  itemVariant: {
    fontSize: 13,
    color: COLORS.TEXT_SECONDARY,
    marginBottom: 2,
  },
  itemQuantity: {
    fontSize: 13,
    color: COLORS.TEXT_SECONDARY,
  },
  itemSubtotal: {
    fontSize: 15,
    fontWeight: '700',
    color: COLORS.TEXT,
  },
  summaryDivider: {
    height: 1,
    backgroundColor: '#E5E7EB',
    marginVertical: 12,
  },
  summaryFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  summaryText: {
    fontSize: 16,
    color: COLORS.TEXT_SECONDARY,
  },
  summaryTotal: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.TEXT,
  },
  addressCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  addressName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.TEXT,
    marginBottom: 4,
  },
  addressText: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
    marginBottom: 2,
  },
  addAddressButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderWidth: 1,
    borderStyle: 'dashed',
    borderColor: COLORS.PRIMARY,
    borderRadius: 12,
    backgroundColor: '#F0FDF4',
  },
  addAddressText: {
    marginLeft: 8,
    color: COLORS.PRIMARY,
    fontWeight: '600',
  },
  paymentCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  paymentCardSelected: {
    borderColor: COLORS.PRIMARY,
    backgroundColor: '#F0FDF4',
  },
  paymentText: {
    flex: 1,
    marginLeft: 12,
    fontSize: 16,
    color: COLORS.TEXT,
  },
  paymentTextSelected: {
    fontWeight: 'bold',
    color: COLORS.PRIMARY,
  },
  footer: {
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    paddingBottom: 34,
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  totalLabel: {
    fontSize: 16,
    color: COLORS.TEXT_SECONDARY,
  },
  totalValue: {
    fontSize: 22,
    fontWeight: 'bold',
    color: COLORS.PRIMARY,
  },
  confirmButton: {
    backgroundColor: COLORS.PRIMARY,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  confirmButtonDisabled: {
    opacity: 0.6,
  },
  confirmButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  loaderContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  spacer: {
    height: 40,
  }
});

export default CheckoutScreen;

