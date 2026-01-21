import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { COLORS, API_ENDPOINTS } from '../utils/constants';
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

const OrdersScreen: React.FC = () => {
  const navigation = useNavigation();
  const [orders, setOrders] = useState<OrderLite[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const loadOrders = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get(API_ENDPOINTS.ORDERS);
      const raw = response.data;
      const list: OrderLite[] = Array.isArray(raw)
        ? raw
        : Array.isArray(raw?.results)
        ? raw.results
        : [];
      setOrders(list);
    } catch (error: any) {
      // Si c'est une erreur de mode hors ligne, gérer silencieusement
      if (error.isOfflineBlocked || error.code === 'OFFLINE_MODE_FORCED') {
        // En mode hors ligne, on peut garder les commandes déjà chargées ou vider la liste
        // setOrders([]); // Optionnel : vider si on veut forcer l'utilisateur à être en ligne
        return;
      }
      console.error('[OrdersScreen] Error loading orders:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const unsubscribe = (navigation as any).addListener('focus', () => {
      loadOrders();
    });
    loadOrders();
    return unsubscribe;
  }, [navigation]);

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Mes commandes</Text>
      </View>
      
      <View style={styles.content}>
        {isLoading ? (
          <LoadingScreen />
        ) : orders.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Ionicons
              name="receipt-outline"
              size={64}
              color={COLORS.TEXT_SECONDARY}
            />
            <Text style={styles.emptyText}>
              Aucune commande
            </Text>
            <Text style={styles.emptySubtext}>
              Vos commandes apparaîtront ici
            </Text>
          </View>
        ) : (
          <View style={{ gap: 12 }}>
            {orders.map((order) => (
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
                          ? `${item.quantity} ${item.weight_unit}`
                          : `x${item.quantity}`}
                      </Text>
                    </View>
                  ))}
                </View>
                <View style={styles.totalRow}>
                  <Text style={styles.totalLabel}>Total</Text>
                  <Text style={styles.totalValue}>{order.total} FCFA</Text>
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

