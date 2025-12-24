import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  SafeAreaView,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchProductDetail, fetchSimilarProducts } from '../store/slices/productSlice';
import { addToCart } from '../store/slices/cartSlice';
import { useRoute, useNavigation } from '@react-navigation/native';
import { formatPrice } from '../utils/helpers';
import { COLORS } from '../utils/constants';
import { Product } from '../types';
import DynamicProductCard from '../components/DynamicProductCard';

const ProductDetailScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigation = useNavigation();
  const route = useRoute();
  const insets = useSafeAreaInsets();
  const { selectedProduct, isLoading, similarProducts, isFetchingSimilarProducts } = useAppSelector((state) => state.product);
  const { isLoading: isAddingToCart } = useAppSelector((state) => state.cart);
  const [quantity, setQuantity] = useState(1);
  const slug = (route.params as any)?.slug;

  useEffect(() => {
    if (slug) {
      dispatch(fetchProductDetail(slug));
    }
  }, [dispatch, slug]);

  useEffect(() => {
    if (selectedProduct?.id) {
      dispatch(fetchSimilarProducts(selectedProduct.id));
    }
  }, [dispatch, selectedProduct?.id]);

  const handleAddToCart = async () => {
    if (!selectedProduct) return;

    try {
      await dispatch(
        addToCart({
          product: selectedProduct.id,
          quantity,
        })
      ).unwrap();
      Alert.alert('Succès', 'Produit ajouté au panier');
    } catch (error: any) {
      Alert.alert('Erreur', error || 'Impossible d\'ajouter le produit au panier');
    }
  };

  if (isLoading || !selectedProduct) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.PRIMARY} />
      </View>
    );
  }

  const hasDiscount = selectedProduct.discount_price && 
                     selectedProduct.discount_price > 0 && 
                     selectedProduct.price > 0 &&
                     selectedProduct.discount_price < selectedProduct.price;
  
  const discountPercentage = hasDiscount && selectedProduct.price > 0
    ? Math.round(((selectedProduct.price - selectedProduct.discount_price!) / selectedProduct.price) * 100)
    : 0;

  return (
    <SafeAreaView style={styles.container}>
      {/* Header avec bouton retour et titre */}
      <View style={[styles.headerContainer, { paddingTop: Math.max(insets.top + 8, 20) }]}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
          activeOpacity={0.8}
        >
          <Ionicons name="arrow-back" size={24} color={COLORS.TEXT} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Détails du produit</Text>
        <View style={styles.headerSpacer} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
      {/* Image du produit avec badge de promotion */}
      <View style={styles.imageContainer}>
        {selectedProduct.image || selectedProduct.image_urls?.main ? (
          <Image
            source={{ uri: selectedProduct.image || selectedProduct.image_urls?.main }}
            style={styles.image}
            resizeMode="cover"
          />
        ) : (
          <View style={styles.imagePlaceholder}>
            <MaterialIcons name="image-not-supported" size={64} color={COLORS.TEXT_SECONDARY} />
          </View>
        )}
        
        {/* Badge de promotion */}
        {discountPercentage > 0 && (
          <View style={styles.discountBadge}>
            <View style={styles.discountBadgeInner}>
              <Text style={styles.discountBadgeText}>-{discountPercentage}%</Text>
            </View>
            <View style={styles.discountBadgeTriangle} />
          </View>
        )}

        {/* Badge SALAM */}
        {selectedProduct.is_salam && (
          <View style={styles.salamBadge}>
            <Text style={styles.salamBadgeText}>SALAM</Text>
          </View>
        )}
      </View>

      {/* Contenu principal */}
      <View style={styles.content}>
        {/* En-tête avec titre et marque */}
        <View style={styles.header}>
          {selectedProduct.brand && (
            <View style={styles.brandContainer}>
              <MaterialIcons name="business" size={18} color={COLORS.PRIMARY} />
              <Text style={styles.brand}>{selectedProduct.brand}</Text>
            </View>
          )}
          <Text style={styles.title}>{selectedProduct.title}</Text>
          
          {/* Note et avis */}
          {selectedProduct.average_rating && selectedProduct.average_rating > 0 && (
            <View style={styles.ratingContainer}>
              <Ionicons name="star" size={16} color={COLORS.SECONDARY} />
              <Text style={styles.ratingText}>
                {selectedProduct.average_rating.toFixed(1)} ({selectedProduct.review_count || 0} avis)
              </Text>
            </View>
          )}
        </View>

        {/* Prix */}
        <View style={styles.priceSection}>
          {hasDiscount ? (
            <View style={styles.priceContainer}>
              <View style={styles.priceRow}>
                <Text style={styles.discountPrice}>
                  {formatPrice(selectedProduct.discount_price!)}
                </Text>
                <View style={styles.discountTag}>
                  <Text style={styles.discountTagText}>PROMO</Text>
                </View>
              </View>
            </View>
          ) : (
            <Text style={styles.price}>{formatPrice(selectedProduct.price)}</Text>
          )}
        </View>

        {/* Indicateur de stock */}
        {selectedProduct.stock !== undefined && (
          <View style={styles.stockContainer}>
            {selectedProduct.stock > 0 ? (
              <View style={styles.stockAvailable}>
                <View style={styles.stockDot} />
                <Text style={styles.stockText}>
                  {selectedProduct.stock > 10 
                    ? 'En stock' 
                    : `Plus que ${selectedProduct.stock} disponible${selectedProduct.stock > 1 ? 's' : ''}`}
                </Text>
              </View>
            ) : (
              <View style={styles.stockUnavailable}>
                <MaterialIcons name="error-outline" size={18} color={COLORS.DANGER} />
                <Text style={styles.stockTextUnavailable}>Rupture de stock</Text>
              </View>
            )}
          </View>
        )}

        {/* Contrôle de quantité */}
        <View style={styles.quantitySection}>
          <Text style={styles.quantityLabel}>Quantité</Text>
          <View style={styles.quantityContainer}>
            <TouchableOpacity
              style={[styles.quantityButton, quantity === 1 && styles.quantityButtonDisabled]}
              onPress={() => setQuantity(Math.max(1, quantity - 1))}
              disabled={quantity === 1}
            >
              <Ionicons 
                name="remove" 
                size={20} 
                color={quantity === 1 ? COLORS.TEXT_SECONDARY : COLORS.TEXT} 
              />
            </TouchableOpacity>
            <View style={styles.quantityValueContainer}>
              <Text style={styles.quantityValue}>{quantity}</Text>
            </View>
            <TouchableOpacity
              style={styles.quantityButton}
              onPress={() => setQuantity(quantity + 1)}
            >
              <Ionicons name="add" size={20} color={COLORS.TEXT} />
            </TouchableOpacity>
          </View>
        </View>

        {/* Bouton Ajouter au panier */}
        <TouchableOpacity
          style={[
            styles.addToCartButton, 
            !selectedProduct.is_available && styles.disabledButton
          ]}
          onPress={handleAddToCart}
          disabled={!selectedProduct.is_available || isAddingToCart}
          activeOpacity={0.8}
        >
          {isAddingToCart ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <View style={styles.addToCartContent}>
              <MaterialIcons 
                name={selectedProduct.is_available ? "shopping-cart" : "block"} 
                size={24} 
                color="#FFFFFF" 
              />
              <Text style={styles.addToCartText}>
                {selectedProduct.is_available ? 'Ajouter au panier' : 'Indisponible'}
              </Text>
            </View>
          )}
        </TouchableOpacity>

        {/* Description */}
        {selectedProduct.description && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <MaterialIcons name="description" size={20} color={COLORS.PRIMARY} />
              <Text style={styles.sectionTitle}>Description</Text>
            </View>
            <Text style={styles.description}>{selectedProduct.description}</Text>
          </View>
        )}

        {/* Caractéristiques techniques avec cartes individuelles */}
        {selectedProduct.specifications && Object.keys(selectedProduct.specifications).length > 0 && (
          <View style={styles.specsSection}>
            <View style={styles.sectionHeader}>
              <MaterialIcons name="settings" size={20} color={COLORS.PRIMARY} />
              <Text style={styles.sectionTitle}>Caractéristiques techniques</Text>
            </View>
            <View style={styles.specsGrid}>
              {Object.entries(selectedProduct.specifications).map(([key, value]) => {
                // Traduire les clés en français
                const translateKey = (specKey: string): string => {
                  const lowerKey = specKey.toLowerCase();
                  const translations: Record<string, string> = {
                    'brand': 'Marque',
                    'model': 'Modèle',
                    'color': 'Couleur',
                    'color_name': 'Couleur',
                    'condition': 'État',
                    'is_new': 'État',
                    'storage': 'Stockage',
                    'ram': 'RAM',
                    'screen_size': 'Taille d\'écran',
                    'resolution': 'Résolution',
                    'operating_system': 'Système d\'exploitation',
                    'processor': 'Processeur',
                    'battery_capacity': 'Batterie',
                    'camera_main': 'Caméra principale',
                    'camera_front': 'Caméra frontale',
                    'network': 'Réseau',
                    'box_included': 'Boîte incluse',
                    'accessories': 'Accessoires',
                  };
                  
                  // Chercher une correspondance exacte ou partielle
                  for (const [enKey, frValue] of Object.entries(translations)) {
                    if (lowerKey === enKey || lowerKey.includes(enKey)) {
                      return frValue;
                    }
                  }
                  
                  // Si pas de traduction, capitaliser la première lettre
                  return specKey.charAt(0).toUpperCase() + specKey.slice(1).replace(/_/g, ' ');
                };

                // Déterminer l'icône selon la clé
                const getIcon = (specKey: string) => {
                  const lowerKey = specKey.toLowerCase();
                  if (lowerKey.includes('marque') || lowerKey.includes('brand')) return 'business';
                  if (lowerKey.includes('modèle') || lowerKey.includes('model')) return 'phone-android';
                  if (lowerKey.includes('couleur') || lowerKey.includes('color')) return 'palette';
                  if (lowerKey.includes('état') || lowerKey.includes('condition') || lowerKey.includes('is_new')) return 'verified';
                  if (lowerKey.includes('stockage') || lowerKey.includes('storage')) return 'storage';
                  if (lowerKey.includes('ram')) return 'memory';
                  if (lowerKey.includes('écran') || lowerKey.includes('screen')) return 'screen-lock-portrait';
                  if (lowerKey.includes('résolution') || lowerKey.includes('resolution')) return 'high-quality';
                  if (lowerKey.includes('système') || lowerKey.includes('os') || lowerKey.includes('operating')) return 'settings';
                  if (lowerKey.includes('processeur') || lowerKey.includes('processor')) return 'speed';
                  if (lowerKey.includes('batterie') || lowerKey.includes('battery')) return 'battery-charging-full';
                  if (lowerKey.includes('réseau') || lowerKey.includes('network')) return 'network-cell';
                  if (lowerKey.includes('caméra') || lowerKey.includes('camera')) return 'camera-alt';
                  if (lowerKey.includes('box') || lowerKey.includes('accessories')) return 'inventory';
                  return 'info';
                };

                const translatedKey = translateKey(key);
                const displayValue = String(value);

                return (
                  <View key={key} style={styles.specCard}>
                    <View style={styles.specCardContent}>
                      <View style={styles.specIconContainer}>
                        <MaterialIcons 
                          name={getIcon(key) as any} 
                          size={20} 
                          color={COLORS.PRIMARY} 
                        />
                      </View>
                      <View style={styles.specCardText}>
                        <Text style={styles.specCardLabel}>{translatedKey}</Text>
                        <Text style={styles.specCardValue} numberOfLines={1}>
                          {displayValue}
                        </Text>
                      </View>
                    </View>
                  </View>
                );
              })}
            </View>
          </View>
        )}

        {/* Informations supplémentaires */}
        <View style={styles.infoSection}>
          {selectedProduct.condition && (
            <View style={styles.infoItem}>
              <MaterialIcons name="verified" size={18} color={COLORS.PRIMARY} />
              <Text style={styles.infoText}>État: {selectedProduct.condition}</Text>
            </View>
          )}
          {selectedProduct.has_warranty && (
            <View style={styles.infoItem}>
              <MaterialIcons name="security" size={18} color={COLORS.SECONDARY} />
              <Text style={styles.infoText}>Garantie incluse</Text>
            </View>
          )}
        </View>
      </View>

      {/* Produits similaires */}
      {similarProducts.length > 0 && (
        <View style={styles.similarProductsContainer}>
          <View style={styles.similarProductsHeader}>
            <MaterialIcons name="shopping-bag" size={24} color={COLORS.PRIMARY} />
            <Text style={styles.similarProductsTitle}>Produits Similaires</Text>
          </View>
          {isFetchingSimilarProducts ? (
            <View style={styles.loadingSimilar}>
              <ActivityIndicator size="small" color={COLORS.PRIMARY} />
            </View>
          ) : (
            <ScrollView 
              horizontal 
              showsHorizontalScrollIndicator={false} 
              contentContainerStyle={styles.similarProductsScroll}
            >
              {similarProducts.map((product) => (
                <DynamicProductCard key={product.id} product={product} />
              ))}
            </ScrollView>
          )}
        </View>
      )}
    </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.BACKGROUND,
  },
  headerContainer: {
    backgroundColor: '#FFFFFF',
    paddingTop: 16,
    paddingBottom: 12,
    paddingHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 3,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 5,
  },
  headerTitle: {
    flex: 1,
    fontSize: 18,
    fontWeight: '700',
    color: COLORS.TEXT,
    textAlign: 'center',
    marginHorizontal: 16,
  },
  headerSpacer: {
    width: 40,
  },
  content: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.BACKGROUND,
  },
  imageContainer: {
    width: '100%',
    height: 400,
    position: 'relative',
    backgroundColor: '#F9FAFB',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  imagePlaceholder: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
  },
  discountBadge: {
    position: 'absolute',
    top: 16,
    right: 16,
    zIndex: 10,
    alignItems: 'center',
  },
  discountBadgeInner: {
    backgroundColor: COLORS.DANGER,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.4,
    shadowRadius: 4,
    elevation: 6,
  },
  discountBadgeTriangle: {
    width: 0,
    height: 0,
    borderLeftWidth: 6,
    borderRightWidth: 6,
    borderTopWidth: 6,
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
    borderTopColor: '#DC2626',
    marginTop: -1,
  },
  discountBadgeText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '900',
    letterSpacing: 0.5,
  },
  salamBadge: {
    position: 'absolute',
    top: 16,
    left: 16,
    backgroundColor: COLORS.SECONDARY,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  salamBadgeText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  content: {
    padding: 20,
    backgroundColor: COLORS.BACKGROUND,
  },
  header: {
    marginBottom: 20,
  },
  brandContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  brand: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.PRIMARY,
    marginLeft: 6,
  },
  title: {
    fontSize: 26,
    fontWeight: '800',
    color: COLORS.TEXT,
    marginBottom: 12,
    lineHeight: 32,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  ratingText: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
    marginLeft: 6,
    fontWeight: '600',
  },
  priceSection: {
    marginBottom: 20,
    paddingBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  priceContainer: {
    flexDirection: 'column',
  },
  priceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  price: {
    fontSize: 32,
    fontWeight: '900',
    color: COLORS.DANGER,
    letterSpacing: -0.5,
  },
  discountPrice: {
    fontSize: 32,
    fontWeight: '900',
    color: COLORS.DANGER,
    letterSpacing: -0.5,
    marginRight: 12,
  },
  discountTag: {
    backgroundColor: COLORS.DANGER,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  discountTagText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  stockContainer: {
    marginBottom: 24,
  },
  stockAvailable: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F0FDF4',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: COLORS.PRIMARY,
  },
  stockUnavailable: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEE2E2',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: COLORS.DANGER,
  },
  stockDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: COLORS.PRIMARY,
    marginRight: 8,
  },
  stockText: {
    fontSize: 14,
    color: COLORS.PRIMARY,
    fontWeight: '600',
  },
  stockTextUnavailable: {
    fontSize: 14,
    color: COLORS.DANGER,
    fontWeight: '600',
    marginLeft: 6,
  },
  quantitySection: {
    marginBottom: 24,
  },
  quantityLabel: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.TEXT,
    marginBottom: 12,
  },
  quantityContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 4,
    borderWidth: 1.5,
    borderColor: '#E5E7EB',
  },
  quantityButton: {
    width: 48,
    height: 48,
    borderRadius: 10,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  quantityButtonDisabled: {
    opacity: 0.5,
  },
  quantityValueContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 16,
  },
  quantityValue: {
    fontSize: 20,
    fontWeight: '700',
    color: COLORS.TEXT,
    minWidth: 40,
    textAlign: 'center',
  },
  addToCartButton: {
    backgroundColor: COLORS.PRIMARY,
    borderRadius: 12,
    padding: 18,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 32,
    shadowColor: COLORS.PRIMARY,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  disabledButton: {
    backgroundColor: COLORS.TEXT_SECONDARY,
    opacity: 0.6,
    shadowOpacity: 0,
  },
  addToCartContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  addToCartText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '700',
    marginLeft: 8,
  },
  section: {
    marginBottom: 32,
  },
  specsSection: {
    marginBottom: 24,
    paddingHorizontal: 0,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    paddingHorizontal: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: COLORS.TEXT,
    marginLeft: 8,
  },
  description: {
    fontSize: 16,
    color: COLORS.TEXT_SECONDARY,
    lineHeight: 24,
  },
  specsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginTop: 4,
    paddingHorizontal: 0,
    width: '100%',
  },
  specCard: {
    width: '48.5%',
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
    minHeight: 65,
  },
  specCardContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  specIconContainer: {
    width: 30,
    height: 30,
    borderRadius: 8,
    backgroundColor: `${COLORS.PRIMARY}15`,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
    flexShrink: 0,
  },
  specCardText: {
    flex: 1,
    minWidth: 0,
  },
  specCardLabel: {
    fontSize: 10,
    fontWeight: '600',
    color: COLORS.TEXT_SECONDARY,
    marginBottom: 2,
  },
  specCardValue: {
    fontSize: 12,
    fontWeight: '700',
    color: COLORS.TEXT,
    lineHeight: 15,
  },
  infoSection: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 32,
    gap: 12,
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  infoText: {
    fontSize: 14,
    color: COLORS.TEXT,
    marginLeft: 6,
    fontWeight: '600',
  },
  similarProductsContainer: {
    marginTop: 8,
    paddingBottom: 32,
    backgroundColor: '#F9FAFB',
    paddingTop: 24,
  },
  similarProductsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    marginBottom: 16,
  },
  similarProductsTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: COLORS.TEXT,
    marginLeft: 8,
  },
  loadingSimilar: {
    padding: 20,
    alignItems: 'center',
  },
  similarProductsScroll: {
    paddingHorizontal: 12,
    paddingBottom: 16,
  },
});

export default ProductDetailScreen;
