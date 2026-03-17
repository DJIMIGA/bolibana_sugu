import React, { useRef, useState } from 'react';
import { View, StyleSheet, Text, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { WebView } from 'react-native-webview';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { COLORS } from '../utils/constants';
import { useAppDispatch } from '../store/hooks';
import { fetchCart } from '../store/slices/cartSlice';

interface PaymentWebViewParams {
  checkout_url: string;
  payment_method: 'stripe' | 'orange_money';
}

// URLs de retour du backend (succès ou annulation)
const SUCCESS_PATTERNS = ['/payment-success/', '/orange-money/return/'];
const CANCEL_PATTERNS = ['/payment-cancel/', '/orange-money/cancel/'];

const isReturnUrl = (url: string, patterns: string[]): boolean => {
  return patterns.some((pattern) => url.includes(pattern));
};

const PAYMENT_ALLOWED_DOMAINS = [
  'bolibana.com',
  'www.bolibana.com',
  'checkout.stripe.com',
  'js.stripe.com',
  'm.stripe.com',
  'api.stripe.com',
  'api.sandbox.orange.com',
  'api.orange.com',
];

const PaymentWebViewScreen: React.FC = () => {
  const route = useRoute();
  const navigation = useNavigation();
  const dispatch = useAppDispatch();
  const insets = useSafeAreaInsets();
  const webViewRef = useRef<WebView>(null);

  const { checkout_url, payment_method } = (route.params as PaymentWebViewParams) || {};

  const [isLoading, setIsLoading] = useState(true);
  const [hasHandledReturn, setHasHandledReturn] = useState(false);

  const title = payment_method === 'orange_money' ? 'Orange Money' : 'Paiement par carte';

  const handleNavigationStateChange = (navState: { url: string }) => {
    if (hasHandledReturn) return;

    const { url } = navState;

    if (isReturnUrl(url, SUCCESS_PATTERNS)) {
      setHasHandledReturn(true);
      // Rafraîchir le panier (le webhook a mis à jour la commande)
      dispatch(fetchCart());
      Alert.alert('Paiement effectué', 'Votre commande a été enregistrée avec succès !', [
        {
          text: 'Voir mes commandes',
          onPress: () => {
            (navigation as any).navigate('Profile', { screen: 'Orders' });
          },
        },
      ]);
    } else if (isReturnUrl(url, CANCEL_PATTERNS)) {
      setHasHandledReturn(true);
      dispatch(fetchCart());
      Alert.alert('Paiement annulé', 'Le paiement a été annulé. Votre panier a été conservé.', [
        {
          text: 'OK',
          onPress: () => navigation.goBack(),
        },
      ]);
    }
  };

  const handleCancel = () => {
    Alert.alert(
      'Annuler le paiement',
      'Êtes-vous sûr de vouloir annuler le paiement ?',
      [
        { text: 'Continuer le paiement', style: 'cancel' },
        {
          text: 'Annuler',
          style: 'destructive',
          onPress: () => navigation.goBack(),
        },
      ]
    );
  };

  if (!checkout_url) {
    return (
      <View style={[styles.container, { paddingTop: insets.top }]}>
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle-outline" size={48} color={COLORS.TEXT_SECONDARY} />
          <Text style={styles.errorText}>URL de paiement invalide</Text>
          <TouchableOpacity style={styles.retryButton} onPress={() => navigation.goBack()}>
            <Text style={styles.retryButtonText}>Retour</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.closeButton} onPress={handleCancel}>
          <Ionicons name="close" size={24} color={COLORS.TEXT} />
        </TouchableOpacity>
        <View style={styles.headerCenter}>
          <Ionicons
            name={payment_method === 'orange_money' ? 'phone-portrait-outline' : 'card-outline'}
            size={20}
            color={COLORS.PRIMARY}
          />
          <Text style={styles.headerTitle} numberOfLines={1}>{title}</Text>
        </View>
        <View style={styles.headerRight}>
          <Ionicons name="lock-closed" size={16} color={COLORS.PRIMARY} />
        </View>
      </View>

      {isLoading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color={COLORS.PRIMARY} />
          <Text style={styles.loadingText}>Chargement du paiement...</Text>
        </View>
      )}

      <WebView
        ref={webViewRef}
        source={{ uri: checkout_url }}
        style={styles.webView}
        onLoadStart={() => setIsLoading(true)}
        onLoadEnd={() => setIsLoading(false)}
        onNavigationStateChange={handleNavigationStateChange}
        javaScriptEnabled={true}
        domStorageEnabled={true}
        startInLoadingState={false}
        scalesPageToFit={true}
        sharedCookiesEnabled={true}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  closeButton: {
    padding: 4,
  },
  headerCenter: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    justifyContent: 'center',
    gap: 6,
  },
  headerTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.TEXT,
  },
  headerRight: {
    padding: 4,
  },
  webView: {
    flex: 1,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 60,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    zIndex: 10,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 15,
    color: COLORS.TEXT_SECONDARY,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  errorText: {
    marginTop: 12,
    fontSize: 16,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
  },
  retryButton: {
    marginTop: 20,
    backgroundColor: COLORS.PRIMARY,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '600',
  },
});

export default PaymentWebViewScreen;
