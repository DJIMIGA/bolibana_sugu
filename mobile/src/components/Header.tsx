import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useAppSelector } from '../store/hooks';
import { COLORS } from '../utils/constants';
import { Logo } from './Logo';
import { Category } from '../types';

interface HeaderProps {
  searchQuery: string;
  onSearchChange: (text: string) => void;
  onClearSearch?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  searchQuery,
  onSearchChange,
  onClearSearch,
  showCategories = false,
  categories = [],
  onCategoryPress,
  onExplorePress,
}) => {
  const navigation = useNavigation();
  const cartItemsCount = useAppSelector((state) => state.cart.items.length);

  // Afficher uniquement les catégories sans parent (catégories principales)
  const displayCategories = categories.filter((c: Category) => !c.parent).slice(0, 8);

  return (
    <View style={styles.header}>
      <View style={styles.headerTop}>
        <View style={styles.logoContainer}>
          <Logo size="medium" showText={false} />
        </View>
        <TouchableOpacity 
          style={styles.notificationIconContainer}
          onPress={() => {
            // Naviguer vers Cart qui est dans RootStack
            const parent = navigation.getParent();
            if (parent) {
              parent.navigate('Cart' as never);
            } else {
              navigation.navigate('Cart' as never);
            }
          }}
        >
          <Ionicons name="cart-outline" size={28} color={COLORS.TEXT} />
          {cartItemsCount > 0 && (
            <View style={styles.notificationBadge}>
              <Text style={styles.notificationBadgeText}>
                {cartItemsCount > 99 ? '99+' : cartItemsCount}
              </Text>
            </View>
          )}
        </TouchableOpacity>
      </View>
      <View style={styles.searchContainer}>
        <View style={styles.searchInputContainer}>
          <Ionicons name="search" size={20} color={COLORS.TEXT_SECONDARY} style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder="Rechercher un produit..."
            placeholderTextColor={COLORS.TEXT_SECONDARY}
            value={searchQuery}
            onChangeText={onSearchChange}
          />
          {searchQuery.length > 0 && onClearSearch && (
            <TouchableOpacity
              onPress={onClearSearch}
              style={styles.clearButton}
            >
              <Ionicons name="close-circle" size={20} color={COLORS.TEXT_SECONDARY} />
            </TouchableOpacity>
          )}
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  header: {
    padding: 12, // Réduit de 16 à 12
    paddingTop: 16, // Ajout d'un padding en haut
    paddingBottom: 10, // Padding en bas réduit
    backgroundColor: '#FFFFFF',
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: -4, // Espace négatif pour rapprocher le logo et le champ de recherche
  },
  logoContainer: {
    alignSelf: 'flex-start',
  },
  notificationIconContainer: {
    position: 'relative',
    padding: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  notificationBadge: {
    position: 'absolute',
    top: 4,
    right: 4,
    backgroundColor: '#EF4444', // Rouge
    borderRadius: 12,
    minWidth: 20,
    height: 20,
    paddingHorizontal: 6,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#FFFFFF',
    zIndex: 1000,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 8,
  },
  notificationBadgeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '800',
    lineHeight: 12,
  },
  searchContainer: {
    width: '100%',
    marginTop: -4, // Espace négatif pour rapprocher du logo
  },
  searchInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 10, // Réduit de 12 à 10
    borderWidth: 1.5,
    borderColor: '#D1D5DB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  searchIcon: {
    marginRight: 12,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: COLORS.TEXT,
    padding: 0,
  },
  clearButton: {
    padding: 4,
    marginLeft: 8,
  },
});


