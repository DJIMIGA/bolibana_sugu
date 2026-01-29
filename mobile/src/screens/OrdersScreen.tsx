import React, { useEffect, useState, useMemo, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useFocusEffect, useRoute } from '@react-navigation/native';
import * as WebBrowser from 'expo-web-browser';
import { COLORS, API_ENDPOINTS } from '../utils/constants';
import { formatWeightQuantity, formatPrice } from '../utils/helpers';
import apiClient from '../services/api';
import { LoadingScreen } from '../components/LoadingScreen';

type OrderItemLite = {
  id: number;
  product_title: string;
  quantity: number;
  price: string;
  weight_unit?: string | null;
  is_weighted?: boolean;
};

type OrderLite = {
  id: number;
  order_number: string;
  status: string;
  status_label: string;
  total: string;
  created_at: string;
  items: OrderItemLite[];
};

type FilterStatus = 'all' | 'draft' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';

const FILTER_OPTIONS: { value: FilterStatus; label: string }[] = [
  { value: 'all', label: 'Toutes' },
  { value: 'draft', label: 'Brouillons' },
  { value: 'confirmed', label: 'Confirmées' },
  { value: 'shipped', label: 'Expédiées' },
  { value: 'delivered', label: 'Livrées' },
  { value: 'cancelled', label: 'Annulées' },
];

const OrdersScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute<any>();
  const [orders, setOrders] = useState<OrderLite[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState<FilterStatus>('all');
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const isScreenFocusedRef = useRef(false);

  const loadOrders = async (silent = false) => {
    try {
      if (!silent) {
        setIsLoading(true);
      }
      const response = await apiClient.get(API_ENDPOINTS.ORDERS);
      const raw = response.data;
      const list: OrderLite[] = Array.isArray(raw)
        ? raw
        : Array.isArray(raw?.results)
        ? raw.results
        : [];
      
      // Log détaillé des commandes avec leur statut
      console.log('[OrdersScreen] 📋 Commandes chargées:', {
        total: list.length,
        orders: list.map(order => ({
          id: order.id,
          order_number: order.order_number,
          status: order.status,
          status_label: order.status_label,
          total: order.total,
          created_at: order.created_at,
          items_count: order.items?.length || 0,
        })),
      });
      
      // Log répartition par statut
      const statusCounts = list.reduce((acc, order) => {
        acc[order.status] = (acc[order.status] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);
      console.log('[OrdersScreen] 📊 Répartition par statut:', statusCounts);
      
      setOrders(list);
      return list;
    } catch (error: any) {
      // Si c'est une erreur de mode hors ligne, gérer silencieusement
      if (error.isOfflineBlocked || error.code === 'OFFLINE_MODE_FORCED') {
        // En mode hors ligne, on peut garder les commandes déjà chargées ou vider la liste
        // setOrders([]); // Optionnel : vider si on veut forcer l'utilisateur à être en ligne
        return;
      }
      console.error('[OrdersScreen] ❌ Error loading orders:', error);
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadOrders(true);
  };

  // Rafraîchir quand l'écran est focus
  useFocusEffect(
    React.useCallback(() => {
      isScreenFocusedRef.current = true;
      loadOrders();

      // Tenter de fermer le WebBrowser s'il est encore ouvert (retour paiement sur Android)
      const closeBrowserTimer = setTimeout(async () => {
        try {
          await WebBrowser.dismissBrowser();
          console.log('[OrdersScreen] WebBrowser.dismissBrowser() appelé (écran Commandes focus)');
        } catch {
          // Ignorer si déjà fermé ou non supporté
        }
      }, 300);

      // Démarrer le polling automatique toutes les 30 secondes
      pollingIntervalRef.current = setInterval(() => {
        if (isScreenFocusedRef.current) {
          loadOrders(true); // Rafraîchir silencieusement
        }
      }, 30000); // 30 secondes

      return () => {
        clearTimeout(closeBrowserTimer);
        isScreenFocusedRef.current = false;
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
      };
    }, [])
  );

  // Après un retour de paiement, re-poll quelques fois pour récupérer le statut confirmé
  useEffect(() => {
    const targetOrderId = route?.params?.orderId ? Number(route.params.orderId) : undefined;
    const targetOrderNumber = route?.params?.orderNumber as string | undefined;
    if (!targetOrderId && !targetOrderNumber) {
      return;
    }

    let attempts = 0;
    let intervalId: NodeJS.Timeout | null = null;

    const pollOnce = async () => {
      attempts += 1;
      const list = await loadOrders(true);
      const match = (list || []).find((order) =>
        targetOrderId ? order.id === targetOrderId : order.order_number === targetOrderNumber
      );

      if (match && match.status !== 'draft') {
        console.log('[OrdersScreen] ✅ Statut mis à jour pour la commande:', match.order_number, match.status);
        if (intervalId) {
          clearInterval(intervalId);
          intervalId = null;
        }
      } else if (attempts >= 6) {
        if (intervalId) {
          clearInterval(intervalId);
          intervalId = null;
        }
      }
    };

    pollOnce();
    intervalId = setInterval(pollOnce, 2000);

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [route?.params?.orderId, route?.params?.orderNumber]);

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  // Filtrer les commandes selon le filtre sélectionné
  const filteredOrders = useMemo(() => {
    let filtered: OrderLite[];
    if (selectedFilter === 'all') {
      filtered = orders;
    } else {
      filtered = orders.filter(order => order.status === selectedFilter);
    }
    
    // Log des commandes filtrées
    console.log('[OrdersScreen] 🔍 Filtrage commandes:', {
      filter: selectedFilter,
      total_orders: orders.length,
      filtered_count: filtered.length,
      filtered_orders: filtered.map(order => ({
        id: order.id,
        order_number: order.order_number,
        status: order.status,
        status_label: order.status_label,
      })),
    });
    
    return filtered;
  }, [orders, selectedFilter]);

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>Mes commandes</Text>
      </View>
      
      {/* Filtres horizontaux */}
      <View style={styles.filtersContainer}>
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.filtersScroll}
        >
          {FILTER_OPTIONS.map((filter) => (
            <TouchableOpacity
              key={filter.value}
              style={[
                styles.filterChip,
                selectedFilter === filter.value && styles.filterChipActive
              ]}
              onPress={() => setSelectedFilter(filter.value)}
            >
              <Text
                style={[
                  styles.filterChipText,
                  selectedFilter === filter.value && styles.filterChipTextActive
                ]}
              >
                {filter.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>
      
      <View style={styles.content}>
        {isLoading ? (
          <LoadingScreen />
        ) : filteredOrders.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Ionicons
              name="receipt-outline"
              size={64}
              color={COLORS.TEXT_SECONDARY}
            />
            <Text style={styles.emptyText}>
              {selectedFilter === 'all' ? 'Aucune commande' : `Aucune commande ${FILTER_OPTIONS.find(f => f.value === selectedFilter)?.label.toLowerCase()}`}
            </Text>
            <Text style={styles.emptySubtext}>
              {selectedFilter === 'all' ? 'Vos commandes apparaîtront ici' : 'Essayez un autre filtre'}
            </Text>
          </View>
        ) : (
          <View style={{ gap: 12 }}>
            {filteredOrders.map((order) => (
              <View key={order.id} style={styles.orderCard}>
                <View style={styles.orderHeader}>
                  <Text style={styles.orderNumber}>#{order.order_number}</Text>
                  <View style={styles.statusBadge}>
                    <Text style={styles.statusText}>{order.status_label}</Text>
                  </View>
                </View>
                <Text style={styles.orderDate}>Créée le {formatDate(order.created_at)}</Text>
                <View style={styles.itemsList}>
                  {order.items.map((item) => (
                    <View key={item.id} style={styles.itemRow}>
                      <Text style={styles.itemTitle}>{item.product_title}</Text>
                      <Text style={styles.itemQty}>
                        {item.is_weighted && item.weight_unit
                          ? `${formatWeightQuantity(Number(item.quantity))} ${item.weight_unit}`
                          : `x${Math.round(Number(item.quantity))}`}
                      </Text>
                    </View>
                  ))}
                </View>
                <View style={styles.totalRow}>
                  <Text style={styles.totalLabel}>Total</Text>
                  <Text style={styles.totalValue}>{formatPrice(parseFloat(order.total))}</Text>
                </View>
              </View>
            ))}
          </View>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.BACKGROUND,
  },
  header: {
    backgroundColor: COLORS.PRIMARY,
    padding: 24,
    paddingTop: 60,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  filtersContainer: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  filtersScroll: {
    paddingHorizontal: 16,
    gap: 8,
  },
  filterChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#F3F4F6',
    marginRight: 8,
  },
  filterChipActive: {
    backgroundColor: COLORS.PRIMARY,
  },
  filterChipText: {
    fontSize: 14,
    fontWeight: '500',
    color: COLORS.TEXT,
  },
  filterChipTextActive: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  content: {
    padding: 16,
  },
  loaderContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 40,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
    marginTop: 40,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
  },
  orderCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  orderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  orderNumber: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.TEXT,
  },
  statusBadge: {
    backgroundColor: '#ECFDF3',
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  statusText: {
    fontSize: 12,
    color: COLORS.PRIMARY,
    fontWeight: '600',
  },
  orderDate: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
    marginBottom: 10,
  },
  itemsList: {
    gap: 6,
    marginBottom: 10,
  },
  itemRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  itemTitle: {
    fontSize: 14,
    color: COLORS.TEXT,
    flex: 1,
    marginRight: 8,
  },
  itemQty: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
  },
  totalLabel: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
  },
  totalValue: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.TEXT,
  },
});

export default OrdersScreen;

