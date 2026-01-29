import React, { useEffect, useMemo, useState } from 'react';
import {
  View,
  Text,
  Image,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { COLORS, API_ENDPOINTS } from '../utils/constants';
import { formatPrice } from '../utils/helpers';
import apiClient from '../services/api';
import type { ShippingAddress, CartItem, Product } from '../types';
import * as WebBrowser from 'expo-web-browser';
import { LoadingScreen } from '../components/LoadingScreen';
import { fetchCart } from '../store/slices/cartSlice';

const CheckoutScreen: React.FC = () => {
  const navigation = useNavigation();
  const dispatch = useAppDispatch();
  const { items, itemsCount } = useAppSelector((state) => state.cart);
  const { sessionExpired, isAuthenticated } = useAppSelector((state) => state.auth);
  
  const [addresses, setAddresses] = useState<ShippingAddress[]>([]);
  const [selectedAddress, setSelectedAddress] = useState<ShippingAddress | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<'stripe' | 'orange_money' | 'cash_on_delivery'>('stripe');
  const [selectedDeliveryMethodId, setSelectedDeliveryMethodId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  // Rediriger vers Login si l'utilisateur n'est pas authentifié
  useEffect(() => {
    if (!isAuthenticated && !sessionExpired) {
      Alert.alert(
        'Connexion requise',
        'Vous devez être connecté pour passer une commande. Souhaitez-vous vous connecter ?',
        [
          { text: 'Annuler', style: 'cancel', onPress: () => navigation.goBack() },
          {
            text: 'Se connecter',
            onPress: () => {
              try {
                (navigation as any).navigate('Profile', { screen: 'Login' });
              } catch {
                navigation.goBack();
              }
            },
          },
        ]
      );
    }
  }, [isAuthenticated, sessionExpired, navigation]);

  useEffect(() => {
    if (isAuthenticated && !sessionExpired) {
      loadAddresses();
    }
  }, [isAuthenticated, sessionExpired]);

  useEffect(() => {
    if (sessionExpired) {
      // La session a expiré (callback global), on redirige vers Login
      try {
        (navigation as any).navigate('Profile', { screen: 'Login' });
      } catch {
        // no-op
      }
    }
  }, [navigation, sessionExpired]);

  const isSessionExpiredError = (error: any): boolean => {
    const status = error?.response?.status;
    const msg = (error?.message || '').toString().toLowerCase();
    return status === 401 || msg.includes('session expirée') || msg.includes('session expiree');
  };

  const isStockInsufficientError = (message: string): boolean => {
    const msg = (message || '').toLowerCase();
    return msg.includes('stock insuffisant');
  };

  const getProductTitle = (product?: Product | null): string => {
    if (!product) return 'Produit';
    return product.title || 'Produit';
  };

  const getVariantInfo = (product?: Product | null): string | null => {
    const specs = product?.specifications;
    if (!specs) return null;

    const parts: string[] = [];
    if (specs.color_name || specs.color) {
      parts.push(specs.color_name || specs.color);
    }
    if (specs.storage) {
      parts.push(`${specs.storage}Go`);
    }
    if (specs.ram) {
      parts.push(`${specs.ram}Go RAM`);
    }

    return parts.length > 0 ? parts.join(' • ') : null;
  };

  // Vérifier si un produit est vendu au poids
  const isWeightedProduct = (product: Product | null | undefined): boolean => {
    if (!product) return false;
    const specs = product.specifications || {};
    const soldByWeight = specs.sold_by_weight;
    const isSoldByWeight = soldByWeight === true || (
      typeof soldByWeight === 'string' && ['true', '1', 'yes'].includes(soldByWeight.toLowerCase())
    );
    const unitRaw = specs.weight_unit || specs.unit_display || specs.unit_type;
    const unit = unitRaw ? String(unitRaw).toLowerCase() : '';
    const hasWeightFields = specs.available_weight_kg !== undefined ||
      specs.available_weight_g !== undefined ||
      specs.price_per_kg !== undefined ||
      specs.price_per_g !== undefined ||
      specs.discount_price_per_kg !== undefined ||
      specs.discount_price_per_g !== undefined;
    return isSoldByWeight ||
      ['weight', 'kg', 'kilogram', 'g', 'gram', 'gramme'].includes(unit) ||
      hasWeightFields;
  };

  const getWeightUnit = (product: Product | null | undefined): 'kg' | 'g' => {
    const specs = product?.specifications || {};
    const unitRaw = specs.weight_unit || specs.unit_display || specs.unit_type;
    if (!unitRaw) {
      return (specs.available_weight_g !== undefined || specs.price_per_g !== undefined || specs.discount_price_per_g !== undefined) ? 'g' : 'kg';
    }
    const unit = String(unitRaw).toLowerCase();
    if (['g', 'gram', 'gramme'].includes(unit)) return 'g';
    return 'kg';
  };

  const formatWeightQuantity = (quantity: number, unit: 'kg' | 'g'): string => {
    if (unit === 'g') {
      return Number.isFinite(quantity) ? String(Math.round(quantity)) : '0';
    }
    if (quantity % 1 === 0) return quantity.toString();
    return quantity.toFixed(3).replace(/\.?0+$/, '');
  };

  // Obtenir le prix unitaire (au kg/g pour les produits au poids, unitaire pour les autres)
  const getUnitPrice = (item: CartItem): number => {
    const product = item.product;
    if (isWeightedProduct(product)) {
      const specs = product.specifications || {};
      const unit = getWeightUnit(product);
      if (unit === 'g') {
        const discountPricePerG = specs.discount_price_per_g;
        if (discountPricePerG && discountPricePerG > 0) {
          if (__DEV__) {
            console.log('[CheckoutScreen] ⚖️ Prix unitaire (promo au g):', {
              productId: product.id,
              productTitle: product.title,
              discountPricePerG,
              quantity: item.quantity,
            });
          }
          return discountPricePerG;
        }
        const pricePerG = specs.price_per_g;
        if (pricePerG) {
          if (__DEV__) {
            console.log('[CheckoutScreen] ⚖️ Prix unitaire (normal au g):', {
              productId: product.id,
              productTitle: product.title,
              pricePerG,
              quantity: item.quantity,
            });
          }
          return pricePerG;
        }
      }
      // Vérifier d'abord s'il y a un prix promotionnel au kg
      const discountPricePerKg = specs.discount_price_per_kg;
      if (discountPricePerKg && discountPricePerKg > 0) {
        if (__DEV__) {
          console.log('[CheckoutScreen] ⚖️ Prix unitaire (promo au kg):', {
            productId: product.id,
            productTitle: product.title,
            discountPricePerKg,
            quantity: item.quantity,
          });
        }
        return discountPricePerKg;
      }
      // Sinon, utiliser le prix normal au kg
      const pricePerKg = specs.price_per_kg;
      if (pricePerKg) {
        if (__DEV__) {
          console.log('[CheckoutScreen] ⚖️ Prix unitaire (normal au kg):', {
            productId: product.id,
            productTitle: product.title,
            pricePerKg,
            quantity: item.quantity,
          });
        }
        return pricePerKg;
      }
      // Fallback sur le prix du produit si price_per_kg/g n'est pas défini
      if (__DEV__) {
        console.log('[CheckoutScreen] ⚖️ Prix unitaire (fallback):', {
          productId: product.id,
          productTitle: product.title,
          fallbackPrice: product.discount_price || product.price || 0,
          quantity: item.quantity,
        });
      }
      return product.discount_price || product.price || 0;
    }
    // Pour les produits normaux, utiliser discount_price ou price
    return product.discount_price || product.price || 0;
  };

  const cartItemsSafe = useMemo(
    () => (Array.isArray(items) ? items.filter((it) => it && it.product && it.id) : []),
    [items]
  );

  const normalizeDeliveryMethods = (methods: any[]): any[] => {
    if (!Array.isArray(methods)) return [];
    return methods
      .filter((method) => method && method.id !== undefined && method.id !== null)
      .map((method) => {
        const id = Number(method.id);
        const order = method.order !== undefined && method.order !== null ? Number(method.order) : undefined;
        return {
          ...method,
          id,
          order: Number.isNaN(order) ? undefined : order,
        };
      })
      .filter((method) => !Number.isNaN(method.id))
      .sort((a, b) => {
        const orderA = a.order ?? Number.POSITIVE_INFINITY;
        const orderB = b.order ?? Number.POSITIVE_INFINITY;
        if (orderA !== orderB) return orderA - orderB;
        return a.id - b.id;
      });
  };

  const deliveryMethodsInfo = useMemo(() => {
    const lists = cartItemsSafe
      .map((item) => normalizeDeliveryMethods(item.product?.delivery_methods || []))
      .filter((list) => list.length > 0);

    if (lists.length === 0) {
      return { common: [] as Product['delivery_methods'], all: [] as Product['delivery_methods'], isIntersection: false };
    }

    const allMethodsMap = new Map<string, any>();
    lists.flat().forEach((method: any) => {
      if (!method || method.id === undefined || method.id === null) return;
      const id = Number(method.id);
      if (Number.isNaN(id)) return;
      const siteId = method.site_configuration ?? 'default';
      const key = `${siteId}:${id}`;
      if (!allMethodsMap.has(key)) {
        allMethodsMap.set(key, method);
      }
    });

    const intersectionKeys = lists.reduce((acc, list) => {
      const keys = new Set(
        list
          .map((m: any) => {
            const id = Number(m?.id);
            if (Number.isNaN(id)) return null;
            const siteId = m?.site_configuration ?? 'default';
            return `${siteId}:${id}`;
          })
          .filter(Boolean) as string[]
      );
      if (acc === null) return keys;
      return new Set([...acc].filter((key) => keys.has(key)));
    }, null as Set<string> | null);

    const commonMethods = intersectionKeys
      ? Array.from(intersectionKeys)
          .map((key) => allMethodsMap.get(key))
          .filter(Boolean)
      : [];

    return {
      common: commonMethods,
      all: Array.from(allMethodsMap.values()),
      isIntersection: commonMethods.length > 0,
    };
  }, [cartItemsSafe]);

  const getDeliveryPrice = (method: any): number => {
    if (!method) return 0;
    if (method.effective_price !== undefined && method.effective_price !== null) {
      return Number(method.effective_price) || 0;
    }
    if (method.override_price !== undefined) {
      return method.override_price !== null ? Number(method.override_price) || 0 : 0;
    }
    if (method.base_price !== undefined && method.base_price !== null) {
      return Number(method.base_price) || 0;
    }
    return 0;
  };

  const selectedDeliveryMethod = useMemo(() => {
    if (!deliveryMethodsInfo.common || deliveryMethodsInfo.common.length === 0) {
      return null;
    }
    return deliveryMethodsInfo.common.find((m: any) => Number(m?.id) === selectedDeliveryMethodId) || null;
  }, [deliveryMethodsInfo.common, selectedDeliveryMethodId]);

  const calculatedItemsTotal = useMemo(() => (
    cartItemsSafe.reduce((sum, item) => sum + (getUnitPrice(item) * item.quantity), 0)
  ), [cartItemsSafe]);

  const deliveryGroups = useMemo(() => {
    const groups = new Map<string, { method: any | null; items: CartItem[]; shipping_cost: number; siteId: any }>();

    cartItemsSafe.forEach((item) => {
      const methods = normalizeDeliveryMethods(item.product?.delivery_methods || []);
      let selected = null;

      if (deliveryMethodsInfo.isIntersection && selectedDeliveryMethodId !== null) {
        selected = methods.find((m: any) => Number(m?.id) === selectedDeliveryMethodId) || null;
      }
      if (!selected) {
        selected = methods.length > 0 ? methods[0] : null;
      }

      const siteId = selected?.site_configuration ?? 'default';
      const methodId = selected?.id ?? 'unknown';
      const key = `${siteId}:${methodId}`;

      if (!groups.has(key)) {
        groups.set(key, {
          method: selected,
          items: [],
          shipping_cost: selected ? getDeliveryPrice(selected) : 0,
          siteId,
        });
      }

      const group = groups.get(key);
      if (group) {
        group.items.push(item);
      }
    });

    return Array.from(groups.values());
  }, [cartItemsSafe, deliveryMethodsInfo.isIntersection, selectedDeliveryMethodId]);

  const estimatedShippingCost = deliveryGroups.reduce((sum, group) => sum + (group.shipping_cost || 0), 0);
  const estimatedTotal = calculatedItemsTotal + estimatedShippingCost;

  useEffect(() => {
    if (!deliveryMethodsInfo.isIntersection || !deliveryMethodsInfo.common || deliveryMethodsInfo.common.length === 0) {
      if (selectedDeliveryMethodId !== null) {
        setSelectedDeliveryMethodId(null);
      }
      return;
    }
    const exists = deliveryMethodsInfo.common.some((m: any) => Number(m?.id) === selectedDeliveryMethodId);
    if (!exists) {
      setSelectedDeliveryMethodId(Number(deliveryMethodsInfo.common[0]?.id));
    }
  }, [deliveryMethodsInfo.common, deliveryMethodsInfo.isIntersection, selectedDeliveryMethodId]);

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
        return;
      }
      // Si session expirée, le callback global déclenche déjà l'UX (et on redirige via useEffect)
      if (isSessionExpiredError(error)) {
        return;
      }
      console.error('[CheckoutScreen] Error loading addresses:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePlaceOrder = async () => {
    console.log('[CheckoutScreen] 🧾 Finalisation: début', {
      isAuthenticated,
      sessionExpired,
      paymentMethod,
      selectedAddressId: selectedAddress?.id,
      selectedDeliveryMethodId,
      deliveryGroupsCount: deliveryGroups.length,
      itemsCount: cartItemsSafe.length,
    });
    // Vérifier l'authentification avant de procéder
    if (!isAuthenticated) {
      Alert.alert(
        'Connexion requise',
        'Vous devez être connecté pour passer une commande. Souhaitez-vous vous connecter ?',
        [
          { text: 'Annuler', style: 'cancel' },
          {
            text: 'Se connecter',
            onPress: () => {
              try {
                (navigation as any).navigate('Profile', { screen: 'Login' });
              } catch {
                // no-op
              }
            },
          },
        ]
      );
      return;
    }

    if (!selectedAddress) {
      Alert.alert('Erreur', 'Veuillez sélectionner une adresse de livraison');
      return;
    }

    try {
      setIsProcessing(true);

      // Re-synchroniser le panier avant de passer la commande
      const refreshedCart = await dispatch(fetchCart()).unwrap();
      const refreshedItems = refreshedCart?.items || [];
      console.log('[CheckoutScreen] 🛒 Panier re-synchronisé', {
        refreshedItemsCount: refreshedItems.length,
      });
      if (!refreshedItems.length) {
        Alert.alert('Panier vide', 'Votre panier est vide. Veuillez ajouter des articles avant de commander.', [
          { text: 'OK', onPress: () => navigation.goBack() },
        ]);
        return;
      }

      const shippingMethodId = deliveryMethodsInfo.isIntersection && selectedDeliveryMethod
        ? selectedDeliveryMethod.id
        : undefined;
      const payload = {
        payment_method: paymentMethod,
        shipping_address_id: selectedAddress.id,
        product_type: 'all',
        shipping_method_id: shippingMethodId,
      };
      console.log('[CheckoutScreen] 📦 Payload checkout', {
        paymentMethod,
        shippingAddressId: selectedAddress.id,
        shippingMethodId,
        deliveryIntersection: deliveryMethodsInfo.isIntersection,
      });

      const response = await apiClient.post(`${API_ENDPOINTS.CART}checkout/`, {
        ...payload,
      });

      const data = response.data || {};
      const orders = Array.isArray(data.orders) ? data.orders : [];
      const warnings = Array.isArray(data.warnings) ? data.warnings : [];
      console.log('[CheckoutScreen] ✅ Réponse checkout', {
        hasOrdersArray: Array.isArray(data.orders),
        ordersCount: orders.length,
        warningsCount: warnings.length,
        paymentMethod: data.payment_method,
        status: data.status,
        checkoutUrl: !!data.checkout_url,
      });

      if (warnings.length > 0) {
        Alert.alert('Info livraison', warnings.join('\n'));
      }

      if (orders.length > 0) {
        const cashOnly = orders.every((order: any) => order.payment_method === 'cash_on_delivery' || order.status === 'confirmed');
        if (cashOnly) {
          await dispatch(fetchCart());
          Alert.alert('Succès', 'Votre commande a été enregistrée avec succès !', [
            {
              text: 'OK',
              onPress: () => {
                (navigation as any).navigate('Profile', { screen: 'Orders' });
              }
            }
          ]);
          return;
        }

        const checkoutUrls = orders
          .map((order: any) => order.checkout_url)
          .filter((url: string | undefined) => !!url);

        for (const url of checkoutUrls) {
          console.log('[CheckoutScreen] Ouverture du WebBrowser (multiple commandes):', url);
          const result = await WebBrowser.openBrowserAsync(url, {
            presentationStyle: WebBrowser.WebBrowserPresentationStyle.FULL_SCREEN,
            controlsColor: COLORS.PRIMARY,
          });
          
          console.log('[CheckoutScreen] WebBrowser retour - result.type:', result.type);
          
          // Fermer explicitement le WebBrowser s'il est encore ouvert (cas result.type === 'opened')
          try {
            await WebBrowser.dismissBrowser();
            console.log('[CheckoutScreen] WebBrowser.dismissBrowser() appelé (multiple)');
          } catch (e) {
            console.log('[CheckoutScreen] dismissBrowser (déjà fermé):', (e as Error).message);
          }
        }

        // Rafraîchir le panier et naviguer après paiement
        await dispatch(fetchCart());
        (navigation as any).navigate('Profile', { screen: 'Orders' });
        return;
      }

      const { checkout_url, payment_method, status } = data;

      if (payment_method === 'cash_on_delivery' || status === 'confirmed') {
        await dispatch(fetchCart());
        Alert.alert('Succès', 'Votre commande a été enregistrée avec succès !', [
          { 
            text: 'OK', 
            onPress: () => {
              (navigation as any).navigate('Profile', { screen: 'Orders' });
            } 
          }
        ]);
        return;
      }

      if (checkout_url) {
        console.log('[CheckoutScreen] Ouverture du WebBrowser pour paiement:', checkout_url);
        const result = await WebBrowser.openBrowserAsync(checkout_url, {
          presentationStyle: WebBrowser.WebBrowserPresentationStyle.FULL_SCREEN,
          controlsColor: COLORS.PRIMARY,
        });
        
        console.log('[CheckoutScreen] ========== WebBrowser retour ==========');
        console.log('[CheckoutScreen] result.type:', result.type, '(dismiss = fermé par l\'utilisateur, opened = ouvert / résolu sans fermeture)');
        
        // Fermer explicitement le WebBrowser s'il est encore ouvert (cas result.type === 'opened')
        try {
          await WebBrowser.dismissBrowser();
          console.log('[CheckoutScreen] WebBrowser.dismissBrowser() appelé - navigateur fermé');
        } catch (e) {
          console.log('[CheckoutScreen] dismissBrowser (déjà fermé ou non ouvert):', (e as Error).message);
        }

        // Petit délai pour laisser au serveur le temps de vider le panier
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Rafraîchir le panier et naviguer vers les commandes
        console.log('[CheckoutScreen] Rafraîchissement du panier et navigation...');
        await dispatch(fetchCart());
        (navigation as any).navigate('Profile', { screen: 'Orders' });
      }
    } catch (error: any) {
      const status = error?.response?.status;
      const responseData = error?.response?.data;
      const msg = responseData?.error || responseData?.detail || 'Une erreur est survenue lors de la commande';
      console.log('[CheckoutScreen] ❌ Erreur checkout', {
        status,
        message: error?.message,
        responseData,
      });
      if (isStockInsufficientError(msg)) {
        // Re-synchroniser le panier et revenir à l'écran panier
        dispatch(fetchCart());
        Alert.alert('Stock insuffisant', msg, [
          {
            text: 'Voir le panier',
            onPress: () => navigation.goBack(),
          },
          { text: 'OK' },
        ]);
      } else {
        Alert.alert('Erreur', msg);
      }
    } finally {
      setIsProcessing(false);
    }
  };

  // Afficher un écran de chargement ou rediriger si non authentifié
  if (!isAuthenticated) {
    return <LoadingScreen />;
  }

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
            {(deliveryGroups.length > 0 ? deliveryGroups : [{ items: cartItemsSafe, method: null, siteId: 'default', shipping_cost: 0 }])
              .map((group, groupIndex) => {
                const siteLabel = group.siteId && group.siteId !== 'default'
                  ? `Site ${group.siteId}`
                  : 'Site principal';
                const methodName = group.method?.name || 'Livraison';
                const groupCost = group.shipping_cost || 0;
                return (
                  <View key={`${group.siteId}-${group.method?.id ?? 'unknown'}-${groupIndex}`} style={styles.summaryGroup}>
                    <View style={styles.summaryGroupHeader}>
                      <View>
                        <Text style={styles.summaryGroupTitle}>{methodName}</Text>
                        <Text style={styles.summaryGroupSubtitle}>{siteLabel}</Text>
                      </View>
                      <Text style={styles.summaryGroupCost}>
                        {groupCost > 0 ? formatPrice(groupCost) : 'Gratuit'}
                      </Text>
                    </View>
                    <View style={styles.summaryGroupItems}>
                      {group.items.map((item: CartItem) => {
                        const product = item.product;
                        const unitPrice = getUnitPrice(item);
                        const variantInfo = getVariantInfo(product);
                        const isWeighted = isWeightedProduct(product);
                        const weightUnit = isWeighted ? getWeightUnit(product) : 'kg';
                        const imageUrl = product?.image || product?.image_urls?.main;
                        return (
                          <View key={item.id} style={styles.itemRow}>
                            {imageUrl ? (
                              <Image
                                source={{ uri: imageUrl }}
                                style={styles.itemImage}
                                resizeMode="cover"
                              />
                            ) : (
                              <View style={styles.itemImagePlaceholder}>
                                <Ionicons name="image-outline" size={20} color={COLORS.TEXT_SECONDARY} />
                              </View>
                            )}
                            <View style={styles.itemInfo}>
                              <Text style={styles.itemName} numberOfLines={1}>
                                {getProductTitle(product)}
                              </Text>
                              {variantInfo ? <Text style={styles.itemVariant}>{variantInfo}</Text> : null}
                              <Text style={styles.itemQuantity}>
                                {isWeighted ? 'Poids' : 'Quantité'}: {isWeighted ? `${formatWeightQuantity(item.quantity, weightUnit)} ${weightUnit}` : item.quantity} × {formatPrice(unitPrice)} / {isWeighted ? weightUnit : 'unité'}
                              </Text>
                            </View>
                            <Text style={styles.itemSubtotal}>
                              {formatPrice(unitPrice * item.quantity)}
                            </Text>
                          </View>
                        );
                      })}
                    </View>
                  </View>
                );
              })}
            <View style={styles.summaryDivider} />
            <View style={styles.summaryFooter}>
              <Text style={styles.summaryText}>{itemsCount} article(s)</Text>
              <Text style={styles.summaryTotal}>
                {formatPrice(calculatedItemsTotal)}
              </Text>
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
          <Text style={styles.totalLabel}>Sous-total:</Text>
          <Text style={styles.totalValue}>{formatPrice(calculatedItemsTotal)}</Text>
        </View>
        <View style={styles.totalRow}>
          <Text style={styles.totalLabel}>Livraison:</Text>
          <Text style={styles.totalValue}>{formatPrice(estimatedShippingCost)}</Text>
        </View>
        <View style={styles.totalRow}>
          <Text style={styles.totalLabel}>Total estimé:</Text>
          <Text style={styles.totalValue}>{formatPrice(estimatedTotal)}</Text>
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
    padding: 16,
    paddingTop: 45, // Réduit de 60
    flexDirection: 'row',
    alignItems: 'center',
  },
  backButton: {
    marginRight: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  content: {
    padding: 12, // Réduit de 16
  },
  section: {
    marginBottom: 16, // Réduit de 24
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.TEXT,
    marginBottom: 8,
  },
  editLink: {
    color: COLORS.PRIMARY,
    fontWeight: '600',
    fontSize: 13,
  },
  summaryCard: {
    backgroundColor: '#F9FAFB',
    borderRadius: 10,
    padding: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  summaryGroup: {
    marginBottom: 6,
  },
  summaryGroupHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 3,
    paddingHorizontal: 6,
    borderRadius: 5,
    backgroundColor: '#ECFDF3',
    borderWidth: 1,
    borderColor: '#D1FAE5',
    marginBottom: 4,
  },
  summaryGroupTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: COLORS.TEXT,
  },
  summaryGroupSubtitle: {
    fontSize: 10,
    color: COLORS.TEXT_SECONDARY,
  },
  summaryGroupCost: {
    fontSize: 11,
    fontWeight: '700',
    color: COLORS.PRIMARY,
  },
  summaryGroupItems: {
    gap: 4,
  },
  itemRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 2,
  },
  itemImage: {
    width: 30, // Encore plus petit (était 36)
    height: 30,
    borderRadius: 4,
    marginRight: 6,
    backgroundColor: '#F3F4F6',
  },
  itemImagePlaceholder: {
    width: 30,
    height: 30,
    borderRadius: 4,
    marginRight: 6,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  itemInfo: {
    flex: 1,
    marginRight: 6,
  },
  itemName: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 0,
  },
  itemVariant: {
    fontSize: 10,
    color: COLORS.TEXT_SECONDARY,
  },
  itemQuantity: {
    fontSize: 10,
    color: COLORS.TEXT_SECONDARY,
  },
  itemSubtotal: {
    fontSize: 12,
    fontWeight: '700',
    color: COLORS.TEXT,
  },
  summaryDivider: {
    height: 1,
    backgroundColor: '#E5E7EB',
    marginVertical: 6,
  },
  summaryFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  summaryText: {
    fontSize: 13,
    color: COLORS.TEXT_SECONDARY,
  },
  summaryTotal: {
    fontSize: 15,
    fontWeight: 'bold',
    color: COLORS.TEXT,
  },
  deliveryNotice: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    borderRadius: 10,
    padding: 10,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  deliveryNoticeText: {
    marginLeft: 8,
    color: COLORS.TEXT_SECONDARY,
    fontSize: 13,
  },
  deliveryCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  deliveryCardSelected: {
    borderColor: COLORS.PRIMARY,
    backgroundColor: '#F0FDF4',
  },
  deliveryInfo: {
    flex: 1,
    marginLeft: 12,
  },
  deliveryTitle: {
    fontSize: 16,
    color: COLORS.TEXT,
    fontWeight: '600',
    marginBottom: 4,
  },
  deliveryTitleSelected: {
    color: COLORS.PRIMARY,
  },
  deliverySubtitle: {
    fontSize: 13,
    color: COLORS.TEXT_SECONDARY,
  },
  deliveryEmpty: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    borderRadius: 10,
    padding: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  deliveryEmptyText: {
    marginLeft: 8,
    color: COLORS.TEXT_SECONDARY,
    fontSize: 13,
  },
  addressCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 12, // Réduit de 16
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  addressName: {
    fontSize: 14, // Réduit de 16
    fontWeight: 'bold',
    color: COLORS.TEXT,
    marginBottom: 2,
  },
  addressText: {
    fontSize: 13, // Réduit de 14
    color: COLORS.TEXT_SECONDARY,
    marginBottom: 1,
  },
  addAddressButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12, // Réduit de 16
    borderWidth: 1,
    borderStyle: 'dashed',
    borderColor: COLORS.PRIMARY,
    borderRadius: 10,
    backgroundColor: '#F0FDF4',
  },
  addAddressText: {
    marginLeft: 8,
    color: COLORS.PRIMARY,
    fontWeight: '600',
    fontSize: 14,
  },
  paymentCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 12, // Réduit de 16
    marginBottom: 8, // Réduit de 12
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  paymentCardSelected: {
    borderColor: COLORS.PRIMARY,
    backgroundColor: '#F0FDF4',
  },
  paymentText: {
    flex: 1,
    marginLeft: 10,
    fontSize: 14, // Réduit de 16
    color: COLORS.TEXT,
  },
  paymentTextSelected: {
    fontWeight: 'bold',
    color: COLORS.PRIMARY,
  },
  footer: {
    backgroundColor: '#FFFFFF',
    padding: 10,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    paddingBottom: 20,
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  totalLabel: {
    fontSize: 13,
    color: COLORS.TEXT_SECONDARY,
  },
  totalValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.PRIMARY,
  },
  confirmButton: {
    backgroundColor: COLORS.PRIMARY,
    borderRadius: 8,
    padding: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  confirmButtonDisabled: {
    opacity: 0.6,
  },
  confirmButtonText: {
    color: '#FFFFFF',
    fontSize: 15,
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

