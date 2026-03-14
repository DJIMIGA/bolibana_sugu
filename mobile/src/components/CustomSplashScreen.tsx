import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Text, Animated, Easing } from 'react-native';
import { COLORS, BRAND } from '../utils/constants';
import { BoliBanaLogoIcon } from './BoliBanaLogo';
import TricolorBar from './TricolorBar';

export const CustomSplashScreen: React.FC = () => {
  const logoScale = useRef(new Animated.Value(0)).current;
  const textOpacity = useRef(new Animated.Value(0)).current;
  const textSlide = useRef(new Animated.Value(20)).current;
  const suguOpacity = useRef(new Animated.Value(0)).current;
  const barOpacity = useRef(new Animated.Value(0)).current;
  const taglineOpacity = useRef(new Animated.Value(0)).current;
  const dotScale1 = useRef(new Animated.Value(0.3)).current;
  const dotScale2 = useRef(new Animated.Value(0.3)).current;
  const dotScale3 = useRef(new Animated.Value(0.3)).current;

  useEffect(() => {
    Animated.sequence([
      Animated.spring(logoScale, {
        toValue: 1,
        friction: 5,
        tension: 40,
        useNativeDriver: true,
      }),
      Animated.parallel([
        Animated.timing(textOpacity, { toValue: 1, duration: 400, useNativeDriver: true }),
        Animated.timing(textSlide, { toValue: 0, duration: 400, easing: Easing.out(Easing.cubic), useNativeDriver: true }),
      ]),
      Animated.timing(suguOpacity, { toValue: 1, duration: 300, useNativeDriver: true }),
      Animated.timing(barOpacity, { toValue: 1, duration: 200, useNativeDriver: true }),
      Animated.timing(taglineOpacity, { toValue: 1, duration: 400, useNativeDriver: true }),
    ]).start();

    const loopDots = () => {
      Animated.loop(
        Animated.sequence([
          Animated.timing(dotScale1, { toValue: 1, duration: 300, useNativeDriver: true }),
          Animated.timing(dotScale1, { toValue: 0.3, duration: 300, useNativeDriver: true }),
          Animated.timing(dotScale2, { toValue: 1, duration: 300, useNativeDriver: true }),
          Animated.timing(dotScale2, { toValue: 0.3, duration: 300, useNativeDriver: true }),
          Animated.timing(dotScale3, { toValue: 1, duration: 300, useNativeDriver: true }),
          Animated.timing(dotScale3, { toValue: 0.3, duration: 300, useNativeDriver: true }),
        ])
      ).start();
    };
    setTimeout(loopDots, 2000);
  }, []);

  return (
    <View style={styles.container}>
      <Animated.View style={{ transform: [{ scale: logoScale }] }}>
        <BoliBanaLogoIcon size={120} />
      </Animated.View>

      <Animated.View style={[styles.wordmark, { opacity: textOpacity, transform: [{ translateY: textSlide }] }]}>
        <Text style={styles.wordBoli}>Boli</Text>
        <Text style={styles.wordBana}>Bana</Text>
      </Animated.View>

      <Animated.Text style={[styles.sugu, { opacity: suguOpacity }]}>
        {BRAND.SHORT_NAME.toUpperCase()}
      </Animated.Text>

      <Animated.View style={{ opacity: barOpacity, marginTop: 10 }}>
        <TricolorBar width={130} height={3.5} />
      </Animated.View>

      <Animated.Text style={[styles.tagline, { opacity: taglineOpacity }]}>
        {BRAND.TAGLINE}
      </Animated.Text>

      <View style={styles.loader}>
        <Animated.View style={[styles.dot, styles.dotGreen, { transform: [{ scale: dotScale1 }] }]} />
        <Animated.View style={[styles.dot, styles.dotGold, { transform: [{ scale: dotScale2 }] }]} />
        <Animated.View style={[styles.dot, styles.dotRed, { transform: [{ scale: dotScale3 }] }]} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.PRIMARY,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  wordmark: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginTop: 16,
  },
  wordBoli: {
    fontSize: 44,
    fontWeight: '700',
    color: '#FFFFFF',
    fontFamily: 'Georgia',
    letterSpacing: -2,
  },
  wordBana: {
    fontSize: 44,
    fontWeight: '700',
    color: '#FFD700',
    fontFamily: 'Georgia',
    letterSpacing: -2,
  },
  sugu: {
    color: '#C0392B',
    fontFamily: 'sans-serif',
    fontSize: 14,
    fontWeight: '700',
    letterSpacing: 7,
    marginTop: 6,
  },
  tagline: {
    color: 'rgba(255,255,255,0.4)',
    fontSize: 11,
    marginTop: 14,
    textAlign: 'center',
  },
  loader: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 44,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  dotGreen: { backgroundColor: 'rgba(255,255,255,0.3)' },
  dotGold: { backgroundColor: 'rgba(255,255,255,0.3)' },
  dotRed: { backgroundColor: 'rgba(255,255,255,0.3)' },
});
