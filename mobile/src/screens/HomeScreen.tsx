import React, { useEffect, useState, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  SafeAreaView,
  StatusBar,
  FlatList,
  ActivityIndicator,
  Keyboard,
} from 'react-native';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import { Image } from 'expo-image';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchProducts, fetchCategories, setSearchQuery, searchProducts, clearFilters, setFilters } from '../store/slices/productSlice';
import { useNavigation, NavigationProp, useFocusEffect } from '@react-navigation/native';
import { HomeScreenNavigationProp } from '../types/navigation';
import { formatPrice, getProductImageUrl } from '../utils/helpers';
import { COLORS, API_ENDPOINTS } from '../utils/constants';
import { Product, Category } from '../types';
import { Header } from '../components/Header';
import { LoadingScreen } from '../components/LoadingScreen';
import ProductCardInfo from '../components/ProductCardInfo';
import SearchModal from '../components/SearchModal';
import apiClient from '../services/api';
import { mapProductFromBackend } from '../utils/mappers';
import ProductImage from '../components/ProductImage';
import HomeInfoCarousel from '../components/HomeInfoCarousel';
import HomeProductSection from '../components/HomeProductSection';

const HomeScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigation = useNavigation<HomeScreenNavigationProp>();
  const { products, categories, isLoading, isFetchingMore, pagination, searchQuery } = useAppSelector((state) => state.product);
  const [refreshing, setRefreshing] = React.useState(false);
  const [searchModalVisible, setSearchModalVisible] = useState(false);
  const [homePromoProducts, setHomePromoProducts] = useState<Product[]>([]);
  const [homeNewProducts, setHomeNewProducts] = useState<Product[]>([]);
  
  // États pour stocker les produits par catégorie (comme sur le web)
  const [phoneProducts, setPhoneProducts] = useState<Product[]>([]);
  const [clothingProducts, setClothingProducts] = useState<Product[]>([]);
  const [fabricProducts, setFabricProducts] = useState<Product[]>([]);
  const [culturalProducts, setCulturalProducts] = useState<Product[]>([]);

  useEffect(() => {
    // Charger les produits et catégories au montage
    dispatch(fetchProducts({ page: 1, filters: {} }));
    dispatch(fetchCategories({ forceRefresh: true }));
  }, [dispatch]);

  useEffect(() => {
    if (!products || products.length === 0) return;
    const urls = products
      .slice(0, 12)
      .map((p: Product) => getProductImageUrl(p))
      .filter((u): u is string => !!u);
    const unique = Array.from(new Set(urls));
    unique.forEach((url) => {
      Image.prefetch(url);
    });
  }, [products]);

  // Fermer le modal de recherche quand l'écran redevient actif
  useFocusEffect(
    useCallback(() => {
      setSearchModalVisible(false);
      Keyboard.dismiss();
    }, [])
  );


  // Charger les produits par TYPE (Exactement comme sur le Web avec filtres API)
  // Utilise les mêmes filtres que le web : has_phone, has_clothing, has_fabric, has_cultural
  useEffect(() => {
    const loadProductsByType = async () => {
      try {
        // Chargement des produits par section
        
        // Faire 4 appels API en parallèle avec les filtres spécifiques (comme sur le web)
        const [phonesRes, clothingRes, fabricsRes, culturalRes] = await Promise.all([
          apiClient.get(`${API_ENDPOINTS.PRODUCTS}?is_available=true&has_phone=true&ordering=-created_at&page_size=8`),
          apiClient.get(`${API_ENDPOINTS.PRODUCTS}?is_available=true&has_clothing=true&ordering=-created_at&page_size=8`),
          apiClient.get(`${API_ENDPOINTS.PRODUCTS}?is_available=true&has_fabric=true&ordering=-created_at&page_size=8`),
          apiClient.get(`${API_ENDPOINTS.PRODUCTS}?is_available=true&has_cultural=true&ordering=-created_at&page_size=8`)
        ]);

        // Mapper les produits avec gestion d'erreur
        const mapProductsSafely = (products: any[]): Product[] => {
          return products
            .map((p: any) => {
              try {
                return mapProductFromBackend(p);
              } catch (error) {
                // Ignorer les erreurs de mapping silencieusement
                return null;
              }
            })
            .filter((p): p is Product => p !== null);
        };

        const allPhones = mapProductsSafely(phonesRes.data.results || phonesRes.data || []);
        const allClothing = mapProductsSafely(clothingRes.data.results || clothingRes.data || []);
        const allFabrics = mapProductsSafely(fabricsRes.data.results || fabricsRes.data || []);
        const allCultural = mapProductsSafely(culturalRes.data.results || culturalRes.data || []);

        // Tous les produits sont B2B maintenant, pas besoin de filtrer
        const phones = allPhones;
        const clothing = allClothing;
        const fabrics = allFabrics;
        const cultural = allCultural;

        // Log silencieux - données chargées

        setPhoneProducts(phones);
        setClothingProducts(clothing);
        setFabricProducts(fabrics);
        setCulturalProducts(cultural);
      } catch (error) {
        // Erreur silencieuse - utiliser le cache si disponible
      }
    };

    loadProductsByType();
  }, [dispatch, categories]);

  // Réinitialiser les filtres chaque fois que l'écran est affiché
  useFocusEffect(
    React.useCallback(() => {
      dispatch(clearFilters());
      dispatch(fetchProducts({ page: 1, filters: {} }));
    }, [dispatch])
  );

  const onRefresh = React.useCallback(async () => {
    setRefreshing(true);
    dispatch(clearFilters());
    await Promise.all([
      dispatch(fetchProducts({ page: 1, filters: {} })),
      dispatch(fetchCategories({ forceRefresh: true })),
    ]);
    
    // Recharger les produits par type (Exactement comme sur le Web)
    try {
      const [phonesRes, clothingRes, fabricsRes, culturalRes] = await Promise.all([
        apiClient.get(`${API_ENDPOINTS.PRODUCTS}?is_available=true&has_phone=true&ordering=-created_at&page_size=8`),
        apiClient.get(`${API_ENDPOINTS.PRODUCTS}?is_available=true&has_clothing=true&ordering=-created_at&page_size=8`),
        apiClient.get(`${API_ENDPOINTS.PRODUCTS}?is_available=true&has_fabric=true&ordering=-created_at&page_size=8`),
        apiClient.get(`${API_ENDPOINTS.PRODUCTS}?is_available=true&has_cultural=true&ordering=-created_at&page_size=8`)
      ]);
      
      // Mapper les produits avec gestion d'erreur
      const mapProductsSafely = (products: any[]): Product[] => {
        return products
          .map((p: any) => {
            try {
              return mapProductFromBackend(p);
            } catch (error) {
              console.error('HOME / Erreur mapping produit:', error, p);
              return null;
            }
          })
          .filter((p): p is Product => p !== null);
      };

        // Les produits retournés par l'API sont déjà filtrés pour ne garder que ceux dans des catégories B2B
        // (filtrés côté backend dans ProductViewSet.get_queryset())
        setPhoneProducts(mapProductsSafely(phonesRes.data.results || phonesRes.data || []));
        setClothingProducts(mapProductsSafely(clothingRes.data.results || clothingRes.data || []));
        setFabricProducts(mapProductsSafely(fabricsRes.data.results || fabricsRes.data || []));
        setCulturalProducts(mapProductsSafely(culturalRes.data.results || culturalRes.data || []));
    } catch (error: any) {
      if (error.code !== 'OFFLINE_MODE_FORCED' && error.message !== 'OFFLINE_MODE_FORCED') {
        // Erreur refresh silencieuse
      }
    }
    
    setRefreshing(false);
  }, [dispatch]);

  const handleSearch = (text: string) => {
    dispatch(setSearchQuery(text));
    // Si le modal n'est pas ouvert, l'ouvrir automatiquement
    if (!searchModalVisible && text.trim().length > 0) {
      setSearchModalVisible(true);
    }
    // Déclencher la recherche avec debounce
    if (text.trim()) {
      dispatch(searchProducts(text));
    } else {
      dispatch(clearFilters());
      dispatch(fetchProducts({ page: 1, filters: {} }));
    }
  };

  const handleSearchFocus = () => {
    setSearchModalVisible(true);
  };

  useEffect(() => {
    if (!products || products.length === 0) return;
    if (pagination.page !== 1) return;

    const trending = products.filter((p: Product) => p.is_trending).slice(0, 6);
    const promo = products.filter((p: Product) => {
      return p.discount_price && p.discount_price < p.price && p.discount_price > 0;
    });
    const displayPromo = promo.length > 0
      ? promo.slice(0, 10)
      : (trending.length > 0 ? trending.slice(0, 10) : products.slice(0, Math.min(10, products.length)));

    const newOnes = [...products]
      .filter((p: Product) => p.created_at)
      .sort(
        (a: Product, b: Product) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
      .slice(0, 8);

    setHomePromoProducts(displayPromo.slice(0, 8));
    setHomeNewProducts(newOnes);
  }, [products, pagination.page]);
  
  // Catégories B2B (même logique que CategoryScreen)
  const b2bCategories = useMemo(() => {
    return (categories || []).filter((c: Category) =>
      (c.rayon_type !== null && c.rayon_type !== undefined) ||
      (c.level !== null && c.level !== undefined)
    );
  }, [categories]);

  // Catégories de niveau 0 uniquement, triées
  const level0Categories = useMemo(() => {
    const level0 = b2bCategories.filter((c: Category) =>
      c.level === 0 || (c.level === null && !c.parent)
    );

    return level0.sort((a: Category, b: Category) => {
      if (a.order !== b.order) {
        return a.order - b.order;
      }
      return a.name.localeCompare(b.name);
    });
  }, [b2bCategories]);

  // S'assurer qu'on a toujours quelque chose à afficher
  const displayCategories = level0Categories;

  // Helpers de catégorisation (même logique que DynamicProductCard)
  const findCategoryWithParents = (categoryId: number, allCategories: Category[]): Category | null => {
    const category = allCategories.find((cat) => cat.id === categoryId);
    return category || null;
  };

  const isCategoryOrParent = (
    category: Category | null,
    targetSlugs: string[],
    allCategories: Category[]
  ): boolean => {
    if (!category) return false;

    if (targetSlugs.includes(category.slug)) {
      return true;
    }

    if (category.parent) {
      const parentCategory = findCategoryWithParents(category.parent, allCategories);
      if (parentCategory && isCategoryOrParent(parentCategory, targetSlugs, allCategories)) {
        return true;
      }
    }

    return false;
  };

  // Les produits par catégorie sont maintenant chargés via des requêtes séparées (voir useEffect ci-dessus)


  const handleClearSearch = () => {
    dispatch(setSearchQuery(''));
    dispatch(clearFilters());
    dispatch(fetchProducts({ page: 1, filters: {} }));
  };

  const handleLoadMore = () => {
    if (!isLoading && !isFetchingMore && pagination.hasNext) {
      dispatch(fetchProducts({ 
        page: pagination.page + 1, 
        filters: {}, 
        append: true 
      }));
    }
  };


  const renderProductItem = ({ item }: { item: Product }) => {
    const imageUrl = getProductImageUrl(item);
    return (
    <TouchableOpacity
      key={item.id}
      style={styles.gridProductCard}
      onPress={() => navigation.navigate('Products', { screen: 'ProductDetail', params: { slug: item.slug } })}
    >
      <View style={styles.gridProductImageContainer}>
        <ProductImage
          uri={imageUrl}
          style={styles.gridProductImage}
          resizeMode="cover"
          fallback={
            <View style={styles.gridProductImageFallback}>
              <MaterialIcons name="image-not-supported" size={40} color={COLORS.TEXT_SECONDARY} />
            </View>
          }
        />
        {item.discount_price && item.discount_price < item.price && (
          <View style={styles.gridProductBadge}>
            <Text style={styles.gridProductBadgeText}>
              -{Math.round(((item.price - item.discount_price) / item.price) * 100)}%
            </Text>
          </View>
        )}
      </View>
      <View style={styles.gridProductInfo}>
        <Text style={styles.gridProductTitle} numberOfLines={2}>{item.title}</Text>
        <View style={styles.gridProductPriceContainer}>
          <Text style={styles.gridProductPrice}>
            {formatPrice(item.discount_price || item.price)}
          </Text>
          {item.discount_price && item.discount_price < item.price && (
            <Text style={styles.gridProductOldPrice}>{formatPrice(item.price)}</Text>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );
  };

  const headerContent = useMemo(() => (
    <>
      {/* Catégories (Défilent avec le contenu) */}
      <View style={styles.categoriesSection}>
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.categoriesScrollContent}
          nestedScrollEnabled={true}
        >
          {displayCategories.length > 0 ? (
            displayCategories.map((category: Category) => {
              return (
                <TouchableOpacity
                  key={category.id}
                  style={styles.categoryCard}
                  onPress={() => navigation.navigate('Products', {
                    screen: 'ProductList',
                    params: { categoryId: category.id },
                  })}
                >
                  <Text style={styles.categoryName} numberOfLines={1} ellipsizeMode="tail">
                    {category.name || `Catégorie ${category.id}`}
                  </Text>
                </TouchableOpacity>
              );
            })
          ) : (
            <View style={styles.categoryCard}>
              <Text style={styles.categoryName}>Chargement...</Text>
            </View>
          )}
        </ScrollView>
      </View>

      {/* Section combinée : Cartes d'informations */}
      <HomeInfoCarousel />

      {/* Section Promo - Carrousel */}
      {homePromoProducts.length > 0 && (
        <HomeProductSection
          title="Promo Flash"
          subtitle="Économie"
          iconName="local-offer"
          iconColor={COLORS.DANGER}
          products={homePromoProducts}
          showSeeAll={homePromoProducts.length > 5}
          onPressSeeAll={() => navigation.navigate('Products', { screen: 'ProductList', params: { promo: true } })}
          onPressProduct={(product) => navigation.navigate('Products', { screen: 'ProductDetail', params: { slug: product.slug } })}
        />
      )}

      {/* Section Nouveaux produits */}
      {homeNewProducts.length > 0 && (
        <HomeProductSection
          title="Nouveaux"
          subtitle="Produits"
          iconName="new-releases"
          iconColor={COLORS.PRIMARY}
          products={homeNewProducts}
          showNewBadge={true}
          onPressProduct={(product) => navigation.navigate('Products', { screen: 'ProductDetail', params: { slug: product.slug } })}
        />
      )}

      {/* Section Téléphones */}
      {phoneProducts.length > 0 && (
        <View style={styles.promoSection}>
          <View style={styles.promoHeaderInline}>
            <View style={styles.promoHeaderIconContainer}>
              <MaterialIcons name="phone-android" size={20} color={COLORS.PRIMARY} />
            </View>
            <View style={styles.promoHeaderTextContainer}>
              <Text style={styles.promoSectionTitleInline}>Nos téléphones</Text>
              <Text style={styles.promoSectionSubtitleInline}>Mobiles & smartphones</Text>
            </View>
          </View>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.promoCarouselContent}
            snapToInterval={156}
            decelerationRate="fast"
            snapToAlignment="start"
            pagingEnabled={false}
          >
            {phoneProducts.map((product: Product) => (
              <React.Fragment key={product.id}>
                {(
                  <TouchableOpacity
                    style={styles.promoCard}
                    onPress={() => navigation.navigate('Products', { screen: 'ProductDetail', params: { slug: product.slug } })}
                    activeOpacity={0.8}
                  >
                    <View style={styles.promoImageContainer}>
                      <ProductImage
                        uri={getProductImageUrl(product)}
                        style={styles.promoImage}
                        resizeMode="cover"
                        fallback={
                          <View style={styles.promoImageFallback}>
                            <MaterialIcons name="image-not-supported" size={48} color={COLORS.TEXT_SECONDARY} />
                          </View>
                        }
                      />
                    </View>
                    <View style={styles.promoCardContent}>
                      <Text style={styles.promoProductTitle} numberOfLines={1}>{product.title}</Text>
                      <ProductCardInfo product={product} showBrand={true} showSpecs={false} compact={true} />
                      <View style={styles.promoPriceContainer}>
                        <View style={styles.promoPriceRow}>
                          <Text style={styles.promoNewPrice}>{formatPrice(product.discount_price || product.price)}</Text>
                          {product.is_salam && (
                            <View style={styles.salamBadge}>
                              <Text style={styles.salamBadgeText}>SALAM</Text>
                            </View>
                          )}
                        </View>
                      </View>
                    </View>
                  </TouchableOpacity>
                )}
              </React.Fragment>
            ))}
          </ScrollView>
        </View>
      )}

      {/* Titre pour "Autres produits" */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Découvrez d'autres produits</Text>
      </View>
    </>
  ), [displayCategories, homePromoProducts, homeNewProducts, phoneProducts, navigation]);

  const renderFooter = () => {
    if (!isFetchingMore) return <View style={{ height: 20 }} />;
    return (
      <View style={styles.loaderFooter}>
        <ActivityIndicator size="small" color={COLORS.PRIMARY} />
        <Text style={styles.loaderText}>Chargement de plus de produits...</Text>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      
      {/* Header Fixe */}
      <View style={styles.headerFixedContainer}>
        <Header
          searchQuery={searchQuery}
          onSearchChange={handleSearch}
          onClearSearch={handleClearSearch}
          openSearchModal={handleSearchFocus}
        />
      </View>

      {/* Modal de recherche - remplace le contenu */}
      {searchModalVisible ? (
        <SearchModal
          visible={searchModalVisible}
          onClose={() => {
            Keyboard.dismiss();
            setSearchModalVisible(false);
          }}
          initialQuery={searchQuery}
        />
      ) : (
        <>
          {isLoading && products.length === 0 ? (
            <LoadingScreen />
          ) : (
            <FlatList
              data={products}
              renderItem={renderProductItem}
              keyExtractor={(item) => item.id.toString()}
              ListHeaderComponent={headerContent}
              ListFooterComponent={renderFooter}
              onEndReached={handleLoadMore}
              onEndReachedThreshold={0.5}
              refreshControl={
                <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
              }
              numColumns={2}
              columnWrapperStyle={styles.columnWrapper}
              contentContainerStyle={styles.flatListContent}
              showsVerticalScrollIndicator={false}
            />
          )}
        </>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.BACKGROUND,
  },
  headerFixedContainer: {
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 5,
    zIndex: 10,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingTop: 0,
  },
  categoriesSection: {
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 8,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  categoriesContainer: {
    marginTop: 8,
    minHeight: 44,
    paddingLeft: 0,
    paddingVertical: 4,
  },
  categoriesScrollContent: {
    paddingLeft: 0,
    paddingRight: 12,
  },
  categoryCard: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 20,
    marginRight: 6,
    minWidth: 72,
    maxWidth: 160,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 2,
    elevation: 1,
  },
  exploreCard: {
    backgroundColor: '#10B981',
    borderColor: '#10B981',
    marginRight: 6,
    paddingHorizontal: 10,
  },
  categoryName: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.TEXT,
    textAlign: 'center',
    flexShrink: 1,
  },
  exploreCardText: {
    color: '#FFFFFF',
  },
  section: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 12,
  },
  productCard: {
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
  productImage: {
    width: 80,
    height: 80,
    borderRadius: 8,
    marginRight: 12,
  },
  productInfo: {
    flex: 1,
    justifyContent: 'center',
  },
  productTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 4,
  },
  productPriceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  productPrice: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.DANGER,
  },
  productOldPrice: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
    textDecorationLine: 'line-through',
    fontWeight: '500',
  },
  promoSection: {
    paddingBottom: 2,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
  },
  promoHeaderInline: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: '#F9FAFB',
    borderRadius: 6,
    paddingVertical: 4,
    paddingHorizontal: 6,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    justifyContent: 'flex-start',
  },
  promoHeaderTextContainer: {
    flex: 1,
    marginLeft: 2,
  },
  promoSectionTitleInline: {
    fontSize: 14,
    fontWeight: '800',
    color: COLORS.TEXT,
    letterSpacing: -0.2,
    marginBottom: 1,
  },
  promoSectionSubtitleInline: {
    fontSize: 9,
    fontWeight: '600',
    color: COLORS.TEXT_SECONDARY,
    marginTop: 0,
  },
  promoSeeAllButtonInline: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 2,
  },
  promoSeeAllTextInline: {
    fontSize: 11,
    fontWeight: '700',
    color: COLORS.PRIMARY,
    marginRight: 2,
  },
  promoHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginBottom: 12,
  },
  promoHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  promoHeaderIconContainer: {
    width: 36,
    height: 36,
    borderRadius: 8,
    backgroundColor: '#FEE2E2',
    justifyContent: 'center',
    alignItems: 'center',
  },
  promoSectionTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: COLORS.TEXT,
    letterSpacing: -0.5,
    marginBottom: 2,
  },
  promoSectionSubtitle: {
    fontSize: 11,
    color: COLORS.TEXT_SECONDARY,
    fontWeight: '500',
  },
  promoSeeAllButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 6,
    backgroundColor: '#F0FDF4',
    borderRadius: 16,
    borderWidth: 1.5,
    borderColor: COLORS.PRIMARY,
  },
  promoSeeAllText: {
    fontSize: 12,
    fontWeight: '700',
    color: COLORS.PRIMARY,
    marginRight: 4,
  },
  promoCarouselContent: {
    paddingLeft: 8,
    paddingRight: 8,
    paddingBottom: 2,
    alignItems: 'flex-start',
  },
  promoCard: {
    width: 150,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginRight: 6,
    overflow: 'hidden',
    position: 'relative',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 3,
    borderWidth: 0,
    borderColor: 'transparent',
  },
  promoImageContainer: {
    width: '100%',
    height: 140,
    position: 'relative',
    backgroundColor: '#F9FAFB',
  },
  promoImage: {
    width: '100%',
    height: '100%',
  },
  promoImageFallback: {
    width: '100%',
    height: '100%',
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  promoBadge: {
    position: 'absolute',
    top: 6,
    right: 6,
    zIndex: 10,
    alignItems: 'center',
  },
  promoBadgeInner: {
    backgroundColor: COLORS.DANGER,
    paddingHorizontal: 6,
    paddingVertical: 4,
    borderRadius: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 3,
    elevation: 4,
  },
  promoBadgeTriangle: {
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
  promoBadgeText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '900',
    letterSpacing: 0.5,
  },
  promoCardContent: {
    padding: 4,
    paddingTop: 4,
    backgroundColor: '#FFFFFF',
  },
  promoProductTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: COLORS.TEXT,
    marginBottom: 2,
    lineHeight: 14,
    minHeight: 14,
  },
  promoPriceContainer: {
    marginBottom: 2,
  },
  promoPriceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 0,
  },
  promoNewPrice: {
    fontSize: 17, // Réduit de 18 à 17
    fontWeight: '900',
    color: COLORS.DANGER, // Changé de PRIMARY (vert) à DANGER (rouge)
    letterSpacing: -0.3,
  },
  promoOldPrice: {
    fontSize: 11, // Réduit de 13 à 11
    color: '#9CA3AF',
    textDecorationLine: 'line-through',
    fontWeight: '600',
  },
  salamBadge: {
    backgroundColor: COLORS.SECONDARY,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  salamBadgeText: {
    color: '#FFFFFF',
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  newBadge: {
    position: 'absolute',
    top: 6,
    left: 6,
    backgroundColor: COLORS.PRIMARY,
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 6,
    zIndex: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 3,
    elevation: 4,
  },
  newBadgeText: {
    color: '#FFFFFF',
    fontSize: 8,
    fontWeight: '900',
    letterSpacing: 0.5,
  },
  stockIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 2,
    paddingTop: 4,
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
  },
  stockDot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: COLORS.WARNING,
    marginRight: 4,
  },
  stockText: {
    fontSize: 11,
    color: COLORS.WARNING,
    fontWeight: '600',
  },
  promoSeeMoreCard: {
    width: 150,
    height: 200,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginRight: 6,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1.5,
    borderColor: COLORS.PRIMARY,
    borderStyle: 'dashed',
    shadowColor: COLORS.PRIMARY,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 2,
  },
  promoSeeMoreContent: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 12,
  },
  promoSeeMoreIconContainer: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#F0FDF4',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 6,
    borderWidth: 1.5,
    borderColor: COLORS.PRIMARY,
  },
  promoSeeMoreText: {
    fontSize: 12,
    fontWeight: '800',
    color: COLORS.PRIMARY,
    marginBottom: 2,
    textAlign: 'center',
  },
  promoSeeMoreCount: {
    fontSize: 11, // Réduit de 12 à 11
    color: COLORS.TEXT_SECONDARY,
    fontWeight: '600',
    textAlign: 'center',
  },
  promoSeeMoreButtonContainer: {
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 8,
    alignItems: 'center',
  },
  promoSeeMoreButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F0FDF4',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12,
    borderWidth: 1.5,
    borderColor: COLORS.PRIMARY,
    gap: 8,
  },
  promoSeeMoreButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.PRIMARY,
  },
  categorySectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginBottom: 12,
  },
  categorySectionHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  categorySectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: COLORS.TEXT,
  },
  categorySeeAllButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#F0FDF4',
    borderRadius: 16,
    borderWidth: 1.5,
    borderColor: COLORS.PRIMARY,
    gap: 4,
  },
  categorySeeAllText: {
    fontSize: 12,
    fontWeight: '700',
    color: COLORS.PRIMARY,
  },
  flatListContent: {
    paddingBottom: 20,
  },
  columnWrapper: {
    justifyContent: 'space-between',
    paddingHorizontal: 16,
  },
  sectionHeader: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: '#FFFFFF',
    marginTop: 8,
  },
  gridProductCard: {
    width: '48%',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    overflow: 'hidden',
  },
  gridProductImageContainer: {
    width: '100%',
    height: 160,
    backgroundColor: '#F9FAFB',
  },
  gridProductImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  gridProductImageFallback: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
  },
  gridProductBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: COLORS.DANGER,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  gridProductBadgeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: 'bold',
  },
  gridProductInfo: {
    padding: 10,
  },
  gridProductTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 6,
    height: 36,
  },
  gridProductPriceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 4,
  },
  gridProductPrice: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.DANGER,
  },
  gridProductOldPrice: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
    textDecorationLine: 'line-through',
  },
  loaderFooter: {
    paddingVertical: 20,
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 10,
  },
  loaderText: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
    fontWeight: '500',
  },
});

export default HomeScreen;
