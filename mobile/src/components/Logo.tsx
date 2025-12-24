import React from 'react';
import { Image, StyleSheet, View, Text } from 'react-native';

interface LogoProps {
  size?: 'small' | 'medium' | 'large';
  showText?: boolean;
}

export const Logo: React.FC<LogoProps> = ({ size = 'medium', showText = true }) => {
  const sizeStyles = {
    small: { width: 120, height: 40 },
    medium: { width: 180, height: 60 },
    large: { width: 240, height: 80 },
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
        <Text style={styles.sugu}>Sugu</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  logo: {
    // Les dimensions sont définies dynamiquement
  },
  sugu: {
    color: '#FFFFFF',
    fontWeight: '600',
    marginTop: 8,
    fontSize: 16,
    opacity: 0.9,
  },
});
