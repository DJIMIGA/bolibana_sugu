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
import { fetchCart, updateCartItem, removeFromCart, clearCart, optimisticUpdateQuantity } from '../store/slices/cartSlice';
import { fetchCategories, setSearchQuery, searchProducts, fetchProducts } from '../store/slices/productSlice';
import { useNavigation } from '@react-navigation/native';
import { formatPrice, debounce } from '../utils/helpers';
import { COLORS } from '../utils/constants';
import { CartItem } from '../types';
import { Header } from '../components/Header';
import { LoadingScreen } from '../components/LoadingScreen';

const CartScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigation = useNavigation();
  const { cart, items, total, itemsCount, isLoading } = useAppSelector((state) => state.cart);
  const { categories, searchQuery } = useAppSelector((state) => state.product);
  const [refreshing, setRefreshing] = useState(false);
  const [localSearch, setLocalSearch] = useState(searchQuery);

  // Fonction pour envoyer la mise à jour au serveur (débouncée)
  const debouncedUpdate = useCallback(
    debounce((itemId: number, quantity: number) => {
      dispatch(updateCartItem({ itemId, quantity }));
    }, 500),
    [dispatch]
  );

  useEffect(() => {
    dispatch(fetchCart());
    dispatch(fetchCategories());
  }, [dispatch]);

  const onRefresh = async () => {
    setRefreshing(true);
    await dispatch(fetchCart());
    setRefreshing(false);
  };

  const handleUpdateQuantity = (itemId: number, newQuantity: number) => {
    if (newQuantity <= 0) {
      handleRemoveItem(itemId);
      return;
    }
    
    const item = items.find(i => i.id === itemId);
    if (item && item.product.stock !== undefined && item.product.stock > 0 && newQuantity > item.product.stock) {
      Alert.alert('Stock insuffisant', `Stock disponible: ${item.product.stock}`);
      return;
    }
    
    // 1. Mise à jour visuelle instantanée
    dispatch(optimisticUpdateQuantity({ itemId, quantity: newQuantity }));
    
    // 2. Programmation de la mise à jour serveur
    debouncedUpdate(itemId, newQuantity);
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
    // Navigation vers l'écran de checkout
    navigation.navigate('Checkout' as never);
  };

  const handleSearch = (text: string) => {
    setLocalSearch(text);
    if (text.trim()) {
      dispatch(setSearchQuery(text));
      dispatch(searchProducts(text));
    } else {
      dispatch(setSearchQuery(''));
      dispatch(fetchProducts({ page: 1 }));
    }
  };

  const handleClearSearch = () => {
    setLocalSearch('');
    dispatch(setSearchQuery(''));
    dispatch(fetchProducts({ page: 1 }));
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
    return item.product.discount_price || item.product.price;
  };

  const getTotalItemPrice = (item: CartItem): number => {
    return getUnitPrice(item) * item.quantity;
  };

  const renderItem = ({ item }: { item: CartItem }) => {
    // Vérification de sécurité
    if (!item || !item.product) {
      return null;
    }

    const unitPrice = getUnitPrice(item);
    const totalItemPrice = getTotalItemPrice(item);
    const variantInfo = getVariantInfo(item);
    const hasDiscount = item.product.discount_price && item.product.discount_price < item.product.price;

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
                  {formatPrice(unitPrice)} / unité
                </Text>
              </View>
            ) : (
              <View style={styles.priceRow}>
                <Text style={styles.itemPrice}>
                  {formatPrice(totalItemPrice)}
                </Text>
                <Text style={styles.unitPrice}>
                  {formatPrice(unitPrice)} / unité
                </Text>
              </View>
            )}
          </View>

          {/* Contrôle de quantité */}
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
        searchQuery={localSearch}
        onSearchChange={handleSearch}
        onClearSearch={handleClearSearch}
        showCategories={true}
        categories={categories}
        onCategoryPress={(categoryId: number) => (navigation as any).navigate('Products', { categoryId })}
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
                <Text style={styles.totalPrice}>{formatPrice(total)}</Text>
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
