import React, { useEffect, useMemo, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Dimensions,
  FlatList,
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
import { LoadingScreen } from '../components/LoadingScreen';
import ProductImage from '../components/ProductImage';

const ProductDetailScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigation = useNavigation();
  const route = useRoute();
  const insets = useSafeAreaInsets();
  const { selectedProduct, isLoading, similarProducts, isFetchingSimilarProducts, categories } = useAppSelector((state) => state.product);
  const { isReadOnly } = useAppSelector((state) => state.auth);
  const { items, isLoading: isAddingToCart } = useAppSelector((state) => state.cart);
  const [quantity, setQuantity] = useState(1);
  const [activeImageIndex, setActiveImageIndex] = useState(0);
  const slug = (route.params as any)?.slug;

  // Vérifier si le produit est déjà dans le panier
  const itemInCart = selectedProduct ? items.find(item => item.product.id === selectedProduct.id) : null;

  // Réinitialiser la quantité quand le produit change
  useEffect(() => {
    if (selectedProduct) {
      const specs = selectedProduct.specifications || {};
      const isWeighted = isWeightedProduct(specs);
      const weightUnit = getWeightUnit(specs);
      // Pour les produits au poids, initialiser au minimum selon l'unité
      if (isWeighted) {
        setQuantity(weightUnit === 'g' ? 1 : 0.5);
      } else {
        setQuantity(1);
      }
    }
  }, [selectedProduct?.id]);

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

  // Préparer la liste des images pour le carrousel (toujours appeler les hooks, même si selectedProduct est null)
  const images: string[] = useMemo(() => {
    if (!selectedProduct) return [];
    const imgs: string[] = [];
    if (selectedProduct.image) imgs.push(selectedProduct.image);
    if (selectedProduct.image_urls?.gallery) {
      selectedProduct.image_urls.gallery.forEach((img) => {
        if (!imgs.includes(img)) imgs.push(img);
      });
    }
    return imgs;
  }, [selectedProduct?.id, selectedProduct?.image, selectedProduct?.image_urls?.gallery]);

  // Fonction helper pour formater le poids (définie avant handleAddToCart)
  const formatAvailableWeight = (weight: number | undefined): string => {
    if (weight === undefined || weight === null) return '0';
    const specs = selectedProduct?.specifications || {};
    // Utiliser la valeur formatée depuis les spécifications si disponible (évite l'arrondi)
    if (specs.formatted_quantity) {
      return specs.formatted_quantity;
    }
    // Sinon, formater avec précision (jusqu'à 3 décimales pour éviter l'arrondi à 1.00)
    if (weight % 1 !== 0) {
      // Garder les décimales significatives sans arrondir
      const str = weight.toString();
      if (str.includes('.')) {
        const parts = str.split('.');
        const decimals = parts[1].length;
        // Garder jusqu'à 3 décimales, mais ne pas arrondir
        return decimals <= 3 ? str : weight.toFixed(3);
      }
      return weight.toFixed(3);
    }
    return weight.toFixed(0);
  };

  // Formater la quantité pour l'affichage (évite l'arrondi à 1.0)
  const formatQuantity = (qty: number): string => {
    // Si c'est un entier, afficher sans décimales
    if (qty % 1 === 0) {
      return qty.toString();
    }
    // Pour les décimales, garder la précision exacte (jusqu'à 3 décimales)
    // Utiliser toFixed avec le nombre de décimales nécessaires, puis supprimer les zéros de fin
    const fixed = qty.toFixed(3);
    // Supprimer les zéros de fin inutiles
    return fixed.replace(/\.?0+$/, '');
  };

  const handleAddToCart = async () => {
    if (!selectedProduct) return;

    // Vérifier la disponibilité
    if (!selectedProduct.is_available) {
      Alert.alert('Indisponible', 'Ce produit n\'est actuellement pas disponible');
      return;
    }

    // Détecter si c'est un produit au poids (utiliser la même logique que dans le JSX)
    const specs = selectedProduct.specifications || {};
    const isWeighted = isWeightedProduct(specs);

    // Vérifier le stock (sauf pour les produits Salam)
    if (!selectedProduct.is_salam) {
      if (isWeighted) {
        // Pour les produits au poids, vérifier le poids disponible
        const availableWeight = getAvailableWeight(specs);
        const weightUnit = getWeightUnit(specs);
        const existingQuantity = itemInCart ? (Number(itemInCart.quantity) || 0) : 0;
        const desiredTotal = existingQuantity + quantity;
        if (availableWeight > 0 && desiredTotal > availableWeight) {
          Alert.alert(
            'Stock insuffisant',
            `Poids disponible: ${formatAvailableWeight(availableWeight)} ${weightUnit}. Veuillez réduire la quantité.`
          );
          return;
        }
        const minQuantity = weightUnit === 'g' ? 1 : 0.5;
        // Vérifier le minimum (0.5 kg ou 1 g)
        if (quantity < minQuantity) {
          Alert.alert('Quantité minimale', `La quantité minimale est de ${minQuantity} ${weightUnit}`);
          return;
        }
      } else {
        // Pour les produits normaux, vérifier le stock en unités
        if (selectedProduct.stock !== undefined && selectedProduct.stock > 0) {
          if (quantity > selectedProduct.stock) {
            Alert.alert(
              'Stock insuffisant',
              `Stock disponible: ${selectedProduct.stock}. Veuillez réduire la quantité.`
            );
            return;
          }
        }
      }
    }

    if (isReadOnly) {
      Alert.alert(
        'Mode lecture seule',
        'Votre session a expiré ou vous êtes hors ligne. Veuillez vous connecter pour ajouter des produits au panier.'
      );
      return;
    }

    try {
      await dispatch(
        addToCart({
          product: selectedProduct.id,
          quantity,
        })
      ).unwrap();
      Alert.alert('Succès', 'Produit ajouté au panier');
    } catch (error: any) {
      const errorMessage = typeof error === 'string' ? error : 'Impossible d\'ajouter le produit au panier';
      Alert.alert('Erreur', errorMessage);
    }
  };

  if (isLoading || !selectedProduct) {
    return <LoadingScreen />;
  }

  const getWeightUnit = (specsData: any): string => {
    const unitRaw = specsData?.weight_unit || specsData?.unit_display || specsData?.unit_type;
    if (!unitRaw) return 'kg';
    const unit = String(unitRaw).toLowerCase();
    if (['weight', 'kg', 'kilogram'].includes(unit)) return 'kg';
    if (['g', 'gram', 'gramme'].includes(unit)) return 'g';
    return unit;
  };

  const isWeightedProduct = (specsData: any): boolean => {
    const specs = specsData || {};
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

  const getAvailableWeight = (specsData: any): number => {
    const unit = getWeightUnit(specsData);
    if (unit === 'g') {
      const availableG = specsData?.available_weight_g;
      if (availableG !== undefined && availableG !== null) return Number(availableG) || 0;
    }
    return Number(specsData?.available_weight_kg) || 0;
  };

  // Vérifier si c'est un produit au poids
  const specs = selectedProduct.specifications || {};
  const isWeighted = isWeightedProduct(specs);
  const weightUnit = getWeightUnit(specs);

  // Vérifier la disponibilité du stock (poids pour les produits au poids, unités pour les autres)
  const hasStock = isWeighted 
    ? (getAvailableWeight(specs) > 0)
    : (selectedProduct.stock !== undefined && selectedProduct.stock > 0);
  
  const availableStock = isWeighted
    ? getAvailableWeight(specs)
    : selectedProduct.stock;


  // Obtenir le prix unitaire (au kg pour les produits au poids, unitaire pour les autres)
  const getUnitPrice = (): number => {
    if (isWeighted) {
      const unit = getWeightUnit(specs);
      if (unit === 'g') {
        const pricePerG = specs.price_per_g;
        if (pricePerG) {
          return pricePerG;
        }
      } else {
        // Pour les produits au poids, utiliser price_per_kg depuis les spécifications
        const pricePerKg = specs.price_per_kg;
        if (pricePerKg) {
          return pricePerKg;
        }
      }
    }
    return selectedProduct.price;
  };

  const getDiscountPrice = (): number | undefined => {
    if (isWeighted) {
      const unit = getWeightUnit(specs);
      if (unit === 'g') {
        const discountPricePerG = specs.discount_price_per_g;
        if (discountPricePerG) {
          return discountPricePerG;
        }
      } else {
        // Pour les produits au poids, vérifier s'il y a un discount_price_per_kg
        const discountPricePerKg = specs.discount_price_per_kg;
        if (discountPricePerKg) {
          return discountPricePerKg;
        }
      }
    }
    return selectedProduct.discount_price;
  };

  const unitPrice = getUnitPrice();
  const discountPrice = getDiscountPrice();
  const hasDiscount = discountPrice &&
                     discountPrice > 0 &&
                     unitPrice > 0 &&
                     discountPrice < unitPrice;
  
  const discountPercentage = hasDiscount && unitPrice > 0
    ? Math.round(((unitPrice - discountPrice!) / unitPrice) * 100)
    : 0;

  const hasImages = images.length > 0;
  const screenWidth = Dimensions.get('window').width;

  return (
    <View style={styles.container}>
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

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
      {/* Image du produit avec carrousel si plusieurs images */}
      <View style={styles.imageContainer}>
        {hasImages ? (
          <>
            <FlatList
              data={images}
              horizontal
              pagingEnabled
              showsHorizontalScrollIndicator={false}
              onMomentumScrollEnd={(e) => {
                const index = Math.round(e.nativeEvent.contentOffset.x / screenWidth);
                setActiveImageIndex(index);
              }}
              keyExtractor={(_, index) => `image-${index}`}
              renderItem={({ item }) => (
                <ProductImage
                  uri={item}
                  style={styles.carouselImage}
                  resizeMode="contain"
                  fallback={
                    <View style={styles.imagePlaceholder}>
                      <MaterialIcons name="image-not-supported" size={64} color={COLORS.TEXT_SECONDARY} />
                    </View>
                  }
                />
              )}
            />
            {images.length > 1 && (
              <View style={styles.paginationContainer}>
                {images.map((_, index) => (
                  <View
                    key={index}
                    style={[
                      styles.paginationDot,
                      activeImageIndex === index && styles.paginationDotActive,
                    ]}
                  />
                ))}
              </View>
            )}
          </>
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
      <View style={styles.mainContent}>
        {/* En-tête avec titre et marque */}
        <View style={styles.header}>
          {(() => {
            // Fonction helper pour extraire et nettoyer une valeur de marque
            // Basée sur la logique du template tag get_brand_name du web
            const extractBrand = (value: any): string | null => {
              if (!value) return null;
              
              // Si c'est un objet/dict (comme {id: 10, name: 'nike'})
              if (typeof value === 'object' && !Array.isArray(value) && value !== null) {
                // Chercher la propriété name en priorité (comme dans get_brand_name)
                if (value.name) {
                  const brandName = String(value.name).trim();
                  if (brandName.length > 0) return brandName;
                }
                // Si pas de name, retourner la représentation string de l'objet (comme dans get_brand_name)
                return String(value);
              }
              
              // Si c'est une string
              if (typeof value === 'string') {
                const trimmed = value.trim();
                // Si la string ressemble à un dict (commence par {), essayer de parser
                if (trimmed.startsWith('{')) {
                  try {
                    const parsed = JSON.parse(trimmed);
                    if (parsed && typeof parsed === 'object' && parsed.name) {
                      return String(parsed.name).trim();
                    }
                  } catch {
                    // Si le parsing JSON échoue, essayer d'extraire avec regex (comme dans get_brand_name)
                    const match = trimmed.match(/'name':\s*['"]([^'"]+)['"]/);
                    if (match && match[1]) {
                      return match[1].trim();
                    }
                  }
                }
                return trimmed.length > 0 ? trimmed : null;
              }
              
              // Convertir en string si possible
              try {
                const str = String(value).trim();
                return str.length > 0 ? str : null;
              } catch {
                return null;
              }
            };

            // Extraire la marque depuis plusieurs sources possibles (dans l'ordre de priorité)
            const brand = 
              extractBrand(selectedProduct.brand) ||
              extractBrand(selectedProduct.specifications?.brand) ||
              extractBrand(selectedProduct.specifications?.manufacturer) ||
              extractBrand(selectedProduct.specifications?.brand_name) ||
              null;

            return brand ? (
              <View style={styles.brandContainer}>
                <MaterialIcons name="business" size={18} color={COLORS.PRIMARY} />
                <Text style={styles.brand}>{brand}</Text>
              </View>
            ) : null;
          })()}
          {selectedProduct.category && (() => {
            const category = categories.find(c => c.id === selectedProduct.category);
            return category ? (
              <View style={styles.categoryContainer}>
                <MaterialIcons name="category" size={18} color={COLORS.SECONDARY} />
                <Text style={styles.category}>{category.name}</Text>
              </View>
            ) : null;
          })()}
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
                  {formatPrice(discountPrice!)}
                </Text>
                <Text style={styles.oldPrice}>
                  {formatPrice(unitPrice)}
                </Text>
                <Text style={styles.priceUnit}> / {isWeighted ? weightUnit : 'unité'}</Text>
                <View style={styles.discountTag}>
                  <Text style={styles.discountTagText}>PROMO</Text>
                </View>
              </View>
            </View>
          ) : (
            <View style={styles.priceRow}>
              <Text style={styles.price}>{formatPrice(unitPrice)}</Text>
              <Text style={styles.priceUnit}> / {isWeighted ? weightUnit : 'unité'}</Text>
            </View>
          )}
        </View>

        {/* Indicateur de stock */}
        {(selectedProduct.stock !== undefined || (isWeighted && getAvailableWeight(specs) !== undefined)) && (
          <View style={styles.stockContainer}>
            {hasStock ? (
              <View style={styles.stockAvailable}>
                <View style={styles.stockDot} />
                <Text style={styles.stockText}>
                  {isWeighted ? (
                    availableStock && availableStock > 0
                      ? `${formatAvailableWeight(availableStock)} ${weightUnit} disponible${availableStock > 1 ? 's' : ''}`
                      : 'En stock'
                  ) : (
                    availableStock && availableStock > 10
                      ? 'En stock'
                      : `Plus que ${availableStock} disponible${availableStock > 1 ? 's' : ''}`
                  )}
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

        {/* Contrôle de quantité/poids */}
        <View style={styles.quantitySection}>
          <Text style={styles.quantityLabel}>{isWeighted ? 'Poids' : 'Quantité'}</Text>
          <View style={styles.quantityContainer}>
            {isWeighted ? (
              <>
                <TouchableOpacity
                  style={[styles.quantityButton, quantity <= (weightUnit === 'g' ? 1 : 0.5) && styles.quantityButtonDisabled]}
                  onPress={() => {
                    const step = weightUnit === 'g' ? 1 : 0.5;
                    const newWeight = Math.max(step, quantity - step);
                    setQuantity(newWeight);
                  }}
                  disabled={quantity <= (weightUnit === 'g' ? 1 : 0.5)}
                >
                  <Ionicons 
                    name="remove" 
                    size={20} 
                    color={quantity <= (weightUnit === 'g' ? 1 : 0.5) ? COLORS.TEXT_SECONDARY : COLORS.TEXT} 
                  />
                </TouchableOpacity>
                <View style={styles.quantityValueContainer}>
                  <Text style={styles.quantityValue}>{formatQuantity(quantity)}</Text>
                  <Text style={styles.quantityUnit}>{weightUnit}</Text>
                </View>
                <TouchableOpacity
                  style={[
                    styles.quantityButton,
                    (availableStock && (quantity >= availableStock || (quantity + (weightUnit === 'g' ? 1 : 0.5)) > availableStock)) && styles.quantityButtonDisabled
                  ]}
                  onPress={() => {
                    const increment = weightUnit === 'g' ? 1 : 0.5;
                    // Vérifier qu'il y a assez de poids disponible pour ajouter le pas
                    if (availableStock && (quantity + increment) > availableStock) {
                      return; // Ne pas ajouter si pas assez de poids disponible
                    }
                    const newWeight = quantity + increment;
                    setQuantity(newWeight);
                  }}
                  disabled={availableStock ? (quantity >= availableStock || (quantity + (weightUnit === 'g' ? 1 : 0.5)) > availableStock) : false}
                >
                  <Ionicons 
                    name="add" 
                    size={20} 
                    color={(availableStock && (quantity >= availableStock || (quantity + (weightUnit === 'g' ? 1 : 0.5)) > availableStock)) ? COLORS.TEXT_SECONDARY : COLORS.TEXT} 
                  />
                </TouchableOpacity>
              </>
            ) : (
              <>
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
                  style={[
                    styles.quantityButton,
                    availableStock && quantity >= availableStock && styles.quantityButtonDisabled
                  ]}
                  onPress={() => {
                    const newQty = availableStock 
                      ? Math.min(availableStock, quantity + 1)
                      : quantity + 1;
                    setQuantity(newQty);
                  }}
                  disabled={availableStock ? quantity >= availableStock : false}
                >
                  <Ionicons 
                    name="add" 
                    size={20} 
                    color={(availableStock && quantity >= availableStock) ? COLORS.TEXT_SECONDARY : COLORS.TEXT} 
                  />
                </TouchableOpacity>
              </>
            )}
          </View>
        </View>

        <TouchableOpacity
          style={[
            styles.addToCartButton, 
            (!selectedProduct.is_available || !hasStock || isReadOnly) && styles.disabledButton
          ]}
          onPress={handleAddToCart}
          disabled={!selectedProduct.is_available || !hasStock || isAddingToCart}
          activeOpacity={0.8}
        >
          {isAddingToCart ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <View style={styles.addToCartContent}>
              <MaterialIcons 
                name={isReadOnly ? "cloud-off" : (selectedProduct.is_available && hasStock ? "shopping-cart" : "block")} 
                size={24} 
                color="#FFFFFF" 
              />
              <Text style={styles.addToCartText}>
                {isReadOnly 
                  ? 'Mode lecture seule'
                  : (selectedProduct.is_available && hasStock ? 'Ajouter au panier' : 'Indisponible')}
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
    </View>
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
  scrollView: {
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
    height: Dimensions.get('window').width, // Image carrée basée sur la largeur
    position: 'relative',
    backgroundColor: '#FFFFFF',
  },
  carouselImage: {
    width: Dimensions.get('window').width,
    height: Dimensions.get('window').width,
  },
  paginationContainer: {
    position: 'absolute',
    bottom: 16,
    flexDirection: 'row',
    alignSelf: 'center',
    backgroundColor: 'rgba(0,0,0,0.1)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  paginationDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: 'rgba(0,0,0,0.2)',
    marginHorizontal: 4,
  },
  paginationDotActive: {
    backgroundColor: COLORS.PRIMARY,
    width: 16,
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
  mainContent: {
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
  categoryContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  category: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.SECONDARY,
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
    flexWrap: 'wrap',
    marginBottom: 8,
  },
  price: {
    fontSize: 32,
    fontWeight: '900',
    color: COLORS.DANGER,
    letterSpacing: -0.5,
  },
  priceUnit: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.TEXT_SECONDARY,
    marginLeft: 6,
  },
  discountPrice: {
    fontSize: 32,
    fontWeight: '900',
    color: COLORS.DANGER,
    letterSpacing: -0.5,
    marginBottom: 4,
  },
  oldPrice: {
    fontSize: 20,
    color: COLORS.TEXT_SECONDARY,
    textDecorationLine: 'line-through',
    fontWeight: '600',
    marginBottom: 8,
  },
  discountTag: {
    backgroundColor: COLORS.DANGER,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6,
    marginTop: 4,
    alignSelf: 'flex-start',
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
  quantityUnit: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.TEXT_SECONDARY,
    marginTop: 2,
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
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: COLORS.TEXT,
    marginLeft: 8,
  },
  descriptionContainer: {
    backgroundColor: '#FAFAFA',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#F3F4F6',
  },
  description: {
    fontSize: 16,
    color: COLORS.TEXT,
    lineHeight: 26,
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
