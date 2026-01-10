import React, { useEffect, useRef } from 'react';
import { View, ActivityIndicator, StyleSheet, Text, Animated, Easing, Dimensions } from 'react-native';
import { COLORS } from '../utils/constants';
import Logo from './Logo';

const { width } = Dimensions.get('window');

export const LoadingScreen: React.FC = () => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(20)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 1000,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 1000,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
    ]).start();
  }, [fadeAnim, slideAnim]);

  return (
    <View style={styles.container}>
      <Animated.View style={[
        styles.content,
        {
          opacity: fadeAnim,
          transform: [{ translateY: slideAnim }]
        }
      ]}>
        <View style={styles.logoWrapper}>
          <Logo size="large" showText={false} />
        </View>
        
        <View style={styles.textContainer}>
          <Text style={styles.brandMain}>BOLIBANA</Text>
          <Text style={styles.brandSub}>SUGU</Text>
        </View>

        <View style={styles.loaderContainer}>
          <ActivityIndicator size="small" color={COLORS.PRIMARY} />
          <Text style={styles.loadingText}>Chargement sécurisé...</Text>
        </View>
      </Animated.View>
      
      <View style={styles.footer}>
        <Text style={styles.versionText}>v1.0.0</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    alignItems: 'center',
    width: width * 0.8,
  },
  logoWrapper: {
    marginBottom: 16,
    // Un léger effet de profondeur
    shadowColor: COLORS.PRIMARY,
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.1,
    shadowRadius: 20,
    elevation: 2,
  },
  textContainer: {
    alignItems: 'center',
    marginBottom: 60,
  },
  brandMain: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.TEXT_SECONDARY,
    letterSpacing: 6,
    marginBottom: 4,
  },
  brandSub: {
    fontSize: 42,
    fontWeight: '900',
    color: COLORS.PRIMARY,
    letterSpacing: 2,
  },
  loaderContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 30,
    borderWidth: 1,
    borderColor: '#F3F4F6',
  },
  loadingText: {
    marginLeft: 12,
    fontSize: 13,
    color: COLORS.TEXT_SECONDARY,
    fontWeight: '500',
  },
  footer: {
    position: 'absolute',
    bottom: 40,
  },
  versionText: {
    fontSize: 11,
    color: '#D1D5DB',
    fontWeight: '700',
    letterSpacing: 1,
  },
});
