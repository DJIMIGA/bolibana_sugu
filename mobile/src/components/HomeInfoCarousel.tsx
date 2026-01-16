import React, { useEffect, useRef, useState } from 'react';
import { Animated, Text, View, StyleSheet } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { COLORS } from '../utils/constants';

const HomeInfoCarousel: React.FC = () => {
  const [currentInfoCardIndex, setCurrentInfoCardIndex] = useState(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const fadeAnim = useRef(new Animated.Value(1)).current;
  const slideAnim = useRef(new Animated.Value(0)).current;

  const startAutoScroll = React.useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    intervalRef.current = setInterval(() => {
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 0,
          duration: 400,
          useNativeDriver: true,
        }),
        Animated.timing(slideAnim, {
          toValue: -20,
          duration: 400,
          useNativeDriver: true,
        }),
      ]).start(() => {
        slideAnim.setValue(20);
        setCurrentInfoCardIndex((prevIndex) => (prevIndex + 1) % 3);
        Animated.parallel([
          Animated.timing(fadeAnim, {
            toValue: 1,
            duration: 400,
            useNativeDriver: true,
          }),
          Animated.timing(slideAnim, {
            toValue: 0,
            duration: 400,
            useNativeDriver: true,
          }),
        ]).start();
      });
    }, 3000);
  }, [fadeAnim, slideAnim]);

  useEffect(() => {
    startAutoScroll();
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [startAutoScroll]);

  return (
    <View style={styles.combinedSection}>
      <View style={styles.combinedRow}>
        <Animated.View
          style={[
            styles.infoCard,
            {
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }],
              flex: 1,
            },
          ]}
        >
          {currentInfoCardIndex === 0 && (
            <>
              <MaterialIcons name="local-shipping" size={24} color={COLORS.PRIMARY} />
              <View style={styles.infoCardContent}>
                <Text style={styles.infoCardTitle}>Livraisons gratuites</Text>
                <Text style={styles.infoCardSubtitle}>sur tous les articles Salam</Text>
              </View>
            </>
          )}
          {currentInfoCardIndex === 1 && (
            <>
              <MaterialIcons name="assignment-return" size={24} color={COLORS.PRIMARY} />
              <View style={styles.infoCardContent}>
                <Text style={styles.infoCardTitle}>Retours gratuits</Text>
                <Text style={styles.infoCardSubtitle}>sur des milliers de produits</Text>
              </View>
            </>
          )}
          {currentInfoCardIndex === 2 && (
            <>
              <MaterialIcons name="flash-on" size={24} color={COLORS.SECONDARY} />
              <View style={styles.infoCardContent}>
                <Text style={styles.infoCardTitle}>Livraison rapide</Text>
                <Text style={styles.infoCardSubtitle}>remboursement si défectueux</Text>
              </View>
            </>
          )}
        </Animated.View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  combinedSection: {
    paddingHorizontal: 12,
    paddingTop: 0,
    paddingBottom: 4,
  },
  combinedRow: {
    flexDirection: 'row',
    gap: 6,
    alignItems: 'stretch',
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    paddingVertical: 10,
    paddingHorizontal: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    marginRight: 0,
  },
  infoCardContent: {
    flex: 1,
    marginLeft: 12,
  },
  infoCardTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 4,
  },
  infoCardSubtitle: {
    fontSize: 11,
    color: COLORS.TEXT_SECONDARY,
    lineHeight: 16,
  },
});

export default React.memo(HomeInfoCarousel);
