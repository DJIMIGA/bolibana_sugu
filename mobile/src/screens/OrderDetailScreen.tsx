import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import apiClient from '../services/api';
import { API_ENDPOINTS, COLORS } from '../utils/constants';
import { formatPrice, formatWeightQuantity } from '../utils/helpers';
import { LoadingScreen } from '../components/LoadingScreen';

type OrderStatusHistory = {
  id: number;
  old_status?: string | null;
  new_status: string;
  changed_at: string;
  note?: string | null;
};

type OrderItem = {
  id: number;
  product?: { title?: string };
  quantity: number;
  price: number;
  total_price?: number;
  is_weighted?: boolean;
  weight_unit?: string | null;
};

type OrderDetail = {
  id: number;
  order_number: string;
  status: string;
  payment_method: string;
  created_at: string;
  subtotal: number;
  shipping_cost: number;
  tax: number;
  discount: number;
  total: number;
  items: OrderItem[];
  status_history: OrderStatusHistory[];
};

const OrderDetailScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute<any>();
  const [order, setOrder] = useState<OrderDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const orderId = Number(route?.params?.orderId);

  const formatStatusLabel = (status: string) => {
    switch (status) {
      case 'draft':
        return 'Brouillon';
      case 'confirmed':
        return 'Confirmée';
      case 'shipped':
        return 'Expédiée';
      case 'delivered':
        return 'Livrée';
      case 'cancelled':
        return 'Annulée';
      default:
        return status;
    }
  };

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  const loadOrder = async (silent = false) => {
    try {
      if (!silent) {
        setIsLoading(true);
      }
      const response = await apiClient.get(API_ENDPOINTS.CART_ORDER_DETAIL(orderId));
      setOrder(response.data);
    } catch (error: any) {
      const message = error?.message || 'Erreur inconnue';
      console.error('[OrderDetail] ❌ Error loading order:', message);
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    if (orderId) {
      loadOrder();
    }
  }, [orderId]);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadOrder(true);
  };

  if (isLoading || !order) {
    return <LoadingScreen />;
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={20} color="#FFFFFF" />
          <Text style={styles.backText}>Retour</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Commande #{order.order_number}</Text>
        <Text style={styles.subtitle}>Créée le {formatDate(order.created_at)}</Text>
      </View>

      <View style={styles.section}>
        <View style={styles.statusRow}>
          <Text style={styles.label}>Statut</Text>
          <View style={styles.statusBadge}>
            <Text style={styles.statusText}>{formatStatusLabel(order.status)}</Text>
          </View>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Paiement</Text>
          <Text style={styles.value}>{order.payment_method}</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Articles</Text>
        {order.items.map((item) => (
          <View key={item.id} style={styles.itemRow}>
            <View style={styles.itemInfo}>
              <Text style={styles.itemTitle}>{item.product?.title || 'Produit'}</Text>
              <Text style={styles.itemQty}>
                {item.is_weighted && item.weight_unit
                  ? `${formatWeightQuantity(Number(item.quantity))} ${item.weight_unit}`
                  : `x${Math.round(Number(item.quantity))}`}
              </Text>
            </View>
            <Text style={styles.itemTotal}>
              {formatPrice(item.total_price ?? item.price * Number(item.quantity))}
            </Text>
          </View>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Récapitulatif</Text>
        <View style={styles.row}>
          <Text style={styles.label}>Sous-total</Text>
          <Text style={styles.value}>{formatPrice(order.subtotal)}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Livraison</Text>
          <Text style={styles.value}>{formatPrice(order.shipping_cost)}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Taxes</Text>
          <Text style={styles.value}>{formatPrice(order.tax)}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Réduction</Text>
          <Text style={styles.value}>-{formatPrice(order.discount)}</Text>
        </View>
        <View style={styles.totalRow}>
          <Text style={styles.totalLabel}>Total</Text>
          <Text style={styles.totalValue}>{formatPrice(order.total)}</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Historique des statuts</Text>
        {order.status_history?.length ? (
          <View style={styles.timeline}>
            {order.status_history.map((history) => (
              <View key={history.id} style={styles.timelineRow}>
                <View style={styles.timelineDot} />
                <View style={styles.timelineContent}>
                  <Text style={styles.timelineTitle}>
                    {formatStatusLabel(history.new_status)}
                  </Text>
                  <Text style={styles.timelineDate}>
                    {formatDate(history.changed_at)}
                    {history.note ? ` - ${history.note}` : ''}
                  </Text>
                </View>
              </View>
            ))}
          </View>
        ) : (
          <Text style={styles.emptyTimeline}>Aucun changement de statut pour le moment.</Text>
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
    padding: 20,
    paddingTop: 50,
  },
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  backText: {
    color: '#FFFFFF',
    marginLeft: 8,
    fontSize: 14,
    fontWeight: '600',
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  subtitle: {
    fontSize: 12,
    color: '#E5E7EB',
    marginTop: 4,
  },
  section: {
    backgroundColor: '#FFFFFF',
    marginTop: 12,
    marginHorizontal: 16,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.TEXT,
    marginBottom: 12,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  label: {
    fontSize: 13,
    color: COLORS.TEXT_SECONDARY,
  },
  value: {
    fontSize: 13,
    color: COLORS.TEXT,
    fontWeight: '600',
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
  itemRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  itemInfo: {
    flex: 1,
    marginRight: 8,
  },
  itemTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.TEXT,
  },
  itemQty: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
    marginTop: 2,
  },
  itemTotal: {
    fontSize: 14,
    fontWeight: '700',
    color: COLORS.TEXT,
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
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
  timeline: {
    borderLeftWidth: 2,
    borderLeftColor: '#D1FAE5',
    paddingLeft: 12,
  },
  timelineRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  timelineDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: COLORS.PRIMARY,
    marginLeft: -17,
    marginTop: 4,
    marginRight: 10,
  },
  timelineContent: {
    flex: 1,
  },
  timelineTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: COLORS.TEXT,
  },
  timelineDate: {
    fontSize: 11,
    color: COLORS.TEXT_SECONDARY,
    marginTop: 2,
  },
  emptyTimeline: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
  },
});

export default OrderDetailScreen;
