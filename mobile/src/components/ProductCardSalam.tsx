import React from 'react';
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
} from 'react-native';
import { MaterialIcons, Ionicons } from '@expo/vector-icons';
import { Product } from '../types';
import { formatPrice } from '../utils/helpers';
import { COLORS } from '../utils/constants';
import { useNavigation } from '@react-navigation/native';
import { useAppSelector } from '../store/hooks';

interface ProductCardSalamProps {
  product: Product;
}

const { width } = Dimensions.get('window');
const CARD_WIDTH = (width - 48) / 2; // 16px padding on each side, 16px gap in between

const ProductCardSalam: React.FC<ProductCardSalamProps> = ({ product }) => {
  const navigation = useNavigation();
  const { items } = useAppSelector((state) => state.cart);
  
  // Vérifier si le produit est dans le panier
  const itemInCart = items.find(item => item.product.id === product.id);
  const quantityInCart = itemInCart ? itemInCart.quantity : 0;

  const handlePress = () => {
    navigation.navigate('Products' as never, { screen: 'ProductDetail', params: { slug: product.slug } } as never);
  };

  const hasDiscount = product.discount_price && 
                     product.discount_price > 0 && 
                     product.price > 0 &&
                     product.discount_price < product.price;
  
  const discountPercentage = hasDiscount && product.price > 0
    ? Math.round(((product.price - product.discount_price) / product.price) * 100)
    : 0;

  return (
    <TouchableOpacity style={styles.card} onPress={handlePress} activeOpacity={0.8}>
      <View style={styles.imageContainer}>
        {product.image || product.image_urls?.main ? (
          <Image 
            source={{ uri: product.image || product.image_urls?.main }} 
            style={styles.image}
            resizeMode="cover"
          />
        ) : (
          <View style={styles.imagePlaceholder}>
            <MaterialIcons name="image-not-supported" size={32} color={COLORS.TEXT_SECONDARY} />
          </View>
        )}
        
        {/* Badge SALAM */}
        <View style={styles.salamBadgeContainer}>
          <Text style={styles.salamBadgeText}>SALAM</Text>
        </View>

        {/* Badge de promotion */}
        {discountPercentage > 0 && (
          <View style={styles.discountBadge}>
            <Text style={styles.discountBadgeText}>-{discountPercentage}%</Text>
          </View>
        )}

        {/* Badge dans le panier */}
        {quantityInCart > 0 && (
          <View style={styles.cartBadge}>
            <Ionicons name="cart" size={12} color="#FFFFFF" />
            <Text style={styles.cartBadgeText}>{quantityInCart}</Text>
          </View>
        )}

        {/* Badge indisponible */}
        {!product.is_available && (
          <View style={styles.unavailableBadge}>
            <Text style={styles.unavailableBadgeText}>Indisponible</Text>
          </View>
        )}
      </View>

      <View style={styles.infoContainer}>
        <Text style={styles.title} numberOfLines={2}>{product.title}</Text>
        {product.brand && (
          <View style={styles.brandContainer}>
            <MaterialIcons name="business" size={12} color={COLORS.PRIMARY} />
            <Text style={styles.brand}>{product.brand}</Text>
          </View>
        )}
        <View style={styles.priceContainer}>
          {hasDiscount ? (
            <>
              <Text style={styles.discountPrice}>{formatPrice(product.discount_price!)}</Text>
              <Text style={styles.oldPrice}>{formatPrice(product.price)}</Text>
            </>
          ) : (
            <Text style={styles.price}>{formatPrice(product.price)}</Text>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    width: CARD_WIDTH,
    backgroundColor: COLORS.BACKGROUND,
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 16,
    marginHorizontal: 8,
    shadowColor: COLORS.SECONDARY,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 6,
    elevation: 4,
    borderWidth: 2,
    borderColor: COLORS.SECONDARY,
  },
  imageContainer: {
    width: '100%',
    height: 160,
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
  salamBadgeContainer: {
    position: 'absolute',
    top: 8,
    left: 8,
    backgroundColor: COLORS.SECONDARY,
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 3,
    elevation: 4,
  },
  salamBadgeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '900',
    letterSpacing: 0.8,
  },
  discountBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: COLORS.DANGER,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 3,
    elevation: 4,
  },
  discountBadgeText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: '900',
    letterSpacing: 0.3,
  },
  cartBadge: {
    position: 'absolute',
    bottom: 8,
    right: 8,
    backgroundColor: COLORS.PRIMARY,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    borderWidth: 1.5,
    borderColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 3,
    elevation: 4,
  },
  cartBadgeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '800',
    marginLeft: 2,
  },
  unavailableBadge: {
    position: 'absolute',
    bottom: 8,
    left: 8,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  unavailableBadgeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '700',
  },
  infoContainer: {
    padding: 12,
  },
  title: {
    fontSize: 14,
    fontWeight: '700',
    color: COLORS.TEXT,
    marginBottom: 6,
    lineHeight: 18,
    minHeight: 36,
  },
  brandContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  brand: {
    fontSize: 11,
    color: COLORS.PRIMARY,
    marginLeft: 4,
    fontWeight: '600',
  },
  priceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    marginTop: 4,
  },
  price: {
    fontSize: 18,
    fontWeight: '900',
    color: COLORS.DANGER,
    letterSpacing: -0.3,
  },
  discountPrice: {
    fontSize: 18,
    fontWeight: '900',
    color: COLORS.DANGER,
    letterSpacing: -0.3,
    marginRight: 8,
  },
  oldPrice: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.TEXT_SECONDARY,
    textDecorationLine: 'line-through',
  },
});

export default ProductCardSalam;

