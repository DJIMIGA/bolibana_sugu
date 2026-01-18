import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
  RefreshControl,
  ActivityIndicator,
  Alert,
  ScrollView,
} from 'react-native';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchCart, updateCartItem, removeFromCart, clearCart, optimisticUpdateQuantity, enrichCartProducts } from '../store/slices/cartSlice';
import { fetchCategories } from '../store/slices/productSlice';
import { useNavigation } from '@react-navigation/native';
import { formatPrice, isWeightedProduct as isWeightedProductHelper, formatWeightQuantity } from '../utils/helpers';
import { COLORS } from '../utils/constants';
import { CartItem } from '../types';
import { Header } from '../components/Header';
import { LoadingScreen } from '../components/LoadingScreen';

const CartScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigation = useNavigation();
  const { cart, items, total, itemsCount, isLoading } = useAppSelector((state) => state.cart);
  const { categories, searchQuery } = useAppSelector((state) => state.product);
  const { isAuthenticated } = useAppSelector((state) => state.auth);
  const [refreshing, setRefreshing] = useState(false);


  useEffect(() => {
    const loadCart = async () => {
      await dispatch(fetchCart());
      // Enrichir les produits avec leurs spécifications (nécessaire pour les produits au poids)
      dispatch(enrichCartProducts());
    };
    loadCart();
    dispatch(fetchCategories({ forceRefresh: true }));
  }, [dispatch]);

  useEffect(() => {
    if (!__DEV__) return;
    const unitInfo = (items || []).map((item) => {
      const specs = item?.product?.specifications || {};
      const unitType = specs.unit_type || specs.unit || null;
      const soldByWeight = specs.sold_by_weight;
      const isWeighted = soldByWeight === true ||
        (typeof soldByWeight === 'string' && ['true', '1', 'yes'].includes(soldByWeight.toLowerCase())) ||
        (typeof unitType === 'string' && ['weight', 'kg', 'kilogram', 'g', 'gram', 'grams'].includes(unitType.toLowerCase()));
      return {
        itemId: item?.id,
        productId: item?.product?.id,
        productTitle: item?.product?.title,
        quantity: item?.quantity,
        unitType,
        sold_by_weight: soldByWeight,
        isWeighted,
      };
    });
    console.log('[CartScreen] 🛒 Panier - unités et quantités:', unitInfo);
  }, [items]);

  useEffect(() => {
    const hasMissingSpecs = (items || []).some(
      (item) => !item.product?.specifications || Object.keys(item.product.specifications).length === 0
    );
    if (hasMissingSpecs) {
      dispatch(enrichCartProducts());
    }
  }, [dispatch, items]);

  const onRefresh = async () => {
    setRefreshing(true);
    await dispatch(fetchCart());
    await dispatch(enrichCartProducts());
    setRefreshing(false);
  };

  // Vérifier si un item est vendu au poids
  const isWeightedItem = (item: CartItem): boolean => {
    if (!item) return false;
    if (item.is_weighted === true) return true;
    const unit = item.weight_unit ? String(item.weight_unit).toLowerCase() : '';
    if (['weight', 'kg', 'kilogram', 'g', 'gram', 'gramme'].includes(unit)) return true;
    return isWeightedProductHelper(item.product);
  };

  const getWeightUnit = (item: CartItem): string => {
    const unitRaw = item.weight_unit
      || item.product?.specifications?.weight_unit
      || item.product?.specifications?.unit_display
      || item.product?.specifications?.unit_type;
    if (!unitRaw) return 'kg';
    const unit = String(unitRaw).toLowerCase();
    if (['weight', 'kg', 'kilogram'].includes(unit)) return 'kg';
    if (['g', 'gram', 'gramme'].includes(unit)) return 'g';
    return unit;
  };

  const getAvailableWeightForItem = (item: CartItem): number => {
    const specs = item.product?.specifications || {};
    const unit = getWeightUnit(item);
    if (unit === 'g') {
      const availableG = specs.available_weight_g;
      if (availableG !== undefined && availableG !== null) return Number(availableG) || 0;
    }
    return Number(specs.available_weight_kg) || 0;
  };

  // Fonction helper pour formater la quantité (évite d'arrondir 0.999 à 1.0)
  const formatQuantity = (qty: number): string => {
    return formatWeightQuantity(qty);
  };

  // Fonction helper pour formater le poids disponible
  const formatAvailableWeight = (weight: number): string => {
    if (weight === undefined || weight === null) return '0';
    // Formater avec 3 décimales et retirer les zéros finaux
    const formatted = weight.toFixed(3).replace(/\.?0+$/, '');
    return formatted;
  };

  const handleUpdateQuantity = async (itemId: number, newQuantity: number) => {
    if (newQuantity <= 0) {
      handleRemoveItem(itemId);
      return;
    }
    
    const item = items.find(i => i.id === itemId);
    if (!item) return;

    const isWeighted = isWeightedItem(item);
    const specs = item.product.specifications || {};

    // Vérifier les limites de stock
    if (!item.product.is_salam) {
      if (isWeighted) {
        // Pour les produits au poids, vérifier le poids disponible
        const weightUnit = getWeightUnit(item);
        const availableWeight = getAvailableWeightForItem(item);
        if (availableWeight > 0 && newQuantity > availableWeight) {
          Alert.alert(
            'Stock insuffisant',
            `Poids disponible: ${formatAvailableWeight(availableWeight)} ${weightUnit}. Veuillez réduire la quantité.`
          );
          return;
        }
        // Vérifier le minimum (0.5 kg)
        if (newQuantity < 0.5) {
          Alert.alert('Quantité minimale', `La quantité minimale est de 0.5 ${weightUnit}`);
          return;
        }
      } else {
        // Pour les produits normaux, vérifier le stock en unités
        if (item.product.stock !== undefined && item.product.stock > 0 && newQuantity > item.product.stock) {
          Alert.alert('Stock insuffisant', `Stock disponible: ${item.product.stock}`);
          return;
        }
      }
    }
    
    // 1. Mise à jour visuelle instantanée
    dispatch(optimisticUpdateQuantity({ itemId, quantity: newQuantity }));
    
    // 2. Mise à jour serveur avec gestion d'erreur
    try {
      await dispatch(updateCartItem({ itemId, quantity: newQuantity })).unwrap();
    } catch (error: any) {
      // Si l'article n'existe plus, recharger le panier
      if (error?.response?.status === 404 || error?.message?.includes('introuvable') || error?.message?.includes('Pas trouvé')) {
        if (__DEV__) {
          console.warn('[CartScreen] ⚠️ Article introuvable, rechargement du panier:', itemId);
        }
        // Recharger le panier pour synchroniser avec le serveur
        dispatch(fetchCart());
        Alert.alert('Erreur', 'L\'article a été modifié. Le panier a été mis à jour.');
      } else {
        // Autre erreur, restaurer la quantité précédente
        const previousItem = items.find(i => i.id === itemId);
        if (previousItem) {
          dispatch(optimisticUpdateQuantity({ itemId, quantity: previousItem.quantity }));
        }
        Alert.alert('Erreur', error?.message || 'Impossible de mettre à jour la quantité');
      }
    }
  };

  // Gérer l'incrément pour les produits au poids
  const handleUpdateWeight = (itemId: number, increment: number) => {
    const item = items.find(i => i.id === itemId);
    if (!item) return;
    
    const currentWeight = typeof item.quantity === 'number'
      ? item.quantity
      : parseFloat(String(item.quantity)) || 0;
    const specs = item.product.specifications || {};
    const weightUnit = getWeightUnit(item);
    const availableWeight = getAvailableWeightForItem(item);
    
    // Calculer le nouveau poids
    let newWeight = currentWeight + increment;
    
    // Normaliser au pas de 0.5 kg pour éviter les accumulations flottantes
    newWeight = Math.round(newWeight * 2) / 2;
    
    // Appliquer le minimum de 0.5 kg
    if (newWeight < 0.5) {
      newWeight = 0.5;
    }
    
    // Si on augmente et qu'il y a un poids disponible, vérifier qu'il reste assez
    if (increment > 0 && availableWeight !== undefined && availableWeight > 0) {
      // Vérifier qu'on peut ajouter au moins 0.5 kg
      if ((currentWeight + 0.5) > availableWeight) {
        // Pas assez de poids disponible pour ajouter 0.5 kg
        Alert.alert(
          'Stock insuffisant',
          `Poids disponible: ${formatAvailableWeight(availableWeight)} ${weightUnit}. Impossible d'ajouter 0.5 ${weightUnit}.`
        );
        return;
      }
      // Clamper au maximum disponible
      newWeight = Math.min(newWeight, availableWeight);
    }
    
    handleUpdateQuantity(itemId, newWeight);
  };

  const handleRemoveItem = async (itemId: number) => {
    Alert.alert(
      'Supprimer',
      'Êtes-vous sûr de vouloir supprimer cet article ?',
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Supprimer',
          style: 'destructive',
          onPress: async () => {
            try {
              await dispatch(removeFromCart(itemId)).unwrap();
            } catch (error: any) {
              Alert.alert('Erreur', error || 'Impossible de supprimer l\'article');
            }
          },
        },
      ]
    );
  };

  const handleClearCart = () => {
    Alert.alert(
      'Vider le panier',
      'Êtes-vous sûr de vouloir vider tout le panier ?',
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Vider',
          style: 'destructive',
          onPress: async () => {
            try {
              await dispatch(clearCart()).unwrap();
            } catch (error: any) {
              Alert.alert('Erreur', error || 'Impossible de vider le panier');
            }
          },
        },
      ]
    );
  };

  const handleCheckout = () => {
    if (items.length === 0) {
      Alert.alert('Panier vide', 'Votre panier est vide');
      return;
    }
    
    // Vérifier l'authentification avant de naviguer vers le checkout
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
    
    // Navigation vers l'écran de checkout
    navigation.navigate('Checkout' as never);
  };


  const getVariantInfo = (item: CartItem): string | null => {
    const specs = item.product.specifications;
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

  const getUnitPrice = (item: CartItem): number => {
    if (item.unit_price !== undefined && item.unit_price !== null && item.unit_price > 0) {
      return item.unit_price;
    }
    // Pour les produits au poids, utiliser le prix au kg/g depuis les spécifications
    if (isWeightedItem(item)) {
      const specs = item.product.specifications || {};
      const weightUnit = getWeightUnit(item);
      if (weightUnit === 'g') {
        const discountPricePerG = specs.discount_price_per_g;
        if (discountPricePerG && discountPricePerG > 0) {
          return discountPricePerG;
        }
        const pricePerG = specs.price_per_g;
        if (pricePerG) {
          return pricePerG;
        }
      } else {
        // Vérifier d'abord s'il y a un prix promotionnel au kg
        const discountPricePerKg = specs.discount_price_per_kg;
        if (discountPricePerKg && discountPricePerKg > 0) {
          return discountPricePerKg;
        }
        // Sinon, utiliser le prix normal au kg
        const pricePerKg = specs.price_per_kg;
        if (pricePerKg) {
          return pricePerKg;
        }
      }
      // Fallback sur le prix du produit si price_per_kg/g n'est pas défini
      return item.product.discount_price || item.product.price;
    }
    // Pour les produits normaux, utiliser discount_price ou price
    return item.product.discount_price || item.product.price;
  };

  const getTotalItemPrice = (item: CartItem): number => {
    const unitPrice = getUnitPrice(item);
    return unitPrice * item.quantity;
  };

  const renderItem = ({ item }: { item: CartItem }) => {
    // Vérification de sécurité
    if (!item || !item.product) {
      return null;
    }

    const isWeighted = isWeightedItem(item);
    const unitPrice = getUnitPrice(item);
    const totalItemPrice = getTotalItemPrice(item);
    const variantInfo = getVariantInfo(item);
    const weightUnit = getWeightUnit(item);
    
    // Déterminer s'il y a une réduction (pour les produits au poids, vérifier discount_price_per_kg)
    const hasDiscount = isWeighted
      ? (item.product.specifications?.discount_price_per_kg && 
         item.product.specifications.discount_price_per_kg < (item.product.specifications?.price_per_kg || item.product.price))
      : (item.product.discount_price && item.product.discount_price < item.product.price);

    return (
      <View style={styles.itemContainer}>
        <Image
          source={{ uri: item.product.image || item.product.image_urls?.main }}
          style={styles.itemImage}
          resizeMode="cover"
        />
        <View style={styles.itemInfo}>
          <Text style={styles.itemTitle} numberOfLines={2}>
            {item.product.title}
          </Text>
          
          {/* Informations de variante */}
          {variantInfo && (
            <View style={styles.variantContainer}>
              <Text style={styles.variantText}>{variantInfo}</Text>
            </View>
          )}
          
          {/* Couleurs et tailles */}
          {(item.colors && item.colors.length > 0) || (item.sizes && item.sizes.length > 0) ? (
            <View style={styles.attributesContainer}>
              {item.colors && item.colors.length > 0 && (
                <Text style={styles.attributeText}>
                  Couleur{item.colors.length > 1 ? 's' : ''}: {item.colors.length}
                </Text>
              )}
              {item.sizes && item.sizes.length > 0 && (
                <Text style={styles.attributeText}>
                  Taille{item.sizes.length > 1 ? 's' : ''}: {item.sizes.length}
                </Text>
              )}
            </View>
          ) : null}

          {/* Prix unitaire et total */}
          <View style={styles.priceContainer}>
            {hasDiscount ? (
              <View style={styles.priceRow}>
                <Text style={styles.itemPrice}>
                  {formatPrice(totalItemPrice)}
                </Text>
                <Text style={styles.unitPrice}>
                  {formatPrice(unitPrice)} / {isWeightedItem(item) ? weightUnit : 'unité'}
                </Text>
              </View>
            ) : (
              <View style={styles.priceRow}>
                <Text style={styles.itemPrice}>
                  {formatPrice(totalItemPrice)}
                </Text>
                <Text style={styles.unitPrice}>
                  {formatPrice(unitPrice)} / {isWeightedItem(item) ? weightUnit : 'unité'}
                </Text>
              </View>
            )}
          </View>

          {/* Contrôle de quantité/poids */}
          {isWeightedItem(item) ? (() => {
            const specs = item.product.specifications || {};
            const availableWeight = specs.available_weight_kg;
            const canIncrease = !availableWeight || availableWeight === 0 || (item.quantity + 0.5) <= availableWeight;
            
            return (
              <View style={styles.quantityContainer}>
                <TouchableOpacity
                  style={[styles.quantityButton, item.quantity <= 0.5 && styles.quantityButtonDisabled]}
                  onPress={() => handleUpdateWeight(item.id, -0.5)}
                  disabled={item.quantity <= 0.5}
                  hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                >
                  <Text style={styles.quantityButtonText}>-</Text>
                </TouchableOpacity>
                <Text style={styles.quantityValue}>
                  {formatQuantity(item.quantity)} {weightUnit}
                </Text>
                <TouchableOpacity
                  style={[styles.quantityButton, !canIncrease && styles.quantityButtonDisabled]}
                  onPress={() => handleUpdateWeight(item.id, 0.5)}
                  disabled={!canIncrease}
                  hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                >
                  <Text style={styles.quantityButtonText}>+</Text>
                </TouchableOpacity>
              </View>
            );
          })() : (
            <View style={styles.quantityContainer}>
              <TouchableOpacity
                style={[styles.quantityButton, item.quantity <= 1 && styles.quantityButtonDisabled]}
                onPress={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                disabled={item.quantity <= 1}
                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
              >
                <Text style={styles.quantityButtonText}>-</Text>
              </TouchableOpacity>
              <Text style={styles.quantityValue}>{item.quantity}</Text>
              <TouchableOpacity
                style={[
                  styles.quantityButton,
                  item.product.stock !== undefined && 
                  item.product.stock > 0 && 
                  item.quantity >= item.product.stock && 
                  styles.quantityButtonDisabled
                ]}
                onPress={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                disabled={
                  item.product.stock !== undefined && 
                  item.product.stock > 0 && 
                  item.quantity >= item.product.stock
                }
                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
              >
                <Text style={styles.quantityButtonText}>+</Text>
              </TouchableOpacity>
            </View>
          )}

          {/* Avertissement stock */}
          {item.product.stock !== undefined && 
           item.product.stock > 0 && 
           item.quantity >= item.product.stock && (
            <Text style={styles.stockWarning}>
              Stock limité: {item.product.stock} disponible{item.product.stock > 1 ? 's' : ''}
            </Text>
          )}
        </View>
        <TouchableOpacity
          style={styles.removeButton}
          onPress={() => handleRemoveItem(item.id)}
        >
          <Text style={styles.removeButtonText}>×</Text>
        </TouchableOpacity>
      </View>
    );
  };

  if (isLoading && items.length === 0) {
    return <LoadingScreen />;
  }

  return (
    <View style={styles.container}>
      <Header
        showCategories={true}
        categories={categories}
        onCategoryPress={(categoryId: number) => (navigation as any).navigate('Products', { categoryId })}
        showSearch={false}
      />
      {items.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>Votre panier est vide</Text>
          <TouchableOpacity
            style={styles.shopButton}
            onPress={() => {
              // Naviguer vers le Tab Products et réinitialiser la stack vers ProductList
              (navigation as any).navigate('Products', {
                screen: 'ProductList',
                params: undefined,
              });
            }}
          >
            <Text style={styles.shopButtonText}>Continuer les achats</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <>
          <FlatList
            data={(items || []).filter(item => item && item.product && item.id)}
            renderItem={renderItem}
            keyExtractor={(item) => item.id.toString()}
            contentContainerStyle={styles.list}
            refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
            ListEmptyComponent={
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyText}>Votre panier est vide</Text>
              </View>
            }
            ListFooterComponent={
              items.length > 0 ? (
                <TouchableOpacity 
                  style={styles.clearButton} 
                  onPress={handleClearCart}
                  hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                >
                  <Text style={styles.clearButtonText}>Vider le panier</Text>
                </TouchableOpacity>
              ) : null
            }
          />
          <View style={styles.footer}>
            <View style={styles.summaryContainer}>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Articles:</Text>
                <Text style={styles.summaryValue}>
                  {itemsCount} article{itemsCount > 1 ? 's' : ''}
                </Text>
              </View>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Total:</Text>
                <Text style={styles.totalPrice}>
                  {formatPrice(
                    (() => {
                      const calculatedTotal = items.reduce((sum, item) => sum + getTotalItemPrice(item), 0);
                      return calculatedTotal;
                    })()
                  )}
                </Text>
              </View>
            </View>
            <TouchableOpacity 
              style={[styles.checkoutButton, isLoading && styles.checkoutButtonDisabled]} 
              onPress={handleCheckout}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color="#FFFFFF" />
              ) : (
                <Text style={styles.checkoutButtonText}>Passer la commande</Text>
              )}
            </TouchableOpacity>
          </View>
        </>
      )}
    </View>
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
  list: {
    padding: 16,
  },
  itemContainer: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  itemImage: {
    width: 80,
    height: 80,
    borderRadius: 8,
    marginRight: 12,
  },
  itemInfo: {
    flex: 1,
  },
  itemTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 4,
  },
  priceContainer: {
    marginBottom: 8,
  },
  priceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
  },
  itemPrice: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.PRIMARY,
    marginRight: 8,
  },
  unitPrice: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
  },
  variantContainer: {
    marginTop: 4,
    marginBottom: 4,
  },
  variantText: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
    fontStyle: 'italic',
  },
  attributesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 4,
    marginBottom: 4,
  },
  attributeText: {
    fontSize: 11,
    color: COLORS.TEXT_SECONDARY,
    marginRight: 8,
  },
  stockWarning: {
    fontSize: 11,
    color: COLORS.WARNING,
    marginTop: 4,
    fontStyle: 'italic',
  },
  quantityContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  quantityButton: {
    width: 36, // Augmenté de 32 à 36
    height: 36, // Augmenté de 32 à 36
    borderRadius: 18,
    backgroundColor: COLORS.PRIMARY,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 2, // Petite ombre pour le relief
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.41,
  },
  quantityButtonDisabled: {
    backgroundColor: COLORS.TEXT_SECONDARY,
    opacity: 0.5,
  },
  quantityButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  quantityValue: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginHorizontal: 12,
    minWidth: 30,
    textAlign: 'center',
  },
  removeButton: {
    width: 32,
    height: 32,
    justifyContent: 'center',
    alignItems: 'center',
  },
  removeButtonText: {
    fontSize: 24,
    color: COLORS.ERROR,
    fontWeight: 'bold',
  },
  footer: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  summaryContainer: {
    marginBottom: 16,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  summaryLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: COLORS.TEXT,
  },
  summaryValue: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.TEXT,
  },
  totalPrice: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.PRIMARY,
  },
  checkoutButton: {
    backgroundColor: COLORS.PRIMARY,
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 50,
  },
  checkoutButtonDisabled: {
    opacity: 0.6,
  },
  checkoutButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
  },
  clearButton: {
    padding: 12,
    alignItems: 'center',
  },
  clearButtonText: {
    color: COLORS.ERROR,
    fontSize: 16,
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 20,
    color: COLORS.TEXT_SECONDARY,
    marginBottom: 24,
  },
  shopButton: {
    backgroundColor: COLORS.PRIMARY,
    borderRadius: 8,
    padding: 16,
    paddingHorizontal: 32,
  },
  shopButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default CartScreen;
