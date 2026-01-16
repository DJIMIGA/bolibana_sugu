import React, { useEffect, useMemo, useRef, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  RefreshControl,
  FlatList,
  Dimensions,
  SafeAreaView,
  Keyboard,
} from 'react-native';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchCategories, setSearchQuery, searchProducts, fetchProducts, setFilters, clearFilters } from '../store/slices/productSlice';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { COLORS } from '../utils/constants';
import { Category } from '../types';
import { Header } from '../components/Header';
import { LoadingScreen } from '../components/LoadingScreen';
import SearchModal from '../components/SearchModal';

const { width } = Dimensions.get('window');

const CategoryScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigation = useNavigation<any>();
  const { categories, isLoading, searchQuery } = useAppSelector((state) => state.product);
  const [refreshing, setRefreshing] = useState(false);
  const [searchModalVisible, setSearchModalVisible] = useState(false);

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

  const onRefresh = async () => {
    setRefreshing(true);
    await dispatch(fetchCategories());
    setRefreshing(false);
  };

  // Filtrer uniquement les catégories B2B (avec rayon_type ou level défini)
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
    
    // Trier par order puis par nom
    return level0.sort((a: Category, b: Category) => {
      if (a.order !== b.order) {
        return a.order - b.order;
      }
      return a.name.localeCompare(b.name);
    });
  }, [b2bCategories]);

  // Logs debug supprimés pour nettoyage

  // Fonction récursive pour construire la hiérarchie complète (tous les niveaux)
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

    // Trouver les enfants par level et rayon_type (ou par parent si pas de B2B)
    allCategories.forEach((category: Category) => {
      if (category.id === parentCategory.id) return;
      
      // Si on a des catégories B2B, utiliser la logique B2B
      if (b2bCategories.length > 0) {
        // Vérifier si c'est un enfant direct par level et rayon_type
        if (
          category.level === expectedLevel &&
          category.rayon_type === parentCategory.rayon_type
        ) {
          // Vérifier aussi par parent si disponible
          if (category.parent === parentCategory.id || !category.parent) {
            children.push(category);
          }
        }
      } else {
        // Sinon, utiliser la logique normale par parent
        if (category.parent === parentCategory.id) {
          children.push(category);
        }
      }
    });

    // Trier les enfants
    children.sort((a: Category, b: Category) => {
      if (a.order !== b.order) {
        return a.order - b.order;
      }
      return a.name.localeCompare(b.name);
    });

    return children;
  };

  // Créer une hiérarchie complète pour toutes les catégories (tous les niveaux)
  const categoryHierarchy: { [key: number]: { category: Category; children: Category[]; nested: { [key: number]: Category[] } } } = {};
  
  level0Categories.forEach((category: Category) => {
    const level1Children = buildCategoryHierarchy(category, b2bCategories, 0);
    const nested: { [key: number]: Category[] } = {};
    
    // Construire récursivement les niveaux plus profonds
    level1Children.forEach((level1Child: Category) => {
      const level2Children = buildCategoryHierarchy(level1Child, b2bCategories, 1);
      if (level2Children.length > 0) {
        nested[level1Child.id] = level2Children;
        
        // Continuer pour les niveaux 3, 4, etc.
        level2Children.forEach((level2Child: Category) => {
          const level3Children = buildCategoryHierarchy(level2Child, b2bCategories, 2);
          if (level3Children.length > 0) {
            if (!nested[level2Child.id]) {
              nested[level2Child.id] = [];
            }
            nested[level2Child.id] = level3Children;
          }
        });
      }
    });
    
    categoryHierarchy[category.id] = {
      category,
      children: level1Children,
      nested
    };
  });

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

  const renderSubCategoryCard = ({ item }: { item: Category }) => {
    const categoryColor = getCategoryColor(item.color);
    const categoryImageUrl = item.image_url || item.image;
    
    return (
      <TouchableOpacity
        style={styles.subCategoryCard}
        onPress={() => handleCategoryPress(item.id)}
        activeOpacity={0.8}
      >
        <View style={[styles.subCategoryImageContainer, { backgroundColor: `${categoryColor}15` }]}>
          {categoryImageUrl ? (
            <Image source={{ uri: categoryImageUrl }} style={styles.subCategoryImage} />
          ) : (
            <View style={styles.subCategoryIconContainer}>
              <Ionicons 
                name={getCategoryIcon(item.slug) as any} 
                size={40} 
                color={categoryColor} 
              />
            </View>
          )}
        </View>
        <View style={styles.subCategoryContent}>
          <Text style={styles.subCategoryName}>{item.name}</Text>
          {item.product_count !== undefined && item.product_count > 0 && (
            <Text style={[styles.subCategoryCount, { color: categoryColor }]}>
              {item.product_count} produit{item.product_count > 1 ? 's' : ''}
            </Text>
          )}
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={[styles.headerFixedContainer, styles.headerWithIdentity]}>
        <Header
          searchQuery={searchQuery}
          onSearchChange={handleSearch}
          onClearSearch={handleClearSearch}
          showCategories={true}
          categories={categories}
          onCategoryPress={(categoryId) => handleCategoryPress(categoryId)}
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
              {/* Catégories de niveau 0 - affichage compact sans rayon_type */}
              {level0Categories.length > 0 ? (
                <View style={styles.gridContainer}>
                  {level0Categories.map((category: Category) => {
                    const categoryColor = getCategoryColor(category.color);
                    const hasChildren = categoryHierarchy[category.id]?.children.length > 0;
                    const categoryImageUrl = category.image_url || category.image;
                    
                    return (
                      <View
                        key={`category-${category.id}`}
                        style={[styles.gridItem, { borderTopWidth: 2, borderTopColor: `${categoryColor}60` }]}
                      >
                        {/* Zone principale : clic pour ouvrir la catégorie directement */}
                        <TouchableOpacity
                          style={styles.categoryMainArea}
                          onPress={() => handleCategoryPress(category.id)}
                          activeOpacity={0.8}
                        >
                          <View
                            style={[
                              styles.gridImageContainer,
                              {
                                backgroundColor: `${categoryColor}10`,
                                borderColor: `${categoryColor}40`,
                              },
                            ]}
                          >
                            {categoryImageUrl ? (
                              <Image source={{ uri: categoryImageUrl }} style={styles.gridImage} />
                            ) : (
                              <View style={styles.gridIconContainer}>
                                <Ionicons 
                                  name={getCategoryIcon(category.slug) as any} 
                                  size={32} 
                                  color={categoryColor} 
                                />
                              </View>
                            )}
                          </View>
                          <View style={styles.gridContent}>
                            <Text style={styles.gridCategoryName} numberOfLines={2}>
                              {category.name}
                            </Text>
                            {category.product_count !== undefined && category.product_count > 0 && (
                              <Text style={[styles.gridCategoryCount, { color: categoryColor }]}>
                                {category.product_count} produit{category.product_count > 1 ? 's' : ''}
                              </Text>
                            )}
                          </View>
                        </TouchableOpacity>
                        
                        {/* Zone secondaire : clic pour ouvrir les sous-catégories */}
                        {hasChildren && (
                          <TouchableOpacity
                            style={[styles.subcategoryButton, { backgroundColor: `${categoryColor}15`, borderTopColor: categoryColor }]}
                            onPress={() => {
                              navigation.navigate('SubCategory' as never, { 
                                categoryId: category.id 
                              } as never);
                            }}
                            activeOpacity={0.7}
                          >
                            <Ionicons 
                              name="list" 
                              size={16} 
                              color={categoryColor} 
                            />
                            <Text style={[styles.subcategoryButtonText, { color: categoryColor }]}>
                              Sous-catégories
                            </Text>
                            <Ionicons 
                              name="chevron-forward" 
                              size={14} 
                              color={categoryColor} 
                            />
                          </TouchableOpacity>
                        )}
                      </View>
                    );
                  })}
                </View>
              ) : (
                !isLoading && (
                  <View style={styles.emptyContainer}>
                    <MaterialIcons name="category" size={64} color={COLORS.TEXT_SECONDARY} />
                    <Text style={styles.emptyText}>Aucune catégorie disponible</Text>
                  </View>
                )
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
  header: {
    padding: 20,
    backgroundColor: 'transparent',
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  logoContainer: {
    alignSelf: 'flex-start',
  },
  headerContent: {
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.TEXT,
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 12,
    paddingHorizontal: 20,
  },
  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 8,
    paddingTop: 6,
    justifyContent: 'space-between',
    gap: 6,
  },
  gridItem: {
    width: (width - 48) / 2,
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    marginBottom: 6,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 3,
    elevation: 2,
    borderWidth: 1,
    borderColor: '#F3F4F6',
  },
  categoryMainArea: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 8,
  },
  subcategoryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 6,
    paddingHorizontal: 8,
    borderTopWidth: 1,
    marginTop: 2,
  },
  subcategoryButtonText: {
    fontSize: 10,
    fontWeight: '600',
    flex: 1,
    marginLeft: 4,
  },
  subCategoryCard: {
    width: (width - 48) / 2,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginBottom: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  subCategoryImageContainer: {
    width: '100%',
    height: 120,
    justifyContent: 'center',
    alignItems: 'center',
  },
  subCategoryImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  subCategoryIconContainer: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  subCategoryContent: {
    padding: 12,
  },
  subCategoryName: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 4,
  },
  subCategoryCount: {
    fontSize: 12,
    fontWeight: '500',
  },
  gridImageContainer: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
    borderWidth: 1,
  },
  gridImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
    borderRadius: 22,
  },
  gridIconContainer: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  gridContent: {
    flex: 1,
    marginLeft: 6,
  },
  gridCategoryName: {
    fontSize: 12,
    fontWeight: '700',
    color: COLORS.TEXT,
    marginBottom: 2,
    lineHeight: 16,
  },
  gridCategoryCount: {
    fontSize: 9,
    fontWeight: '600',
  },
  horizontalCard: {
    width: (width - 48) / 2,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginBottom: 12,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    flexDirection: 'row',
    padding: 10,
    alignItems: 'center',
  },
  horizontalImageContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
    overflow: 'hidden',
  },
  horizontalImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  horizontalIconContainer: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  horizontalContent: {
    flex: 1,
    justifyContent: 'center',
  },
  horizontalCategoryName: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 4,
  },
  horizontalCategoryCount: {
    fontSize: 11,
    fontWeight: '500',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    fontSize: 16,
    color: COLORS.TEXT_SECONDARY,
    marginTop: 16,
  },
  subcategoriesContainer: {
    flexDirection: 'column',
    paddingHorizontal: 8,
    paddingTop: 6,
    paddingBottom: 6,
    marginTop: 6,
    marginBottom: 4,
    backgroundColor: '#FAFAFA',
    borderRadius: 6,
    marginHorizontal: 4,
    borderLeftWidth: 2,
  },
  subcategoryWrapper: {
    width: '100%',
    marginBottom: 4,
  },
  subcategoryItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 10,
    marginBottom: 3,
    backgroundColor: '#FFFFFF',
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    minWidth: 120,
  },
  subcategoryTextContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginLeft: 8,
  },
  subcategoryCount: {
    fontSize: 9,
    fontWeight: '600',
    marginLeft: 6,
  },
  chevronIcon: {
    marginLeft: 6,
  },
  nestedSubcategoriesContainer: {
    marginLeft: 16,
    marginTop: 4,
    paddingLeft: 8,
    borderLeftWidth: 2,
    paddingTop: 4,
    paddingBottom: 4,
  },
  nestedSubcategoryItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 8,
    marginBottom: 2,
    backgroundColor: '#F9FAFB',
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderLeftWidth: 2,
  },
  nestedSubcategoryName: {
    fontSize: 11,
    fontWeight: '600',
    color: COLORS.TEXT,
    flex: 1,
    marginLeft: 6,
  },
  subcategoryIconContainer: {
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
  },
  subcategoryIconImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  subcategoryName: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.TEXT,
    flex: 1,
  },
});

export default CategoryScreen;

