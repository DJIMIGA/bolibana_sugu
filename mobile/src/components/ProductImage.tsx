import React, { useEffect, useMemo, useState } from 'react';
import { Image } from 'expo-image';
import { ImageResizeMode, ImageStyle, StyleProp } from 'react-native';

interface ProductImageProps {
  uri?: string;
  style: StyleProp<ImageStyle>;
  resizeMode?: ImageResizeMode;
  fallback: React.ReactNode;
}

const ProductImage: React.FC<ProductImageProps> = ({ uri, style, resizeMode = 'cover', fallback }) => {
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    setHasError(false);
  }, [uri]);

  const source = useMemo(() => {
    if (!uri || hasError) return undefined;
    return { uri };
  }, [uri, hasError]);

  const contentFit = useMemo(() => {
    switch (resizeMode) {
      case 'contain':
      case 'cover':
      case 'stretch':
      case 'center':
        return resizeMode;
      default:
        return 'cover';
    }
  }, [resizeMode]);

  if (!source) {
    return <>{fallback}</>;
  }

  return (
    <Image
      source={source}
      style={style}
      contentFit={contentFit}
      cachePolicy="memory-disk"
      transition={0}
      onError={() => setHasError(true)}
    />
  );
};

export default React.memo(ProductImage);
