// Constantes de l'application

export const API_TIMEOUT = 15000; // 15 secondes
export const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 heures en millisecondes
export const SESSION_EXPIRY = 12 * 60 * 60 * 1000; // 12 heures
export const SYNC_BATCH_SIZE = 5; // Nombre d'éléments à synchroniser en parallèle
export const MAX_RETRY_ATTEMPTS = 3;
export const RETRY_BACKOFF_BASE = 1000; // 1 seconde de base


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
  FAVORITES: '/favorites/',
  FAVORITES_TOGGLE: '/favorites/toggle/',
  LOYALTY: '/loyalty/',
  REVIEWS: (productSlug: string) => `/products/${productSlug}/reviews/`,
  STATIC_PAGES: (slug: string) => `/core/pages/${slug}/`,
  SITE_CONFIG: '/core/site-config/',
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
  // BoliBana - Identite visuelle (Couleurs du Mali)
  PRIMARY: '#008000',
  PRIMARY_LIGHT: '#059669',
  PRIMARY_DARK: '#047857',
  SECONDARY: '#FFD700',
  SECONDARY_LIGHT: '#f4e4bc',
  SECONDARY_DARK: '#d4a800',
  ACCENT: '#EF4444',
  ACCENT_LIGHT: '#f87171',
  ACCENT_DARK: '#dc2626',
  DANGER: '#EF4444',
  SUCCESS: '#008000',
  WARNING: '#FFD700',
  ERROR: '#EF4444',
  BACKGROUND: '#FFFFFF',
  BACKGROUND_WARM: '#fffaf0',
  BACKGROUND_GREEN: '#f0f8f0',
  TEXT: '#1F2937',
  TEXT_SECONDARY: '#6B7280',
  BEIGE: '#C08A5B',
  TERRACOTTA: '#C08A5B',
  BORDEAUX: '#8B4A4A',
} as const;

export const BRAND = {
  NAME: 'BoliBana',
  SHORT_NAME: 'SuGu',
  FULL_NAME: 'BoliBana SuGu',
  TAGLINE: 'Votre intermediaire expert du marche',
} as const;

