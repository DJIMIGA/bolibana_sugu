// Constantes de l'application

export const API_TIMEOUT = 15000; // 15 secondes
export const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 heures en millisecondes
export const SESSION_EXPIRY = 12 * 60 * 60 * 1000; // 12 heures
export const SYNC_BATCH_SIZE = 5; // Nombre d'éléments à synchroniser en parallèle
export const MAX_RETRY_ATTEMPTS = 3;
export const RETRY_BACKOFF_BASE = 1000; // 1 seconde de base

// Clé de chiffrement pour la persistance Redux (en production, utiliser une variable d'env)
export const REDUX_PERSIST_SECRET_KEY = 'sagakore-secure-offline-key-2025-v1';

export const CACHE_KEYS = {
  PRODUCTS: 'cache_products',
  CATEGORIES: 'cache_categories',
  CART: 'cache_cart',
  USER_PROFILE: 'cache_user_profile',
  ADDRESSES: 'cache_addresses',
} as const;

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  AUTH_REFRESH_TOKEN: 'auth_refresh_token',
  AUTH_USER: 'auth_user',
  LOYALTY_INFO: 'loyalty_info',
  SYNC_QUEUE: 'sync_queue',
} as const;

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/token/',
    REFRESH: '/token/refresh/',
    LOGOUT: '/token/logout/',
    REGISTER: '/register/',
  },
  PRODUCTS: '/products/',
  CATEGORIES: '/categories/',
  CART: '/cart/',
  PROFILE: '/profile/',
  ADDRESSES: '/addresses/',
  ORDERS: '/orders/',
  CART_ORDERS: '/cart/orders/',
  CART_ORDER_DETAIL: (orderId: number) => `/cart/orders/${orderId}/`,
  LOYALTY: '/loyalty/',
  CHANGE_PASSWORD: '/change-password/',
  DELETE_ACCOUNT: '/delete-account/',
  B2B: {
    // NOTE: API_BASE_URL inclut déjà "/api" (ex: https://domaine.com/api)
    // Donc ici on NE remet pas "/api", sinon on obtient "/api/api/..."
    PRODUCTS: '/inventory/products/synced/',
    CATEGORIES: '/inventory/categories/synced/',
  },
} as const;

export const COLORS = {
  PRIMARY: '#10B981', // Vert
  SECONDARY: '#F59E0B', // Jaune
  DANGER: '#EF4444', // Rouge
  SUCCESS: '#10B981',
  WARNING: '#F59E0B',
  ERROR: '#EF4444',
  BACKGROUND: '#FFFFFF',
  TEXT: '#1F2937',
  TEXT_SECONDARY: '#6B7280',
  // Accent chaud : beige, terre cuite, bordeaux
  BEIGE: '#C08A5B', // Beige/Terre cuite
  TERRACOTTA: '#C08A5B', // Terre cuite
  BORDEAUX: '#8B4A4A', // Bordeaux léger
} as const;

