import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { useConnectivity } from '../hooks/useConnectivity';
import { syncService } from '../services/syncService';
import { COLORS } from '../utils/constants';

export const OfflineBanner: React.FC = () => {
  const { isOnline } = useConnectivity();
  const [pendingCount, setPendingCount] = useState(0);
  const [slideAnim] = useState(new Animated.Value(-100));

  useEffect(() => {
    // Récupérer le nombre d'actions en attente
    const updatePendingCount = async () => {
      const count = await syncService.getPendingCount();
      setPendingCount(count);
    };

    updatePendingCount();

    // Écouter les changements de la file
    const listenerId = syncService.onQueueChange((count) => {
      setPendingCount(count);
    });

    return () => {
      syncService.offQueueChange(listenerId);
    };
  }, []);

  useEffect(() => {
    // Animer l'affichage/masquage du banner
    Animated.timing(slideAnim, {
      toValue: !isOnline || pendingCount > 0 ? 0 : -100,
      duration: 300,
      useNativeDriver: true,
    }).start();
  }, [isOnline, pendingCount, slideAnim]);

  if (isOnline && pendingCount === 0) {
    return null;
  }

  return (
    <Animated.View
      style={[
        styles.banner,
        {
          transform: [{ translateY: slideAnim }],
        },
      ]}
    >
      <View style={styles.content}>
        <Text style={styles.text}>
          {!isOnline
            ? 'Mode hors ligne'
            : `${pendingCount} action${pendingCount > 1 ? 's' : ''} en attente de synchronisation`}
        </Text>
        {pendingCount > 0 && (
          <Text style={styles.count}>{pendingCount}</Text>
        )}
      </View>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  banner: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    backgroundColor: COLORS.WARNING,
    paddingVertical: 8,
    paddingHorizontal: 16,
    zIndex: 1000,
    elevation: 5,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  count: {
    marginLeft: 8,
    backgroundColor: '#FFFFFF',
    color: COLORS.WARNING,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
    fontSize: 12,
    fontWeight: 'bold',
    overflow: 'hidden',
  },
});
