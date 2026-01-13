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
import ProductCardInfo from './ProductCardInfo';

interface ProductCardPhoneProps {
  product: Product;
}

const { width } = Dimensions.get('window');
const CARD_WIDTH = (width - 48) / 2; // 16px padding on each side, 16px gap in between

// Interface pour les données de téléphone (peuvent être dans specifications)
interface PhoneData {
  brand?: string;
  model?: string;
  color?: string;
  color_name?: string;
  color_code?: string;
  storage?: number;
  ram?: number;
  screen_size?: string;
  resolution?: string;
  operating_system?: string;
  processor?: string;
  battery_capacity?: number;
  camera_main?: string;
  camera_front?: string;
  network?: string;
  is_new?: boolean;
  warranty_period?: number;
}

const ProductCardPhone: React.FC<ProductCardPhoneProps> = ({ product }) => {
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

  // Extraire les données de téléphone depuis specifications
  const phoneData: PhoneData = product.specifications || {};
  const colorCode = phoneData.color_code || '#10B981'; // Vert par défaut
  const isNew = phoneData.is_new !== undefined ? phoneData.is_new : product.condition === 'new';

  return (
    <TouchableOpacity style={styles.card} onPress={handlePress} activeOpacity={0.8}>
      {/* Bordure colorée subtile basée sur la couleur du téléphone */}
      <View style={[styles.colorBorder, { borderColor: `${colorCode}30`, backgroundColor: `${colorCode}08` }]} />
      
      <View style={styles.imageContainer}>
        {product.image || product.image_urls?.main ? (
          <Image 
            source={{ uri: product.image || product.image_urls?.main }} 
            style={styles.image}
            resizeMode="cover"
          />
        ) : (
          <View style={styles.imagePlaceholder}>
            <MaterialIcons name="phone-android" size={32} color={COLORS.TEXT_SECONDARY} />
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

        {/* Indicateur de couleur du téléphone */}
        {phoneData.color_code && (
          <View style={[styles.colorIndicator, { backgroundColor: colorCode }]}>
            <Ionicons name="phone-portrait" size={12} color="#FFFFFF" />
          </View>
        )}
      </View>

      <View style={styles.infoContainer}>
        {/* Titre */}
        <Text style={styles.title} numberOfLines={2}>{product.title}</Text>
        
        {/* Informations supplémentaires (marque, modèle, spécifications) */}
        <ProductCardInfo product={product} showBrand={true} showSpecs={true} />

        {/* Prix */}
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
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    overflow: 'hidden',
    marginBottom: 16,
    marginHorizontal: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 3,
    borderWidth: 0,
    borderColor: 'transparent',
    position: 'relative',
  },
  colorBorder: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    borderRadius: 16,
    borderWidth: 2,
    zIndex: 0,
  },
  imageContainer: {
    width: '100%',
    height: 160,
    position: 'relative',
    backgroundColor: '#F9FAFB',
    zIndex: 1,
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
    zIndex: 2,
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
    left: 8,
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
    zIndex: 2,
  },
  cartBadgeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '800',
    marginLeft: 2,
  },
  unavailableBadge: {
    position: 'absolute',
    top: 8,
    left: 8,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    zIndex: 2,
  },
  unavailableBadgeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '700',
  },
  colorIndicator: {
    position: 'absolute',
    bottom: 8,
    right: 8,
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
    elevation: 3,
    zIndex: 2,
  },
  infoContainer: {
    padding: 12,
    zIndex: 1,
  },
  title: {
    fontSize: 14,
    fontWeight: '700',
    color: COLORS.TEXT,
    marginBottom: 6,
    lineHeight: 18,
    minHeight: 36,
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

export default ProductCardPhone;

