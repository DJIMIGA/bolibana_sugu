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

const { width } = Dimensions.get('window');

const CategoryScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigation = useNavigation();
  const { categories, isLoading, searchQuery } = useAppSelector((state) => state.product);
  const [refreshing, setRefreshing] = useState(false);
  const [localSearch, setLocalSearch] = useState(searchQuery);

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

  // Séparer les catégories principales et les sous-catégories
  const mainCategories = categories
    .filter((c: Category) => c.is_main && !c.parent)
    .sort((a: Category, b: Category) => {
      if (a.order !== b.order) {
        return a.order - b.order;
      }
      return a.name.localeCompare(b.name);
    });
  
  const subCategories = categories
    .filter((c: Category) => !c.is_main || (c.is_main && c.parent))
    .sort((a: Category, b: Category) => {
      if (a.order !== b.order) {
        return a.order - b.order;
      }
      return a.name.localeCompare(b.name);
    });

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

      <ScrollView
        style={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Catégories principales - Grille comme les autres */}
        {mainCategories.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Catégories principales</Text>
            <View style={styles.gridContainer}>
              {mainCategories.map((category: Category) => (
                <TouchableOpacity
                  key={`main-${category.id}`}
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
              ))}
            </View>
          </View>
        )}

        {/* Sous-catégories - Layout horizontal avec image arrondie */}
        {subCategories.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Toutes les catégories</Text>
            <View style={styles.gridContainer}>
              {subCategories.map((category: Category) => (
                <TouchableOpacity
                  key={`sub-${category.id}`}
                  style={styles.horizontalCard}
                  onPress={() => handleCategoryPress(category.id)}
                  activeOpacity={0.8}
                >
                  <View style={[styles.horizontalImageContainer, { backgroundColor: `${getCategoryColor(category.color)}15` }]}>
                    {category.image ? (
                      <Image source={{ uri: category.image }} style={styles.horizontalImage} />
                    ) : (
                      <View style={styles.horizontalIconContainer}>
                        <Ionicons 
                          name={getCategoryIcon(category.slug) as any} 
                          size={24} 
                          color={getCategoryColor(category.color)} 
                        />
                      </View>
                    )}
                  </View>
                  <View style={styles.horizontalContent}>
                    <Text style={styles.horizontalCategoryName} numberOfLines={2}>
                      {category.name}
                    </Text>
                    {category.product_count !== undefined && category.product_count > 0 && (
                      <Text style={[styles.horizontalCategoryCount, { color: getCategoryColor(category.color) }]}>
                        {category.product_count} produit{category.product_count > 1 ? 's' : ''}
                      </Text>
                    )}
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}

        {/* Message si aucune catégorie */}
        {!isLoading && categories.length === 0 && (
          <View style={styles.emptyContainer}>
            <MaterialIcons name="category" size={64} color={COLORS.TEXT_SECONDARY} />
            <Text style={styles.emptyText}>Aucune catégorie disponible</Text>
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
});

export default CategoryScreen;

