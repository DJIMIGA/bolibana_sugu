import React, { useCallback } from 'react';
import { FlatList, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import { Product } from '../types';
import { COLORS } from '../utils/constants';
import { formatPrice, getProductImageUrl } from '../utils/helpers';
import ProductCardInfo from './ProductCardInfo';
import ProductImage from './ProductImage';

interface HomeProductSectionProps {
  title: string;
  subtitle: string;
  iconName: keyof typeof MaterialIcons.glyphMap;
  iconColor: string;
  products: Product[];
  showNewBadge?: boolean;
  showSeeAll?: boolean;
  onPressSeeAll?: () => void;
  onPressProduct: (product: Product) => void;
}

const CARD_WIDTH = 150;
const CARD_GAP = 6;
const ITEM_LENGTH = CARD_WIDTH + CARD_GAP;

const HomeProductSection: React.FC<HomeProductSectionProps> = ({
  title,
  subtitle,
  iconName,
  iconColor,
  products,
  showNewBadge = false,
  showSeeAll = false,
  onPressSeeAll,
  onPressProduct,
}) => {
  const renderItem = useCallback(
    ({ item }: { item: Product }) => {
      const hasDiscount = item.discount_price && item.discount_price < item.price && item.discount_price > 0;
      const discountPercentage =
        item.discount_price && item.price > 0
          ? Math.round(((item.price - item.discount_price) / item.price) * 100)
          : 0;
      const imageUrl = getProductImageUrl(item);

      return (
        <TouchableOpacity
          style={styles.promoCard}
          onPress={() => onPressProduct(item)}
          activeOpacity={0.8}
        >
          {discountPercentage > 0 && (
            <View style={styles.promoBadge}>
              <View style={styles.promoBadgeInner}>
                <Text style={styles.promoBadgeText}>-{discountPercentage}%</Text>
              </View>
              <View style={styles.promoBadgeTriangle} />
            </View>
          )}
          {showNewBadge && (
            <View style={styles.newBadge}>
              <Text style={styles.newBadgeText}>NOUVEAU</Text>
            </View>
          )}
          <View style={styles.promoImageContainer}>
            <ProductImage
              uri={imageUrl}
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
            <Text style={styles.promoProductTitle} numberOfLines={1}>
              {item.title}
            </Text>
            <ProductCardInfo product={item} showBrand={true} showSpecs={false} compact={true} />
            <View style={styles.promoPriceContainer}>
              <View style={styles.promoPriceRow}>
                <Text style={styles.promoNewPrice}>{formatPrice(item.discount_price || item.price)}</Text>
                {item.is_salam && (
                  <View style={styles.salamBadge}>
                    <Text style={styles.salamBadgeText}>SALAM</Text>
                  </View>
                )}
              </View>
              {hasDiscount && <Text style={styles.promoOldPrice}>{formatPrice(item.price)}</Text>}
            </View>
          </View>
        </TouchableOpacity>
      );
    },
    [onPressProduct, showNewBadge]
  );

  return (
    <View style={styles.promoSection}>
      <View style={styles.promoHeaderInline}>
        <View style={styles.promoHeaderIconContainer}>
          <MaterialIcons name={iconName} size={20} color={iconColor} />
        </View>
        <View style={styles.promoHeaderTextContainer}>
          <Text style={styles.promoSectionTitleInline}>{title}</Text>
          <Text style={styles.promoSectionSubtitleInline}>{subtitle}</Text>
          {showSeeAll && onPressSeeAll && (
            <TouchableOpacity style={styles.promoSeeAllButtonInline} onPress={onPressSeeAll}>
              <Text style={styles.promoSeeAllTextInline}>Voir</Text>
              <Ionicons name="chevron-forward" size={14} color={COLORS.PRIMARY} />
            </TouchableOpacity>
          )}
        </View>
      </View>
      <FlatList
        data={products}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderItem}
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.promoCarouselContent}
        snapToInterval={ITEM_LENGTH}
        decelerationRate="fast"
        snapToAlignment="start"
        pagingEnabled={false}
        removeClippedSubviews={false}
        initialNumToRender={8}
        maxToRenderPerBatch={8}
        windowSize={7}
        getItemLayout={(_, index) => ({
          length: ITEM_LENGTH,
          offset: ITEM_LENGTH * index,
          index,
        })}
      />
    </View>
  );
};

const styles = StyleSheet.create({
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
  promoHeaderIconContainer: {
    width: 36,
    height: 36,
    borderRadius: 8,
    backgroundColor: '#FEE2E2',
    justifyContent: 'center',
    alignItems: 'center',
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
  promoCarouselContent: {
    paddingLeft: 8,
    paddingRight: 8,
    paddingBottom: 2,
    alignItems: 'flex-start',
  },
  promoCard: {
    width: CARD_WIDTH,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginRight: CARD_GAP,
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
    fontSize: 17,
    fontWeight: '900',
    color: COLORS.DANGER,
    letterSpacing: -0.3,
  },
  promoOldPrice: {
    fontSize: 11,
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
});

export default React.memo(HomeProductSection);
