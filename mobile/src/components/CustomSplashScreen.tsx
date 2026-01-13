import React from 'react';
import { View, Image, StyleSheet, Text } from 'react-native';
import { COLORS } from '../utils/constants';

export const CustomSplashScreen: React.FC = () => {
  return (
    <View style={styles.container}>
      <Image
        source={require('../../assets/logo.png')}
        style={styles.logo}
        resizeMode="contain"
      />
      <Text style={styles.appName}>BoliBana Sugu</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  logo: {
    width: 25,
    height: 25,
    marginBottom: 8,
    maxWidth: '100%',
    maxHeight: '100%',
  },
  appName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.PRIMARY,
    letterSpacing: 1,
    textTransform: 'uppercase',
    textAlign: 'center',
  },
});
