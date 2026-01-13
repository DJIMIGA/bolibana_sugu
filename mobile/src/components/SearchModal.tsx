import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Keyboard,
} from 'react-native';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { searchProducts, setSearchQuery, clearFilters } from '../store/slices/productSlice';
import { formatPrice } from '../utils/helpers';
import { COLORS } from '../utils/constants';
import { Product } from '../types';

interface SearchModalProps {
  visible: boolean;
  onClose: () => void;
  initialQuery?: string;
}

const SearchModal: React.FC<SearchModalProps> = ({ visible, onClose, initialQuery = '' }) => {
  const navigation = useNavigation();
  const dispatch = useAppDispatch();
  const { products, isLoading, searchQuery } = useAppSelector((state) => state.product);
  const [searchResults, setSearchResults] = useState<Product[]>([]);

  // Mettre à jour les résultats quand les produits changent (seulement si on recherche)
  useEffect(() => {
    if (visible) {
      if (searchQuery && searchQuery.trim().length > 0 && products.length > 0) {
        setSearchResults(products);
      } else if (!searchQuery || searchQuery.trim().length === 0) {
        setSearchResults([]);
      }
    }
  }, [products, searchQuery, visible]);

  // Réinitialiser quand le modal se ferme
  useEffect(() => {
    if (!visible) {
      setSearchResults([]);
      Keyboard.dismiss();
    }
  }, [visible]);

  const handleProductPress = (product: Product) => {
    onClose();
    navigation.navigate('Products' as never, { 
      screen: 'ProductDetail', 
      params: { slug: product.slug } 
    } as never);
  };

  const renderProductItem = ({ item }: { item: Product }) => (
    <TouchableOpacity
      style={styles.productItem}
      onPress={() => handleProductPress(item)}
      activeOpacity={0.7}
    >
      <View style={styles.productImageContainer}>
        {item.image ? (
          <Image source={{ uri: item.image }} style={styles.productImage} resizeMode="cover" />
        ) : (
          <View style={styles.productImageFallback}>
            <MaterialIcons name="image-not-supported" size={32} color={COLORS.TEXT_SECONDARY} />
          </View>
        )}
      </View>
      <View style={styles.productInfo}>
        <Text style={styles.productTitle} numberOfLines={2}>{item.title}</Text>
        <Text style={styles.productPrice}>
          {formatPrice(item.discount_price || item.price)}
        </Text>
      </View>
      <Ionicons name="chevron-forward" size={20} color={COLORS.TEXT_SECONDARY} />
    </TouchableOpacity>
  );

  const renderEmpty = () => {
    if (isLoading) {
      return (
        <View style={styles.emptyContainer}>
          <ActivityIndicator size="large" color={COLORS.PRIMARY} />
          <Text style={styles.emptyText}>Recherche en cours...</Text>
        </View>
      );
    }

    if (searchQuery.trim().length === 0) {
      return (
        <View style={styles.emptyContainer}>
          <Ionicons name="search" size={64} color={COLORS.TEXT_SECONDARY} />
          <Text style={styles.emptyTitle}>Rechercher un produit</Text>
          <Text style={styles.emptyText}>
            Tapez le nom d'un produit pour commencer votre recherche
          </Text>
        </View>
      );
    }

    return (
      <View style={styles.emptyContainer}>
        <Ionicons name="search-outline" size={64} color={COLORS.TEXT_SECONDARY} />
        <Text style={styles.emptyTitle}>Aucun résultat</Text>
        <Text style={styles.emptyText}>
          Aucun produit trouvé pour "{searchQuery}"
        </Text>
      </View>
    );
  };

  if (!visible) return null;

  return (
    <View style={styles.container}>
      {/* Header avec bouton de fermeture */}
      <View style={styles.modalHeader}>
        <Text style={styles.modalHeaderTitle}>Résultats de recherche</Text>
        <TouchableOpacity
          onPress={() => {
            Keyboard.dismiss();
            onClose();
          }}
          style={styles.closeButton}
          activeOpacity={0.7}
        >
          <Ionicons name="close" size={24} color={COLORS.TEXT} />
        </TouchableOpacity>
      </View>

      {/* Résultats */}
      <FlatList
        data={searchResults}
        renderItem={renderProductItem}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={renderEmpty}
        contentContainerStyle={styles.listContent}
        keyboardShouldPersistTaps="handled"
        style={styles.list}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
    backgroundColor: '#FFFFFF',
  },
  modalHeaderTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.TEXT,
  },
  closeButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#F9FAFB',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  list: {
    flex: 1,
  },
  listContent: {
    paddingBottom: 20,
  },
  productItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  productImageContainer: {
    width: 60,
    height: 60,
    borderRadius: 8,
    overflow: 'hidden',
    backgroundColor: '#F9FAFB',
    marginRight: 12,
  },
  productImage: {
    width: '100%',
    height: '100%',
  },
  productImageFallback: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
  },
  productInfo: {
    flex: 1,
  },
  productTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 4,
  },
  productPrice: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.DANGER,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
    minHeight: 400,
  },
  emptyTitle: {
    fontSize: 20,
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
  },
});

export default SearchModal;
