// Types de base pour l'application

export interface User {
  id: number;
  email: string;
  phone?: string;
  full_name?: string;
  profile_picture?: string;
  fidelys_number?: string;
  date_of_birth?: string;
  is_staff?: boolean;
  is_superuser?: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoyaltyTier {
  name: 'Bronze' | 'Argent' | 'Or' | 'Diamant';
  min_points: number;
  color: string;
}

export interface LoyaltyHistoryItem {
  loyalty_points: number;
  loyalty_level: 'Bronze' | 'Argent' | 'Or' | 'Diamant';
  total_spent: number;
  total_orders: number;
  created_at: string;
}

export interface LoyaltyInfo {
  fidelys_number: string;
  total_orders: number;
  loyalty_points: number;
  loyalty_level: 'Bronze' | 'Argent' | 'Or' | 'Diamant';
  loyalty_level_color: string;
  total_spent: number;
  next_level: string | null;
  points_needed: number;
  next_tier_name: string | null;
  progress_to_next_tier: number;
  loyalty_tiers: LoyaltyTier[];
  points_expires_at: string | null;
  messages: string[];
  qr_payload: string;
  history: LoyaltyHistoryItem[];
}

export interface Product {
  id: number;
  title: string;
  slug: string;
  description?: string;
  price: number;
  discount_price?: number;
  // Champs promo (API inventory/B2B)
  promo_price?: number;
  has_promotion?: boolean;
  discount_percent?: number;
  promotion_start_date?: string;
  promotion_end_date?: string;
  category: number;
  supplier?: number;
  brand?: string;
  is_available: boolean;
  is_salam: boolean;
  stock: number;
  image?: string;
  image_urls?: {
    main?: string;
    gallery?: string[];
  };
  sku?: string;
  specifications?: Record<string, any>;
  weight?: number;
  dimensions?: string;
  condition?: 'new' | 'used' | 'refurbished';
  has_warranty: boolean;
  is_trending: boolean;
  sales_count: number;
  average_rating?: number;
  review_count?: number;
  created_at: string;
  updated_at: string;
  delivery_methods?: DeliveryMethod[];
}

export interface DeliveryMethod {
  id: number;
  name: string;
  slug?: string;
  description?: string | null;
  base_price?: number;
  effective_price?: number;
  override_price?: number | null;
  order?: number;
  site_configuration?: number;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  parent?: number;
  image?: string;
  image_url?: string;
  description?: string;
  color: string;
  is_main: boolean;
  order: number;
  category_type?: 'MODEL' | 'FILTER' | 'MARKETING';
  product_count?: number;
  rayon_type?: string | null;
  level?: number | null;
}

export interface CartItem {
  id: number;
  product: Product;
  quantity: number;
  colors?: number[];
  sizes?: number[];
  variant?: number;
  is_weighted?: boolean;
  weight_unit?: string;
  unit_price?: number;
  total_price?: number;
}

export interface Cart {
  id: number;
  user?: number;
  items: CartItem[];
  total_price: number;
  created_at: string;
  updated_at: string;
}

export interface ShippingAddress {
  id: number;
  user: number;
  full_name?: string;
  address_type: 'DOM' | 'BUR' | 'AUT';
  quarter: string;
  street_address: string;
  city: string;
  additional_info?: string;
  is_default: boolean;
}

export interface Order {
  id: number;
  order_number: string;
  user: number;
  status: 'draft' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';
  payment_method: 'cash_on_delivery' | 'online_payment' | 'mobile_money' | 'orange_money' | 'stripe';
  is_paid: boolean;
  paid_at?: string;
  shipping_address: ShippingAddress;
  shipping_method?: number;
  tracking_number?: string;
  subtotal: number;
  shipping_cost: number;
  tax: number;
  discount: number;
  total: number;
  created_at: string;
  updated_at: string;
}

export interface ApiError {
  message: string;
  code?: string;
  status?: number;
  details?: Record<string, any>;
  isOfflineBlocked?: boolean;
}

export interface ConnectivityState {
  isOnline: boolean;
  isInternetReachable: boolean;
  type?: string;
}

export interface SyncQueueItem {
  id: string;
  action: 'CREATE' | 'UPDATE' | 'DELETE';
  endpoint: string;
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  data: any;
  status: 'PENDING' | 'SYNCING' | 'SUCCESS' | 'FAILED';
  retryCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface CacheItem<T> {
  data: T;
  timestamp: number;
  version: string;
}

