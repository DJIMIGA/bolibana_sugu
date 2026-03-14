import React from 'react';
import { StyleSheet, View, Text } from 'react-native';
import { COLORS, BRAND } from '../utils/constants';
import BoliBanaLogo from './BoliBanaLogo';

interface LogoProps {
  size?: 'small' | 'medium' | 'large';
  dimension?: number;
  showText?: boolean;
  textColor?: string;
  customText?: string;
  variant?: 'icon' | 'navbar' | 'full';
}

export const Logo: React.FC<LogoProps> = ({
  size = 'medium',
  dimension,
  showText = true,
  textColor = COLORS.PRIMARY,
  customText,
  variant = 'icon',
}) => {
  const sizeMap = { small: 40, medium: 60, large: 100 };
  const currentDimension = dimension || sizeMap[size];

  return (
    <View style={styles.container}>
      <BoliBanaLogo size={currentDimension} variant={variant} />
      {showText && (
        <Text style={[styles.appTitle, { color: textColor }]}>
          {customText || BRAND.FULL_NAME}
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
  appTitle: {
    fontWeight: 'bold',
    marginTop: -4,
    fontSize: 22,
    letterSpacing: 1,
    textTransform: 'uppercase',
  },
});

export default Logo;
