import React from 'react';
import { Image, StyleSheet, View, Text } from 'react-native';
import { COLORS } from '../utils/constants';

interface LogoProps {
  size?: 'small' | 'medium' | 'large';
  dimension?: number;
  showText?: boolean;
  textColor?: string;
  customText?: string;
}

export const Logo: React.FC<LogoProps> = ({
  size = 'medium',
  dimension,
  showText = true,
  textColor = COLORS.PRIMARY,
  customText,
}) => {
  const sizeStyles = {
    small: { width: 50, height: 50 },
    medium: { width: 70, height: 70 },
    large: { width: 140, height: 140 },
  };

  const currentSize = dimension ? { width: dimension, height: dimension } : sizeStyles[size];

  return (
    <View style={styles.container}>
      <Image
        source={require('../../assets/logo.png')}
        style={[styles.logo, currentSize]}
        resizeMode="contain"
      />
      {showText && (
        <Text style={[styles.appTitle, { color: textColor }]}>
          {customText || 'BoliBana Sugu'}
        </Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    maxWidth: '100%',
    overflow: 'hidden',
    flexShrink: 1,
  },
  logo: {
    maxWidth: '100%',
    maxHeight: '100%',
    flexShrink: 1,
  },
  appTitle: {
    fontWeight: 'bold',
    marginTop: -4,
    fontSize: 22,
    letterSpacing: 1,
    textTransform: 'uppercase',
  },
});

export default Logo;
