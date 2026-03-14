import React, { useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { TouchableOpacity } from 'react-native';
import QRCode from 'react-native-qrcode-svg';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchLoyaltyInfoAsync } from '../store/slices/authSlice';
import { COLORS } from '../utils/constants';
import { formatPrice, formatDate } from '../utils/helpers';
import { LoyaltyTier, LoyaltyHistoryItem } from '../types';

const LoyaltyScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigation = useNavigation();
  const insets = useSafeAreaInsets();
  const {
    loyaltyInfo,
    isLoadingLoyalty,
    isLoyaltyStale,
    loyaltyLastUpdated,
  } = useAppSelector((state) => state.auth);

  const [refreshing, setRefreshing] = React.useState(false);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await dispatch(fetchLoyaltyInfoAsync()).unwrap();
    } catch (_) {
      // Erreur silencieuse
    }
    setRefreshing(false);
  }, [dispatch]);

  const loyaltyProgressPercent = loyaltyInfo
    ? Math.min(100, Math.max(0, (loyaltyInfo.progress_to_next_tier || 0) * 100))
    : 0;

  const loyaltyLastUpdatedLabel = loyaltyLastUpdated
    ? new Date(loyaltyLastUpdated).toLocaleString('fr-FR')
    : null;

  const getTierIcon = (tierName: string, isCurrentOrPast: boolean) => {
    if (isCurrentOrPast) {
      return <Ionicons name="checkmark-circle" size={20} color={COLORS.PRIMARY} />;
    }
    return <Ionicons name="ellipse-outline" size={20} color={COLORS.TEXT_SECONDARY} />;
  };

  const formatShortDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  if (!loyaltyInfo) {
    return (
      <View style={[styles.container, { paddingTop: insets.top }]}>
        <View style={[styles.header, { paddingTop: insets.top + 12 }]}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#FFFFFF" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Programme de Fidelite</Text>
          <View style={{ width: 40 }} />
        </View>
        <View style={styles.emptyContainer}>
          <Ionicons name="trophy-outline" size={64} color={COLORS.TEXT_SECONDARY} />
          <Text style={styles.emptyText}>Aucune information de fidelite disponible</Text>
        </View>
      </View>
    );
  }

  // Determiner les niveaux atteints
  const tierOrder = ['Bronze', 'Argent', 'Or', 'Diamant'];
  const currentTierIndex = tierOrder.indexOf(loyaltyInfo.loyalty_level);

  return (
    <View style={styles.container}>
      <ScrollView
        contentContainerStyle={{ paddingBottom: insets.bottom + 20 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Header */}
        <View style={[styles.header, { paddingTop: insets.top + 12 }]}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#FFFFFF" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Programme de Fidelite</Text>
          <View style={{ width: 40 }} />
        </View>

        {/* Carte principale */}
        <View style={styles.section}>
          <View style={[styles.mainCard, { borderColor: loyaltyInfo.loyalty_level_color }]}>
            {/* Badge niveau + numero */}
            <View style={styles.cardTopRow}>
              <View style={[styles.levelBadge, { backgroundColor: loyaltyInfo.loyalty_level_color }]}>
                <Ionicons name="trophy" size={18} color="#FFFFFF" style={{ marginRight: 6 }} />
                <Text style={styles.levelBadgeText}>{loyaltyInfo.loyalty_level}</Text>
              </View>
              <Text style={styles.fidelysNumber}>
                N° <Text style={styles.fidelysNumberMono}>{loyaltyInfo.fidelys_number}</Text>
              </Text>
            </View>

            {/* Stats row */}
            <View style={styles.statsRow}>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{loyaltyInfo.loyalty_points}</Text>
                <Text style={styles.statLabel}>Points</Text>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{loyaltyInfo.total_orders}</Text>
                <Text style={styles.statLabel}>Commandes</Text>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{formatPrice(loyaltyInfo.total_spent)}</Text>
                <Text style={styles.statLabel}>Depense</Text>
              </View>
            </View>

            {/* Barre de progression */}
            {loyaltyInfo.next_level && (
              <View style={styles.progressSection}>
                <View style={styles.progressBar}>
                  <View
                    style={[
                      styles.progressFill,
                      {
                        width: `${loyaltyProgressPercent}%`,
                        backgroundColor: loyaltyInfo.loyalty_level_color,
                      },
                    ]}
                  />
                </View>
                <Text style={styles.progressText}>
                  Plus que {loyaltyInfo.points_needed} pts pour {loyaltyInfo.next_level}
                </Text>
              </View>
            )}

            {/* QR Code */}
            {loyaltyInfo.qr_payload && (
              <View style={styles.qrContainer}>
                <QRCode
                  value={loyaltyInfo.qr_payload}
                  size={140}
                  backgroundColor="#FFFFFF"
                  color="#111827"
                />
                <Text style={styles.qrLabel}>Presenter au magasin</Text>
              </View>
            )}
          </View>
        </View>

        {/* Section Paliers */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Paliers du programme</Text>
          {loyaltyInfo.loyalty_tiers && loyaltyInfo.loyalty_tiers.length > 0 ? (
            <View style={styles.tiersCard}>
              {loyaltyInfo.loyalty_tiers.map((tier: LoyaltyTier, index: number) => {
                const tierIdx = tierOrder.indexOf(tier.name);
                const isCurrentTier = tier.name === loyaltyInfo.loyalty_level;
                const isAchieved = tierIdx <= currentTierIndex;

                return (
                  <View
                    key={tier.name}
                    style={[
                      styles.tierRow,
                      index < loyaltyInfo.loyalty_tiers.length - 1 && styles.tierRowBorder,
                    ]}
                  >
                    <View style={styles.tierLeft}>
                      {getTierIcon(tier.name, isAchieved)}
                      <View style={[styles.tierColorDot, { backgroundColor: tier.color }]} />
                      <Text
                        style={[
                          styles.tierName,
                          isCurrentTier && styles.tierNameCurrent,
                          !isAchieved && styles.tierNameFuture,
                        ]}
                      >
                        {tier.name}
                      </Text>
                    </View>
                    <View style={styles.tierRight}>
                      <Text style={styles.tierPoints}>{tier.min_points} pts</Text>
                      {isCurrentTier && (
                        <View style={[styles.currentBadge, { backgroundColor: tier.color }]}>
                          <Text style={styles.currentBadgeText}>actuel</Text>
                        </View>
                      )}
                    </View>
                  </View>
                );
              })}
            </View>
          ) : (
            <Text style={styles.emptySubText}>Aucun palier disponible</Text>
          )}
        </View>

        {/* Section Historique */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Historique</Text>
          {loyaltyInfo.history && loyaltyInfo.history.length > 0 ? (
            <View style={styles.historyCard}>
              {loyaltyInfo.history.map((item: LoyaltyHistoryItem, index: number) => (
                <View
                  key={index}
                  style={[
                    styles.historyRow,
                    index < loyaltyInfo.history.length - 1 && styles.historyRowBorder,
                  ]}
                >
                  <View style={styles.historyLeft}>
                    <Text style={styles.historyDate}>{formatShortDate(item.created_at)}</Text>
                    <Text style={styles.historyLevel}>{item.loyalty_level}</Text>
                  </View>
                  <View style={styles.historyRight}>
                    <Text style={styles.historyPoints}>{item.loyalty_points} pts</Text>
                    <Text style={styles.historyOrders}>
                      {item.total_orders} cmd • {formatPrice(item.total_spent)}
                    </Text>
                  </View>
                </View>
              ))}
            </View>
          ) : (
            <Text style={styles.emptySubText}>Aucun historique disponible</Text>
          )}
        </View>

        {/* Messages motivationnels */}
        {loyaltyInfo.messages && loyaltyInfo.messages.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Messages</Text>
            <View style={styles.messagesCard}>
              {loyaltyInfo.messages.map((msg: string, index: number) => (
                <View key={index} style={styles.messageRow}>
                  <Ionicons name="chatbubble-outline" size={16} color={COLORS.PRIMARY} />
                  <Text style={styles.messageText}>{msg}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Indicateur fraicheur */}
        {loyaltyLastUpdatedLabel && (
          <View style={styles.metaContainer}>
            <Text style={styles.metaText}>
              {isLoyaltyStale ? 'Hors ligne' : 'A jour'} • {loyaltyLastUpdatedLabel}
            </Text>
          </View>
        )}

      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.BACKGROUND,
  },
  header: {
    backgroundColor: COLORS.PRIMARY,
    paddingBottom: 16,
    paddingHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
    gap: 16,
  },
  emptyText: {
    fontSize: 16,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
  },
  emptySubText: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    paddingVertical: 16,
  },
  section: {
    backgroundColor: '#FFFFFF',
    marginTop: 12,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 12,
  },
  // Carte principale
  mainCard: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 16,
    borderWidth: 2,
  },
  cardTopRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  levelBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  levelBadgeText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  fidelysNumber: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
    fontWeight: '600',
  },
  fidelysNumberMono: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  // Stats
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.PRIMARY,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
  },
  statDivider: {
    width: 1,
    backgroundColor: '#E5E7EB',
  },
  // Progression
  progressSection: {
    marginTop: 14,
  },
  progressBar: {
    height: 10,
    backgroundColor: '#E5E7EB',
    borderRadius: 5,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 5,
  },
  progressText: {
    fontSize: 13,
    color: COLORS.TEXT_SECONDARY,
    marginTop: 8,
    textAlign: 'center',
  },
  // QR
  qrContainer: {
    marginTop: 16,
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  qrLabel: {
    marginTop: 10,
    fontSize: 13,
    color: COLORS.TEXT_SECONDARY,
  },
  // Paliers
  tiersCard: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 4,
  },
  tierRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    paddingHorizontal: 12,
  },
  tierRowBorder: {
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  tierLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  tierColorDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  tierName: {
    fontSize: 15,
    fontWeight: '500',
    color: COLORS.TEXT,
  },
  tierNameCurrent: {
    fontWeight: '700',
    color: COLORS.PRIMARY,
  },
  tierNameFuture: {
    color: COLORS.TEXT_SECONDARY,
  },
  tierRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  tierPoints: {
    fontSize: 13,
    color: COLORS.TEXT_SECONDARY,
  },
  currentBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10,
  },
  currentBadgeText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: '600',
  },
  // Historique
  historyCard: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 4,
  },
  historyRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 12,
  },
  historyRowBorder: {
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  historyLeft: {
    gap: 2,
  },
  historyDate: {
    fontSize: 13,
    color: COLORS.TEXT_SECONDARY,
  },
  historyLevel: {
    fontSize: 15,
    fontWeight: '600',
    color: COLORS.TEXT,
  },
  historyRight: {
    alignItems: 'flex-end',
    gap: 2,
  },
  historyPoints: {
    fontSize: 15,
    fontWeight: '600',
    color: COLORS.PRIMARY,
  },
  historyOrders: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
  },
  // Messages
  messagesCard: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 12,
    gap: 10,
  },
  messageRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 8,
  },
  messageText: {
    flex: 1,
    fontSize: 14,
    color: COLORS.TEXT,
    lineHeight: 20,
  },
  // Meta
  metaContainer: {
    padding: 16,
    alignItems: 'center',
  },
  metaText: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
  },
});

export default LoyaltyScreen;
