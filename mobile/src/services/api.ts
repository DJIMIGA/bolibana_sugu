import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import Constants from 'expo-constants';
import { STORAGE_KEYS, API_TIMEOUT, API_ENDPOINTS } from '../utils/constants';
import { errorService } from './errorService';
import { connectivityService } from './connectivityService';
import { networkMonitor } from '../utils/networkMonitor';

// URL de base de l'API depuis les variables d'environnement
// En développement, utilisez l'IP locale de votre ordinateur au lieu de localhost
// Exemple : http://192.168.1.100:8000/api
export const API_BASE_URL = Constants.expoConfig?.extra?.apiBaseUrl || 
  process.env.EXPO_PUBLIC_API_BASE_URL || 
  'https://www.bolibana.com/api';

// Base URL pour les médias (sans le /api à la fin)
export const MEDIA_BASE_URL = API_BASE_URL.replace(/\/api\/?$/, '');

// Callback pour la session expirée
let sessionExpiredCallback: (() => void) | null = null;

export const setSessionExpiredCallback = (callback: () => void) => {
  sessionExpiredCallback = callback;
};

// Instance Axios configurée
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur de requête : vérification du mode hors ligne et injection du token JWT
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Vérifier si on est en mode hors ligne forcé
    const isOnline = connectivityService.getIsOnline();
    const isForceOffline = connectivityService.isForceOffline();
    
    if (isForceOffline) {
      const endpoint = config.url || 'unknown';
      const method = config.method?.toUpperCase() || 'UNKNOWN';
      
      // Enregistrer la tentative bloquée dans le monitor
      networkMonitor.logRequest({
        method,
        endpoint,
        timestamp: new Date().toISOString(),
        status: 'BLOCKED',
        reason: 'OFFLINE_MODE_FORCED'
      });
      
      // Rejeter la requête avec une erreur Axios compatible
      const error = new Error('') as AxiosError;
      error.isOfflineBlocked = true;
      error.config = config;
      error.response = undefined;
      error.request = undefined;
      error.code = 'OFFLINE_MODE_FORCED';
      error.message = ''; // Message vide pour ne pas afficher d'erreur
      return Promise.reject(error);
    }
    
    // Enregistrer les requêtes autorisées
    networkMonitor.logRequest({
      method: config.method?.toUpperCase() || 'UNKNOWN',
      endpoint: config.url || 'unknown',
      timestamp: new Date().toISOString(),
      status: 'ALLOWED'
    });
    
    // Si on est vraiment hors ligne (pas de connexion), permettre quand même pour les cas d'urgence
    // Logs réduits pour éviter le bruit
    
    try {
      const token = await SecureStore.getItemAsync(STORAGE_KEYS.AUTH_TOKEN);
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Erreur lors de la récupération du token:', error);
    }
    
    // Logs réduits - les requêtes autorisées sont suivies par NetworkMonitor mais non loggées
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Intercepteur de réponse : gestion des erreurs
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Gestion de l'erreur 401 (non autorisé)
    // Ne pas intercepter les erreurs 401 sur l'endpoint de login ou de refresh
    const isAuthEndpoint = originalRequest.url?.includes(API_ENDPOINTS.AUTH.LOGIN) || 
                          originalRequest.url?.includes(API_ENDPOINTS.AUTH.REFRESH);

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true;

      try {
        // Tentative de refresh du token
        const refreshToken = await SecureStore.getItemAsync(STORAGE_KEYS.AUTH_REFRESH_TOKEN);
        
        if (refreshToken) {
          const response = await axios.post(
            `${API_BASE_URL}${API_ENDPOINTS.AUTH.REFRESH}`,
            { refresh: refreshToken }
          );

          const { access } = response.data;
          await SecureStore.setItemAsync(STORAGE_KEYS.AUTH_TOKEN, access);

          // Réessayer la requête originale avec le nouveau token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access}`;
          }
          return apiClient(originalRequest);
        } else {
          // Pas de refresh token, session expirée
          throw new Error('Session expirée');
        }
      } catch (refreshError) {
        // Échec du refresh, déconnexion
        await Promise.all([
          SecureStore.deleteItemAsync(STORAGE_KEYS.AUTH_TOKEN),
          SecureStore.deleteItemAsync(STORAGE_KEYS.AUTH_REFRESH_TOKEN),
          AsyncStorage.removeItem(STORAGE_KEYS.AUTH_USER),
        ]);

        if (sessionExpiredCallback) {
          sessionExpiredCallback();
        }

        return Promise.reject(refreshError);
      }
    }

    // Ne pas logger les erreurs pour les endpoints B2B optionnels (ils sont gérés silencieusement)
    // NOTE: `baseURL` inclut déjà "/api", donc `originalRequest.url` est souvent "/inventory/..." (sans "/api").
    const url = originalRequest.url || '';
    const isInventoryEndpoint = url.includes('/inventory/') || url.includes('/api/inventory/');
    const isB2BOptionalEndpoint =
      isInventoryEndpoint &&
      (url.includes('/synced/') || url.includes('/categories/'));
    
    // Si c'est un endpoint B2B optionnel et que c'est une erreur 400/404, ne pas logger
    if (isB2BOptionalEndpoint && 
        (error.response?.status === 400 || error.response?.status === 404 || !error.response)) {
      // Rejeter l'erreur sans la logger (elle sera gérée silencieusement dans le code appelant)
      return Promise.reject(error);
    }

    // Gestion des autres erreurs
    const apiError = errorService.handleApiError(error);
    return Promise.reject(apiError);
  }
);

// Support FormData pour les uploads
export const uploadFile = async (
  endpoint: string,
  file: any,
  additionalData?: Record<string, any>
): Promise<AxiosResponse> => {
  const formData = new FormData();
  
  if (file) {
    formData.append('file', file);
  }
  
  if (additionalData) {
    Object.keys(additionalData).forEach((key) => {
      formData.append(key, additionalData[key]);
    });
  }

  const token = await SecureStore.getItemAsync(STORAGE_KEYS.AUTH_TOKEN);
  
  return apiClient.post(endpoint, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });
};

export default apiClient;

