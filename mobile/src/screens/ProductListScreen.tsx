import React, { useEffect, useState, useRef, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
  RefreshControl,
  ActivityIndicator,
  SafeAreaView,
  ScrollView,
  Dimensions,
  Keyboard,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchProducts, fetchCategories, setSearchQuery, setFilters, clearFilters } from '../store/slices/productSlice';
import { useNavigation, useRoute, useFocusEffect } from '@react-navigation/native';
import { formatPrice } from '../utils/helpers';
import { COLORS } from '../utils/constants';
import { Product, Category } from '../types';
import DynamicProductCard from '../components/DynamicProductCard';
import { Header } from '../components/Header';
import { LoadingScreen } from '../components/LoadingScreen';
import SearchModal from '../components/SearchModal';

const ProductListScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigation = useNavigation();
  const route = useRoute();
  const { products, categories, isLoading, searchQuery, filters, pagination } = useAppSelector(
    (state) => state.product
  );
  const [refreshing, setRefreshing] = useState(false);
  const [searchModalVisible, setSearchModalVisible] = useState(false);
  const categoriesScrollRef = useRef<ScrollView>(null);

  // Fermer le modal de recherche quand l'écran redevient actif
  useFocusEffect(
    useCallback(() => {
      setSearchModalVisible(false);
      Keyboard.dismiss();
    }, [])
  );

  useEffect(() => {
    const params = (route.params as any) || {};
    const categoryId = params.categoryId;
    const isPromo = params.promo === true;
    
    if (categoryId) {
      dispatch(setFilters({ category: categoryId }));
    }
    
    // Si c'est la page promo, charger tous les produits pour filtrer côté client
    if (isPromo) {
      dispatch(clearFilters());
      dispatch(fetchProducts({ page: 1, search: '', filters: {} }));
    }
  }, [dispatch, route]);

  useEffect(() => {
    const isPromo = (route.params as any)?.promo === true;
    // Ne pas recharger si on est en mode promo (on filtre côté client)
    if (!isPromo) {
      dispatch(fetchProducts({ page: 1, search: searchQuery, filters }));
    }
    dispatch(fetchCategories());
  }, [dispatch, searchQuery, filters, route]);

  const onRefresh = async () => {
    setRefreshing(true);
    await dispatch(fetchProducts({ page: 1, search: searchQuery, filters }));
    setRefreshing(false);
  };

  const handleSearch = (text: string) => {
    dispatch(setSearchQuery(text));
    dispatch(fetchProducts({ page: 1, search: text, filters }));
  };

  const handleSearchFocus = () => {
    setSearchModalVisible(true);
  };

  const clearSearch = () => {
    dispatch(setSearchQuery(''));
    dispatch(clearFilters());
    dispatch(fetchProducts({ page: 1, search: '', filters }));
  };

  const loadMore = () => {
    if (pagination.hasNext && !isLoading) {
      dispatch(fetchProducts({ page: pagination.page + 1, search: searchQuery, filters }));
    }
  };

  // Log pour debug
  console.log('[ProductListScreen] 📊 Total produits reçus:', (products || []).length);
  console.log('[ProductListScreen] 📊 Total catégories reçues:', (categories || []).length);

  // Vérifier si on est en mode promo
  const isPromo = (route.params as any)?.promo === true;
  
  // Tous les produits visibles viennent déjà de l'API B2B côté backend
  const filteredProducts = products || [];
  
  // Filtrer les produits en promotion si nécessaire
  const displayProducts = isPromo
    ? filteredProducts.filter((p: Product) => 
        p.discount_price && p.discount_price < p.price && p.discount_price > 0
      )
    : filteredProducts;

  // Trouver la catégorie sélectionnée
  const selectedCategory = filters.category 
    ? (categories || []).find((c: Category) => c.id === filters.category)
    : null;

  // Afficher les catégories principales, et ajouter la sous-catégorie sélectionnée si elle existe
  const mainCategories = (categories || []).filter((c: Category) => !c.parent).slice(0, 8);
  
  let displayCategories: Category[] = [...mainCategories];
  
  // Si une sous-catégorie est sélectionnée, l'ajouter à la liste (ou remplacer son parent si présent)
  if (selectedCategory && selectedCategory.parent) {
    // Vérifier si le parent est déjà dans la liste
    const parentIndex = displayCategories.findIndex((c: Category) => c.id === selectedCategory.parent);
    if (parentIndex !== -1) {
      // Remplacer le parent par la sous-catégorie
      displayCategories[parentIndex] = selectedCategory;
    } else {
      // Ajouter la sous-catégorie à la fin
      displayCategories.push(selectedCategory);
    }
  }

  // La catégorie à mettre en focus est directement celle sélectionnée
  const categoryToFocus = filters.category;

  // Défilement automatique vers la catégorie sélectionnée
  useEffect(() => {
    if (categoryToFocus && categoriesScrollRef.current) {
      const selectedIndex = displayCategories.findIndex((c: Category) => c.id === categoryToFocus);
      if (selectedIndex !== -1) {
        // Calculer la position approximative
        // Largeur d'une carte: ~88px (80px minWidth + 8px marginRight)
        const cardWidth = 88;
        const screenWidth = Dimensions.get('window').width;
        
        // Position de la catégorie sélectionnée
        const categoryX = selectedIndex * cardWidth;
        
        // Centrer la catégorie avec un offset vers la droite
        const scrollToX = categoryX - (screenWidth / 2) + (cardWidth / 2) + 40;
        
        setTimeout(() => {
          categoriesScrollRef.current?.scrollTo({
            x: Math.max(0, scrollToX),
            animated: true,
          });
        }, 100);
      }
    }
  }, [categoryToFocus, displayCategories]);

  const renderProduct = ({ item }: { item: Product }) => (
    <DynamicProductCard product={item} />
  );

  const renderFooter = () => {
    if (isLoading && products.length > 0) {
      return (
        <View style={styles.footerLoader}>
          <ActivityIndicator size="small" color={COLORS.PRIMARY} />
          <Text style={styles.footerText}>Chargement...</Text>
        </View>
      );
    }
    if (pagination.hasNext && products.length > 0) {
      return (
        <View style={styles.footerLoader}>
          <Text style={styles.footerText}>Charger plus</Text>
        </View>
      );
    }
    return null;
  };

  const renderEmpty = () => {
    const isPromo = (route.params as any)?.promo === true;
    return (
      <View style={styles.emptyContainer}>
        <MaterialIcons name="inventory" size={64} color={COLORS.TEXT_SECONDARY} />
        <Text style={styles.emptyTitle}>Aucun produit trouvé</Text>
        <Text style={styles.emptyText}>
          {isPromo
            ? 'Aucun produit en promotion pour le moment'
            : searchQuery 
              ? `Aucun résultat pour "${searchQuery}"` 
              : 'Essayez de modifier vos filtres ou de rechercher autre chose'}
        </Text>
        {searchQuery && (
          <TouchableOpacity
            style={styles.clearSearchButton}
            onPress={clearSearch}
          >
            <Text style={styles.clearSearchText}>Effacer la recherche</Text>
          </TouchableOpacity>
        )}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.headerFixedContainer}>
        <Header
          searchQuery={searchQuery}
          onSearchChange={handleSearch}
          onClearSearch={clearSearch}
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
          {/* Section Catégories */}
          <View style={styles.categoriesSection}>
        <ScrollView 
          ref={categoriesScrollRef}
          horizontal 
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.categoriesScrollContent}
          nestedScrollEnabled={true}
        >
          {displayCategories.length > 0 ? (
            displayCategories.map((category: Category) => {
              // Mettre en focus si c'est la catégorie sélectionnée
              const isSelected = filters.category === category.id;
              return (
                <TouchableOpacity
                  key={category.id}
                  style={[
                    styles.categoryCard,
                    isSelected && styles.categoryCardActive
                  ]}
                  onPress={() => {
                    console.log(
                      'PRODUCT_LIST / clic catégorie horizontale :',
                      category.id,
                      category.slug,
                      category.name
                    );
                    dispatch(setFilters({ category: category.id }));
                    dispatch(
                      fetchProducts({
                        page: 1,
                        search: searchQuery,
                        filters: { ...filters, category: category.id },
                      })
                    );
                  }}
                >
                  <Text style={[
                    styles.categoryName,
                    isSelected && styles.categoryNameActive
                  ]}>
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

      {isLoading && products.length === 0 ? (
        <LoadingScreen />
      ) : (
        <FlatList
          data={displayProducts}
          renderItem={renderProduct}
          keyExtractor={(item) => item.id.toString()}
          numColumns={2}
          contentContainerStyle={[
            styles.list,
            displayProducts.length === 0 && styles.listEmpty
          ]}
          refreshControl={
            <RefreshControl 
              refreshing={refreshing} 
              onRefresh={onRefresh}
              colors={[COLORS.PRIMARY]}
              tintColor={COLORS.PRIMARY}
            />
          }
          onEndReached={loadMore}
          onEndReachedThreshold={0.5}
          ListFooterComponent={renderFooter}
          ListEmptyComponent={renderEmpty}
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
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 5,
    zIndex: 10,
  },
  categoriesSection: {
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 8,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  categoriesScrollContent: {
    paddingLeft: 0,
    paddingRight: 20,
  },
  categoryCard: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    minWidth: 80,
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
  categoryName: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.TEXT,
    textAlign: 'center',
  },
  categoryCardActive: {
    backgroundColor: COLORS.PRIMARY,
    borderColor: COLORS.PRIMARY,
  },
  categoryNameActive: {
    color: '#FFFFFF',
  },
  list: {
    padding: 12,
    paddingBottom: 24,
  },
  listEmpty: {
    flexGrow: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.BACKGROUND,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: COLORS.TEXT_SECONDARY,
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
    minHeight: 400,
  },
  emptyTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: COLORS.TEXT,
    marginTop: 24,
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 16,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 24,
  },
  clearSearchButton: {
    backgroundColor: COLORS.PRIMARY,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    marginTop: 8,
  },
  clearSearchText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  footerLoader: {
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  footerText: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
    marginTop: 8,
    fontWeight: '600',
  },
});

export default ProductListScreen;
