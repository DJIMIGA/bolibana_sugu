import React from 'react';
import { Image, StyleSheet, View, Text } from 'react-native';
import { COLORS } from '../utils/constants';

interface LogoProps {
  size?: 'small' | 'medium' | 'large';
  showText?: boolean;
  textColor?: string;
}

export const Logo: React.FC<LogoProps> = ({ size = 'medium', showText = true, textColor = COLORS.PRIMARY }) => {
  const sizeStyles = {
    small: { width: 40, height: 40 },
    medium: { width: 60, height: 60 },
    large: { width: 80, height: 80 },
  };

  const currentSize = sizeStyles[size];

  return (
    <View style={styles.container}>
      <Image
        source={require('../../assets/logo.png')}
        style={[styles.logo, currentSize]}
        resizeMode="contain"
      />
      {showText && (
        <Text style={[styles.appTitle, { color: textColor }]}>BoliBana Sugu</Text>
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
