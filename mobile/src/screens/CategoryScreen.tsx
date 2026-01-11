import React, { useEffect, useState } from 'react';
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
} from 'react-native';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchCategories, setSearchQuery, searchProducts, fetchProducts, setFilters } from '../store/slices/productSlice';
import { useNavigation } from '@react-navigation/native';
import { COLORS } from '../utils/constants';
import { Category } from '../types';
import { Header } from '../components/Header';
import { LoadingScreen } from '../components/LoadingScreen';

const { width } = Dimensions.get('window');

const CategoryScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigation = useNavigation();
  const { categories, isLoading, searchQuery } = useAppSelector((state) => state.product);
  const [refreshing, setRefreshing] = useState(false);
  const [localSearch, setLocalSearch] = useState(searchQuery);
  const [expandedCategories, setExpandedCategories] = useState<Set<number>>(new Set());

  useEffect(() => {
    dispatch(fetchCategories());
  }, [dispatch]);

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

  const onRefresh = async () => {
    setRefreshing(true);
    await dispatch(fetchCategories());
    setRefreshing(false);
  };

  // Fonction pour formater le rayon_type (comme sur le web)
  const formatRayonType = (rayonType: string | null | undefined): string => {
    if (!rayonType) return '';
    return rayonType.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
  };

  // Log pour debug
  console.log('[CategoryScreen] 📊 Total catégories reçues:', (categories || []).length);
  if (categories && categories.length > 0) {
    console.log('[CategoryScreen] 📋 Exemples catégories:', categories.slice(0, 5).map((c: Category) => ({
      id: c.id,
      name: c.name,
      rayon_type: c.rayon_type,
      level: c.level,
      parent: c.parent,
      has_rayon_type: !!c.rayon_type,
      has_level: c.level !== undefined && c.level !== null
    })));
    
    // Log toutes les catégories pour voir lesquelles ont rayon_type ou level
    const categoriesWithRayonType = categories.filter((c: Category) => !!c.rayon_type);
    const categoriesWithLevel = categories.filter((c: Category) => c.level !== undefined && c.level !== null);
    console.log(`[CategoryScreen] 📊 Catégories avec rayon_type: ${categoriesWithRayonType.length}`);
    console.log(`[CategoryScreen] 📊 Catégories avec level: ${categoriesWithLevel.length}`);
    
    if (categoriesWithRayonType.length > 0) {
      console.log('[CategoryScreen] 📋 Catégories avec rayon_type:', categoriesWithRayonType.map((c: Category) => ({
        id: c.id,
        name: c.name,
        rayon_type: c.rayon_type
      })));
    }
    
    if (categoriesWithLevel.length > 0) {
      console.log('[CategoryScreen] 📋 Catégories avec level:', categoriesWithLevel.map((c: Category) => ({
        id: c.id,
        name: c.name,
        level: c.level
      })));
    }
  }

  // Filtrer uniquement les catégories B2B (avec rayon_type ou level défini)
  // Vérifier que rayon_type n'est pas null/undefined et que level n'est pas null/undefined
  const b2bCategories = (categories || []).filter((c: Category) => 
    (c.rayon_type !== null && c.rayon_type !== undefined) || 
    (c.level !== null && c.level !== undefined)
  );

  console.log(`[CategoryScreen] 🎯 Catégories B2B filtrées: ${b2bCategories.length}`);
  if (b2bCategories.length > 0) {
    console.log('[CategoryScreen] 📋 Exemples catégories B2B:', b2bCategories.slice(0, 3).map((c: Category) => ({
      id: c.id,
      name: c.name,
      rayon_type: c.rayon_type,
      level: c.level
    })));
  }

  // Organiser les catégories par rayon_type et niveau
  // Catégories de niveau 0 uniquement (comme sur le web)
  const level0Categories = b2bCategories.filter((c: Category) => 
    c.level === 0 || (c.level === null && !c.parent)
  );

  console.log(`[CategoryScreen] 📍 Catégories niveau 0: ${level0Categories.length}`);

  // Grouper par rayon_type
  const categoriesByRayon: { [key: string]: Category[] } = {};
  level0Categories.forEach((category: Category) => {
    const rayonType = category.rayon_type || 'Autres';
    if (!categoriesByRayon[rayonType]) {
      categoriesByRayon[rayonType] = [];
    }
    categoriesByRayon[rayonType].push(category);
  });

  // Trier les catégories dans chaque rayon
  Object.keys(categoriesByRayon).forEach((rayonType) => {
    categoriesByRayon[rayonType].sort((a: Category, b: Category) => {
      if (a.order !== b.order) {
        return a.order - b.order;
      }
      return a.name.localeCompare(b.name);
    });
  });

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

  const toggleCategory = (categoryId: number) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(categoryId)) {
      newExpanded.delete(categoryId);
    } else {
      newExpanded.add(categoryId);
    }
    setExpandedCategories(newExpanded);
  };

  const getCategoryColor = (color: string) => {
    const colorMap: { [key: string]: string } = {
      green: '#10B981',
      yellow: '#F59E0B',
      red: '#EF4444',
      blue: '#3B82F6',
      purple: '#8B5CF6',
      indigo: '#6366F1',
      pink: '#EC4899',
    };
    return colorMap[color] || COLORS.PRIMARY;
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
    
    return (
      <TouchableOpacity
        style={styles.subCategoryCard}
        onPress={() => handleCategoryPress(item.id)}
        activeOpacity={0.8}
      >
        <View style={[styles.subCategoryImageContainer, { backgroundColor: `${categoryColor}15` }]}>
          {item.image ? (
            <Image source={{ uri: item.image }} style={styles.subCategoryImage} />
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
      <View style={styles.headerFixedContainer}>
        <Header
          searchQuery={localSearch}
          onSearchChange={handleSearch}
          onClearSearch={handleClearSearch}
          showCategories={true}
          categories={categories}
          onCategoryPress={(categoryId) => handleCategoryPress(categoryId)}
        />
      </View>

      {isLoading ? (
        <LoadingScreen />
      ) : (
        <ScrollView
          style={styles.content}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        >
          {/* Catégories B2B organisées par rayon_type (comme sur le web) */}
          {Object.keys(categoriesByRayon).length > 0 ? (
            Object.entries(categoriesByRayon).map(([rayonType, rayonCategories]) => (
              <View key={rayonType} style={styles.section}>
                {/* Titre du rayon */}
                <View style={styles.rayonHeader}>
                  <Text style={styles.rayonTitle}>{formatRayonType(rayonType)}</Text>
                </View>
                
                {/* Catégories de niveau 0 */}
              <View style={styles.gridContainer}>
                  {rayonCategories.map((category: Category) => {
                    const isExpanded = expandedCategories.has(category.id);
                    
                    return (
                      <View key={`category-${category.id}`} style={styles.categoryWrapper}>
                  <TouchableOpacity
                    style={styles.gridItem}
                    onPress={() => handleCategoryPress(category.id)}
                    activeOpacity={0.8}
                  >
                    <View style={[styles.gridImageContainer, { backgroundColor: `${getCategoryColor(category.color)}15` }]}>
                      {category.image ? (
                        <Image source={{ uri: category.image }} style={styles.gridImage} />
                      ) : (
                        <View style={styles.gridIconContainer}>
                          <Ionicons 
                            name={getCategoryIcon(category.slug) as any} 
                            size={32} 
                            color={getCategoryColor(category.color)} 
                          />
                        </View>
                      )}
                    </View>
                    <View style={styles.gridContent}>
                      <Text style={styles.gridCategoryName} numberOfLines={2}>
                        {category.name}
                      </Text>
                      {category.product_count !== undefined && category.product_count > 0 && (
                        <Text style={[styles.gridCategoryCount, { color: getCategoryColor(category.color) }]}>
                          {category.product_count} produit{category.product_count > 1 ? 's' : ''}
                        </Text>
                      )}
                    </View>
                  </TouchableOpacity>
                        
                        {/* Bouton pour afficher/masquer les sous-catégories */}
                        {categoryHierarchy[category.id]?.children.length > 0 && (
                          <TouchableOpacity
                            style={styles.expandButton}
                            onPress={() => toggleCategory(category.id)}
                            activeOpacity={0.7}
                          >
                            <Ionicons 
                              name={isExpanded ? 'chevron-up' : 'chevron-down'} 
                              size={20} 
                              color={getCategoryColor(category.color)} 
                            />
                            <Text style={[styles.expandButtonText, { color: getCategoryColor(category.color) }]}>
                              {isExpanded ? 'Masquer' : 'Voir'} ({categoryHierarchy[category.id]?.children.length || 0})
                            </Text>
                          </TouchableOpacity>
                        )}
                        
                        {/* Sous-catégories (tous les niveaux récursifs) */}
                        {isExpanded && categoryHierarchy[category.id]?.children.length > 0 && (
                          <View style={styles.subcategoriesContainer}>
                            {categoryHierarchy[category.id].children.map((subcategory: Category) => {
                              const nestedChildren = categoryHierarchy[category.id]?.nested[subcategory.id] || [];
                              const isSubExpanded = expandedCategories.has(subcategory.id);
                              
                              return (
                                <View key={`sub-${subcategory.id}`} style={styles.subcategoryWrapper}>
                                  <TouchableOpacity
                                    style={styles.subcategoryItem}
                                    onPress={() => handleCategoryPress(subcategory.id)}
                                    activeOpacity={0.8}
                                  >
                                    <View style={[styles.subcategoryIconContainer, { backgroundColor: `${getCategoryColor(subcategory.color)}15` }]}>
                                      {subcategory.image ? (
                                        <Image source={{ uri: subcategory.image }} style={styles.subcategoryIconImage} />
                                      ) : (
                                        <Ionicons 
                                          name={getCategoryIcon(subcategory.slug) as any} 
                                          size={20} 
                                          color={getCategoryColor(subcategory.color)} 
                                        />
                                      )}
                                    </View>
                                    <Text style={styles.subcategoryName} numberOfLines={1}>
                                      {subcategory.name}
                                    </Text>
                                    {nestedChildren.length > 0 && (
                                      <TouchableOpacity
                                        onPress={() => toggleCategory(subcategory.id)}
                                        style={{ marginLeft: 8 }}
                                      >
                                        <Ionicons 
                                          name={isSubExpanded ? 'chevron-up' : 'chevron-down'} 
                                          size={16} 
                                          color={getCategoryColor(subcategory.color)} 
                                        />
                                      </TouchableOpacity>
                                    )}
                                  </TouchableOpacity>
                                  
                                  {/* Niveaux plus profonds (2, 3, etc.) */}
                                  {isSubExpanded && nestedChildren.length > 0 && (
                                    <View style={[styles.nestedSubcategoriesContainer, { borderLeftColor: getCategoryColor(subcategory.color) }]}>
                                      {nestedChildren.map((nestedCategory: Category) => (
                                        <TouchableOpacity
                                          key={`nested-${nestedCategory.id}`}
                                          style={[styles.nestedSubcategoryItem]}
                                          onPress={() => handleCategoryPress(nestedCategory.id)}
                                          activeOpacity={0.8}
                                        >
                                          <View style={[styles.subcategoryIconContainer, { backgroundColor: `${getCategoryColor(nestedCategory.color)}15`, width: 20, height: 20 }]}>
                                            {nestedCategory.image ? (
                                              <Image source={{ uri: nestedCategory.image }} style={styles.subcategoryIconImage} />
                                            ) : (
                                              <Ionicons 
                                                name={getCategoryIcon(nestedCategory.slug) as any} 
                                                size={16} 
                                                color={getCategoryColor(nestedCategory.color)} 
                                              />
                                            )}
                                          </View>
                                          <Text style={[styles.nestedSubcategoryName]} numberOfLines={1}>
                                            {nestedCategory.name}
                                          </Text>
                                        </TouchableOpacity>
                                      ))}
                                    </View>
                                  )}
                                </View>
                              );
                            })}
                          </View>
                        )}
                      </View>
                    );
                  })}
                </View>
              </View>
            ))
          ) : (
            /* Message si aucune catégorie B2B */
            !isLoading && (
            <View style={styles.emptyContainer}>
              <MaterialIcons name="category" size={64} color={COLORS.TEXT_SECONDARY} />
                <Text style={styles.emptyText}>Aucune catégorie B2B disponible</Text>
            </View>
            )
          )}
        </ScrollView>
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
  section: {
    marginBottom: 20, // Réduit à 20px
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
    paddingHorizontal: 12,
    justifyContent: 'space-between',
  },
  gridItem: {
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
    width: '100%',
    height: 100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  gridImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  gridIconContainer: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  gridContent: {
    padding: 12,
  },
  gridCategoryName: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 4,
  },
  gridCategoryCount: {
    fontSize: 11,
    fontWeight: '500',
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
  rayonHeader: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    backgroundColor: '#F9FAFB',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
    marginBottom: 12,
  },
  rayonTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.TEXT,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  categoryWrapper: {
    marginBottom: 16,
  },
  expandButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
    marginTop: 8,
    backgroundColor: '#F3F4F6',
    borderRadius: 8,
    marginHorizontal: 4,
  },
  expandButtonText: {
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4,
  },
  subcategoriesContainer: {
    flexDirection: 'column',
    paddingHorizontal: 12,
    paddingTop: 8,
    paddingBottom: 8,
    marginTop: 8,
    backgroundColor: '#FAFAFA',
    borderRadius: 8,
    marginHorizontal: 4,
  },
  subcategoryWrapper: {
    width: '100%',
    marginBottom: 8,
  },
  subcategoryItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 12,
    marginBottom: 4,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    minWidth: 120,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  nestedSubcategoriesContainer: {
    marginLeft: 16,
    marginTop: 8,
    paddingLeft: 12,
    borderLeftWidth: 2,
    paddingTop: 4,
    paddingBottom: 4,
  },
  nestedSubcategoryItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 10,
    marginBottom: 4,
    backgroundColor: '#F9FAFB',
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  nestedSubcategoryName: {
    fontSize: 12,
    fontWeight: '500',
    color: COLORS.TEXT,
    flex: 1,
    marginLeft: 8,
  },
  subcategoryIconContainer: {
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
    overflow: 'hidden',
  },
  subcategoryIconImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  subcategoryName: {
    fontSize: 12,
    fontWeight: '500',
    color: COLORS.TEXT,
    flex: 1,
  },
});

export default CategoryScreen;

