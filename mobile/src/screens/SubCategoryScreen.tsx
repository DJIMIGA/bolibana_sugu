import React, { useEffect, useMemo, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  RefreshControl,
  Dimensions,
  SafeAreaView,
  Keyboard,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchCategories, setFilters, setSearchQuery, searchProducts, fetchProducts, clearFilters } from '../store/slices/productSlice';
import { useNavigation, useRoute, useFocusEffect } from '@react-navigation/native';
import { COLORS } from '../utils/constants';
import { Category } from '../types';
import { Header } from '../components/Header';
import { LoadingScreen } from '../components/LoadingScreen';
import SearchModal from '../components/SearchModal';

const { width } = Dimensions.get('window');

const SubCategoryScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigation = useNavigation();
  const route = useRoute();
  const { categories, isLoading, searchQuery } = useAppSelector((state) => state.product);
  const [refreshing, setRefreshing] = useState(false);
  const [searchModalVisible, setSearchModalVisible] = useState(false);
  const categoryId = (route.params as any)?.categoryId;

  const handleSearch = (text: string) => {
    dispatch(setSearchQuery(text));
    if (text.trim()) {
      dispatch(searchProducts(text));
    } else {
      dispatch(clearFilters());
      dispatch(fetchProducts({ page: 1, filters: {} }));
    }
  };

  const handleClearSearch = () => {
    dispatch(setSearchQuery(''));
    dispatch(clearFilters());
    dispatch(fetchProducts({ page: 1, filters: {} }));
  };

  const handleSearchFocus = () => {
    setSearchModalVisible(true);
  };

  useEffect(() => {
    dispatch(fetchCategories());
  }, [dispatch]);

  // Fermer le modal de recherche quand l'écran redevient actif
  useFocusEffect(
    useCallback(() => {
      setSearchModalVisible(false);
      Keyboard.dismiss();
    }, [])
  );

  const onRefresh = async () => {
    setRefreshing(true);
    await dispatch(fetchCategories());
    setRefreshing(false);
  };

  const getCategoryColor = (color: string) => {
    const colorLower = color?.toLowerCase() || '';
    const colorMap: { [key: string]: string } = {
      green: COLORS.PRIMARY, // #10B981
      yellow: COLORS.SECONDARY, // #F59E0B
      red: COLORS.DANGER, // #EF4444
      beige: COLORS.BEIGE, // #C08A5B
      terracotta: COLORS.TERRACOTTA, // #C08A5B
      brown: COLORS.BEIGE, // #C08A5B
      tan: COLORS.BEIGE, // #C08A5B
    };
    
    // Si c'est une couleur définie, la retourner
    if (colorMap[colorLower]) {
      return colorMap[colorLower];
    }
    
    // Pour toutes les autres couleurs, utiliser un cycle entre les 4 couleurs disponibles
    const allColors = [
      COLORS.PRIMARY,      // Vert
      COLORS.SECONDARY,   // Jaune
      COLORS.DANGER,      // Rouge
      COLORS.BEIGE,       // Beige/Terre cuite
    ];
    // Utiliser le hash de la couleur pour avoir une distribution cohérente
    const hash = colorLower.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return allColors[hash % allColors.length];
  };

  const getCategoryIcon = (slug: string) => {
    if (slug === 'telephones') {
      return 'phone-portrait-outline';
    } else if (slug === 'vetements') {
      return 'shirt-outline';
    } else if (slug === 'tissus') {
      return 'grid-outline';
    } else {
      return 'cube-outline';
    }
  };

  const handleCategoryPress = (categoryId: number) => {
    dispatch(setFilters({ category: categoryId }));
    navigation.navigate('Products' as never, { 
      screen: 'ProductList', 
      params: { categoryId } 
    } as never);
  };

  // Trouver la catégorie parente
  const parentCategory = useMemo(() => {
    return (categories || []).find((c: Category) => c.id === categoryId);
  }, [categories, categoryId]);

  // Construire la hiérarchie des sous-catégories
  const buildCategoryHierarchy = (
    parentCategory: Category,
    allCategories: Category[],
    currentLevel: number = 0,
    maxDepth: number = 10
  ): Category[] => {
    if (currentLevel >= maxDepth) {
      return [];
    }

    const children: Category[] = [];
    const expectedLevel = (parentCategory.level ?? 0) + 1;

    allCategories.forEach((category: Category) => {
      if (category.id === parentCategory.id) return;
      
      if (
        category.level === expectedLevel &&
        category.rayon_type === parentCategory.rayon_type
      ) {
        if (category.parent === parentCategory.id || !category.parent) {
          children.push(category);
        }
      }
    });

    children.sort((a: Category, b: Category) => {
      if (a.order !== b.order) {
        return a.order - b.order;
      }
      return a.name.localeCompare(b.name);
    });

    return children;
  };

  // Obtenir toutes les catégories B2B
  const b2bCategories = useMemo(() => {
    return (categories || []).filter((c: Category) =>
      (c.rayon_type !== null && c.rayon_type !== undefined) ||
      (c.level !== null && c.level !== undefined)
    );
  }, [categories]);

  // Obtenir les sous-catégories directes
  const directChildren = useMemo(() => {
    if (!parentCategory) return [];
    return buildCategoryHierarchy(parentCategory, b2bCategories, 0);
  }, [parentCategory, b2bCategories]);

  // Construire les niveaux imbriqués
  const nestedChildren: { [key: number]: Category[] } = useMemo(() => {
    const nested: { [key: number]: Category[] } = {};
    directChildren.forEach((child: Category) => {
      const level2 = buildCategoryHierarchy(child, b2bCategories, 1);
      if (level2.length > 0) {
        nested[child.id] = level2;
      }
    });
    return nested;
  }, [directChildren, b2bCategories]);

  if (!parentCategory) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={[styles.headerFixedContainer, styles.headerWithIdentity]}>
          <Header 
            searchQuery={searchQuery}
            onSearchChange={handleSearch}
            onClearSearch={handleClearSearch}
            openSearchModal={handleSearchFocus}
          />
        </View>
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
          <View style={styles.emptyContainer}>
            <View style={[styles.emptyIconContainer, { backgroundColor: `${COLORS.DANGER}15` }]}>
              <Ionicons name="alert-circle-outline" size={48} color={COLORS.DANGER} />
            </View>
            <Text style={styles.emptyTitle}>Catégorie introuvable</Text>
            <Text style={styles.emptyText}>La catégorie demandée n'existe pas ou n'est plus disponible</Text>
          </View>
        )}
      </SafeAreaView>
    );
  }

  const categoryColor = getCategoryColor(parentCategory.color);

  return (
    <SafeAreaView style={styles.container}>
      <View style={[styles.headerFixedContainer, styles.headerWithIdentity]}>
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
          {isLoading ? (
            <LoadingScreen />
          ) : (
            <ScrollView
              style={styles.content}
              refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
            >
          {/* En-tête de la catégorie parente */}
          <View style={[styles.parentHeader, { borderTopColor: `${categoryColor}50`, backgroundColor: `${categoryColor}05` }]}>
            <View style={[styles.parentIconContainer, { backgroundColor: `${categoryColor}15` }]}>
              {parentCategory.image ? (
                <Image source={{ uri: parentCategory.image }} style={styles.parentImage} />
              ) : (
                <Ionicons 
                  name={getCategoryIcon(parentCategory.slug) as any} 
                  size={36} 
                  color={categoryColor} 
                />
              )}
            </View>
            <View style={styles.parentContent}>
              <Text style={styles.parentName}>{parentCategory.name}</Text>
              {parentCategory.product_count !== undefined && parentCategory.product_count > 0 && (
                <View style={[styles.parentCountBadge, { backgroundColor: `${categoryColor}15` }]}>
                  <Text style={[styles.parentCount, { color: categoryColor }]}>
                    {parentCategory.product_count} produit{parentCategory.product_count > 1 ? 's' : ''}
                  </Text>
                </View>
              )}
            </View>
          </View>

          {/* Sous-catégories */}
          {directChildren.length > 0 ? (
            <View style={styles.subcategoriesGrid}>
              {directChildren.map((subcategory: Category) => {
                const subCategoryColor = getCategoryColor(subcategory.color);
                const hasNested = nestedChildren[subcategory.id]?.length > 0;

                return (
                  <View key={subcategory.id} style={styles.subcategoryCardWrapper}>
                    <TouchableOpacity
                      style={[styles.subcategoryCard, { borderTopWidth: 2, borderTopColor: `${subCategoryColor}50` }]}
                      onPress={() => handleCategoryPress(subcategory.id)}
                      activeOpacity={0.8}
                    >
                      <View style={[styles.subcategoryImageContainer, { backgroundColor: `${subCategoryColor}06` }]}>
                        {subcategory.image ? (
                          <Image source={{ uri: subcategory.image }} style={styles.subcategoryImage} />
                        ) : (
                          <Ionicons 
                            name={getCategoryIcon(subcategory.slug) as any} 
                            size={32} 
                            color={subCategoryColor} 
                          />
                        )}
                      </View>
                      <View style={styles.subcategoryContent}>
                        <Text style={styles.subcategoryName} numberOfLines={2}>
                          {subcategory.name}
                        </Text>
                        {subcategory.product_count !== undefined && subcategory.product_count > 0 && (
                          <View style={[styles.subcategoryCountBadge, { backgroundColor: `${subCategoryColor}12` }]}>
                            <Text style={[styles.subcategoryCount, { color: subCategoryColor }]}>
                              {subcategory.product_count} produit{subcategory.product_count > 1 ? 's' : ''}
                            </Text>
                          </View>
                        )}
                      </View>
                    </TouchableOpacity>

                    {/* Sous-catégories imbriquées */}
                    {hasNested && (
                      <View style={[styles.nestedContainer, { borderLeftColor: `${subCategoryColor}40` }]}>
                        {nestedChildren[subcategory.id].map((nestedCategory: Category) => {
                          const nestedColor = getCategoryColor(nestedCategory.color);
                          return (
                            <TouchableOpacity
                              key={nestedCategory.id}
                              style={[styles.nestedItem, { borderLeftColor: `${nestedColor}50` }]}
                              onPress={() => handleCategoryPress(nestedCategory.id)}
                              activeOpacity={0.8}
                            >
                              <View style={[styles.nestedIconContainer, { backgroundColor: `${nestedColor}08` }]}>
                                {nestedCategory.image ? (
                                  <Image source={{ uri: nestedCategory.image }} style={styles.nestedImage} />
                                ) : (
                                  <Ionicons 
                                    name={getCategoryIcon(nestedCategory.slug) as any} 
                                    size={16} 
                                    color={nestedColor} 
                                  />
                                )}
                              </View>
                              <Text style={styles.nestedName} numberOfLines={1}>
                                {nestedCategory.name}
                              </Text>
                            </TouchableOpacity>
                          );
                        })}
                      </View>
                    )}
                  </View>
                );
              })}
            </View>
          ) : (
            <View style={styles.emptyContainer}>
              <View style={[styles.emptyIconContainer, { backgroundColor: `${categoryColor}08` }]}>
                <Ionicons name="folder-outline" size={48} color={categoryColor} />
              </View>
              <Text style={styles.emptyTitle}>Aucune sous-catégorie</Text>
              <Text style={styles.emptyText}>Cette catégorie ne contient pas de sous-catégories</Text>
              <TouchableOpacity
                style={[styles.viewProductsButton, { backgroundColor: categoryColor }]}
                onPress={() => handleCategoryPress(parentCategory.id)}
                activeOpacity={0.8}
              >
                <Ionicons name="cube-outline" size={18} color="#FFFFFF" style={{ marginRight: 6 }} />
                <Text style={styles.viewProductsButtonText}>Voir les produits</Text>
              </TouchableOpacity>
            </View>
          )}
            </ScrollView>
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
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 2,
    elevation: 2,
    zIndex: 10,
  },
  headerWithIdentity: {
    borderBottomWidth: 1.5,
    borderBottomColor: `${COLORS.PRIMARY}40`,
    backgroundColor: '#FAFAFA',
  },
  content: {
    flex: 1,
  },
  parentHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    marginBottom: 16,
    marginTop: 8,
    marginHorizontal: 12,
    borderRadius: 12,
    borderTopWidth: 2,
  },
  parentIconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
    overflow: 'hidden',
  },
  parentImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  parentContent: {
    flex: 1,
  },
  parentName: {
    fontSize: 20,
    fontWeight: '800',
    color: COLORS.TEXT,
    marginBottom: 6,
    letterSpacing: 0.3,
  },
  parentCountBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 4,
  },
  parentCount: {
    fontSize: 12,
    fontWeight: '700',
  },
  subcategoriesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 12,
    paddingTop: 4,
    justifyContent: 'space-between',
  },
  subcategoryCardWrapper: {
    width: (width - 48) / 2,
    marginBottom: 14,
  },
  subcategoryCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.03,
    shadowRadius: 2,
    elevation: 1,
    borderWidth: 0.5,
    borderColor: '#F5F5F5',
  },
  subcategoryImageContainer: {
    width: '100%',
    height: 100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  subcategoryImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  subcategoryContent: {
    padding: 12,
    paddingTop: 10,
  },
  subcategoryName: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 5,
    lineHeight: 19,
  },
  subcategoryCountBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 5,
    paddingVertical: 2,
    borderRadius: 3,
  },
  subcategoryCount: {
    fontSize: 11,
    fontWeight: '700',
  },
  nestedContainer: {
    marginTop: 6,
    paddingLeft: 8,
    borderLeftWidth: 1.5,
    marginLeft: 4,
  },
  nestedItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 8,
    marginBottom: 4,
    backgroundColor: '#FAFAFA',
    borderRadius: 6,
    borderWidth: 0.5,
    borderColor: '#F0F0F0',
    borderLeftWidth: 2,
  },
  nestedIconContainer: {
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
    overflow: 'hidden',
  },
  nestedImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  nestedName: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.TEXT,
    flex: 1,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 80,
    paddingHorizontal: 32,
  },
  emptyIconContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: COLORS.TEXT,
    marginBottom: 8,
    textAlign: 'center',
  },
  emptyText: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
    marginBottom: 32,
    textAlign: 'center',
    lineHeight: 20,
  },
  viewProductsButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.15,
    shadowRadius: 3,
    elevation: 2,
  },
  viewProductsButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
    letterSpacing: 0.3,
  },
});

export default SubCategoryScreen;
