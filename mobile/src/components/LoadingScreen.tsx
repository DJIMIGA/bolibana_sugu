import React, { useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Easing,
  useWindowDimensions,
} from 'react-native';
import Svg, { Path, Circle, G, Text as SvgText } from 'react-native-svg';

const AnimatedG = Animated.createAnimatedComponent(G);

const AnimatedPath = Animated.createAnimatedComponent(Path);
const AnimatedCircle = Animated.createAnimatedComponent(Circle);

export const LoadingScreen: React.FC = () => {
  const { width: screenWidth, height: screenHeight } = useWindowDimensions();
  const SVG_SIZE = Math.min(screenWidth * 0.42, screenHeight * 0.22, 160);

  // Stroke draw
  const handleDash = useRef(new Animated.Value(130)).current;
  const basketDash = useRef(new Animated.Value(280)).current;

  // Dot scales (0 → 1 pop)
  const dotGreenScale = useRef(new Animated.Value(0)).current;
  const dotGoldScale = useRef(new Animated.Value(0)).current;
  const dotRedScale = useRef(new Animated.Value(0)).current;
  const badgeScale = useRef(new Animated.Value(0)).current;
  const wheelsOpacity = useRef(new Animated.Value(0)).current;

  // Text slide-up
  const boliOpacity = useRef(new Animated.Value(0)).current;
  const boliY = useRef(new Animated.Value(18)).current;
  const banaOpacity = useRef(new Animated.Value(0)).current;
  const banaY = useRef(new Animated.Value(18)).current;
  const suguOpacity = useRef(new Animated.Value(0)).current;

  // Tricolor bars scaleX
  const triGreen = useRef(new Animated.Value(0)).current;
  const triGold = useRef(new Animated.Value(0)).current;
  const triRed = useRef(new Animated.Value(0)).current;

  // Tagline + loader
  const taglineOpacity = useRef(new Animated.Value(0)).current;
  const loaderOpacity = useRef(new Animated.Value(0)).current;

  // Pulse dots
  const pulse1 = useRef(new Animated.Value(0)).current;
  const pulse2 = useRef(new Animated.Value(0)).current;
  const pulse3 = useRef(new Animated.Value(0)).current;

  const timing = (
    anim: Animated.Value,
    toValue: number,
    duration: number,
    delay: number,
    easing = Easing.out(Easing.cubic),
    useNativeDriver = true
  ) =>
    Animated.timing(anim, { toValue, duration, delay, easing, useNativeDriver });

  const spring = (anim: Animated.Value, delay: number) =>
    Animated.spring(anim, {
      toValue: 1,
      delay,
      friction: 5,
      tension: 200,
      useNativeDriver: true,
    });

  useEffect(() => {
    // Handle draw
    timing(handleDash, 0, 150, 0, Easing.out(Easing.cubic), false).start();
    // Basket draw
    timing(basketDash, 0, 200, 130, Easing.out(Easing.cubic), false).start();

    // Dots pop
    spring(dotGreenScale, 290).start();
    spring(dotGoldScale, 350).start();
    spring(dotRedScale, 410).start();
    spring(badgeScale, 470).start();

    // Wheels
    timing(wheelsOpacity, 1, 80, 520).start();

    // Text "Boli"
    Animated.parallel([
      timing(boliOpacity, 1, 160, 550),
      timing(boliY, 0, 160, 550, Easing.out(Easing.back(1.4))),
    ]).start();

    // Text "Bana"
    Animated.parallel([
      timing(banaOpacity, 1, 160, 620),
      timing(banaY, 0, 160, 620, Easing.out(Easing.back(1.4))),
    ]).start();

    // SUGU
    timing(suguOpacity, 1, 130, 720).start();

    // Tribar
    timing(triGreen, 1, 100, 800).start();
    timing(triGold, 1, 100, 860).start();
    timing(triRed, 1, 100, 920).start();

    // Tagline + loader
    timing(taglineOpacity, 1, 150, 970).start();
    timing(loaderOpacity, 1, 100, 1050).start(() => {
      const pulse = (anim: Animated.Value, delay: number) =>
        Animated.loop(
          Animated.sequence([
            Animated.timing(anim, {
              toValue: 1,
              duration: 350,
              delay,
              easing: Easing.inOut(Easing.ease),
              useNativeDriver: true,
            }),
            Animated.timing(anim, {
              toValue: 0,
              duration: 350,
              easing: Easing.inOut(Easing.ease),
              useNativeDriver: true,
            }),
          ])
        );
      pulse(pulse1, 0).start();
      pulse(pulse2, 120).start();
      pulse(pulse3, 240).start();
    });
  }, []);

  // Interpolate SVG transform strings for dot scale (useNativeDriver:false — SVG)
  const dotGreenT = dotGreenScale.interpolate({ inputRange: [0, 1], outputRange: ['scale(0)', 'scale(1)'] });
  const dotGoldT = dotGoldScale.interpolate({ inputRange: [0, 1], outputRange: ['scale(0)', 'scale(1)'] });
  const dotRedT = dotRedScale.interpolate({ inputRange: [0, 1], outputRange: ['scale(0)', 'scale(1)'] });
  const badgeT = badgeScale.interpolate({ inputRange: [0, 1], outputRange: ['scale(0)', 'scale(1)'] });

  // Pulse dot scale + color
  const p1Scale = pulse1.interpolate({ inputRange: [0, 1], outputRange: [1, 1.45] });
  const p2Scale = pulse2.interpolate({ inputRange: [0, 1], outputRange: [1, 1.45] });
  const p3Scale = pulse3.interpolate({ inputRange: [0, 1], outputRange: [1, 1.45] });

  const AnimatedView = Animated.View;

  return (
    <View style={styles.container}>
      {/* Basket SVG — viewBox 128×120 identique au splash HTML */}
      <Svg
        viewBox="0 0 128 120"
        width={SVG_SIZE}
        height={SVG_SIZE * (120 / 128)}
      >
        {/* Anse */}
        <AnimatedPath
          d="M28 52 Q28 14 64 14 Q100 14 100 52"
          fill="none"
          stroke="rgba(255,255,255,0.92)"
          strokeWidth={5.5}
          strokeLinecap="round"
          strokeDasharray={130}
          strokeDashoffset={handleDash as any}
        />

        {/* Corps panier */}
        <AnimatedPath
          d="M16 52 L26 96 Q26 102 34 102 L94 102 Q102 102 102 96 L112 52 Z"
          fill="none"
          stroke="rgba(255,255,255,0.92)"
          strokeWidth={5.5}
          strokeLinejoin="round"
          strokeLinecap="round"
          strokeDasharray={280}
          strokeDashoffset={basketDash as any}
        />

        {/* Pastille verte — translate vers centre puis scale */}
        <G transform="translate(42, 74)">
          <AnimatedCircle cx={0} cy={0} r={12} fill="#009A00" transform={dotGreenT as any} />
        </G>

        {/* Pastille or */}
        <G transform="translate(64, 74)">
          <AnimatedCircle cx={0} cy={0} r={12} fill="#FFD700" stroke="#D4A017" strokeWidth={1.2} transform={dotGoldT as any} />
        </G>

        {/* Pastille rouge */}
        <G transform="translate(86, 74)">
          <AnimatedCircle cx={0} cy={0} r={12} fill="#C0392B" transform={dotRedT as any} />
        </G>

        {/* Badge notification */}
        <G transform="translate(106, 34)">
          <AnimatedG transform={badgeT as any}>
            <Circle cx={0} cy={0} r={14} fill="#C0392B" />
            <SvgText
              x={0} y={5.5}
              fontSize={14} fontWeight="700"
              fill="white" fontFamily="sans-serif"
              textAnchor="middle"
            >3</SvgText>
          </AnimatedG>
        </G>

        {/* Roues */}
        <G opacity={wheelsOpacity as any}>
          <Circle cx={34} cy={111} r={7} fill="none" stroke="rgba(255,255,255,0.6)" strokeWidth={2.5} />
          <Circle cx={34} cy={111} r={2.2} fill="rgba(255,255,255,0.6)" />
          <Circle cx={94} cy={111} r={7} fill="none" stroke="rgba(255,255,255,0.6)" strokeWidth={2.5} />
          <Circle cx={94} cy={111} r={2.2} fill="rgba(255,255,255,0.6)" />
        </G>
      </Svg>

      {/* Nom BoliBana */}
      <View style={styles.wordmark}>
        <Animated.Text
          style={[styles.wordBoli, { opacity: boliOpacity, transform: [{ translateY: boliY }] }]}
        >
          Boli
        </Animated.Text>
        <Animated.Text
          style={[styles.wordBana, { opacity: banaOpacity, transform: [{ translateY: banaY }] }]}
        >
          Bana
        </Animated.Text>
      </View>

      {/* SUGU */}
      <Animated.Text style={[styles.sugu, { opacity: suguOpacity }]}>SUGU</Animated.Text>

      {/* Barre tricolore animée */}
      <View style={styles.tribar}>
        <Animated.View style={[styles.tribarSegment, { backgroundColor: 'rgba(255,255,255,0.75)', transform: [{ scaleX: triGreen }] }]} />
        <Animated.View style={[styles.tribarSegment, { backgroundColor: '#FFD700', transform: [{ scaleX: triGold }] }]} />
        <Animated.View style={[styles.tribarSegment, { backgroundColor: '#C0392B', transform: [{ scaleX: triRed }] }]} />
      </View>

      {/* Tagline */}
      <Animated.Text style={[styles.tagline, { opacity: taglineOpacity }]}>
        Votre intermédiaire expert du marché
      </Animated.Text>

      {/* Loader dots */}
      <Animated.View style={[styles.loader, { opacity: loaderOpacity }]}>
        <Animated.View style={[styles.loaderDot, { transform: [{ scale: p1Scale }] }]} />
        <Animated.View style={[styles.loaderDot, { transform: [{ scale: p2Scale }] }]} />
        <Animated.View style={[styles.loaderDot, { transform: [{ scale: p3Scale }] }]} />
      </Animated.View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#008000',
    alignItems: 'center',
    justifyContent: 'center',
  },
  wordmark: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  wordBoli: {
    color: '#FFFFFF',
    fontSize: 52,
    fontWeight: '700',
    letterSpacing: -2,
  },
  wordBana: {
    color: '#FFD700',
    fontSize: 52,
    fontWeight: '700',
    letterSpacing: -2,
  },
  sugu: {
    color: '#C0392B',
    fontSize: 15,
    fontWeight: '700',
    letterSpacing: 8,
    marginTop: 6,
  },
  tribar: {
    flexDirection: 'row',
    gap: 5,
    marginTop: 12,
  },
  tribarSegment: {
    width: 44,
    height: 3.5,
    borderRadius: 2,
  },
  tagline: {
    color: 'rgba(255,255,255,0.4)',
    fontSize: 11,
    letterSpacing: 0.4,
    marginTop: 14,
  },
  loader: {
    flexDirection: 'row',
    gap: 7,
    marginTop: 44,
  },
  loaderDot: {
    width: 7,
    height: 7,
    borderRadius: 3.5,
    backgroundColor: '#FFD700',
  },
});
