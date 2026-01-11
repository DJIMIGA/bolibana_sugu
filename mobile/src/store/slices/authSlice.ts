import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import apiClient, { setSessionExpiredCallback } from '../../services/api';
import { STORAGE_KEYS, API_ENDPOINTS, SESSION_EXPIRY } from '../../utils/constants';
import { User, LoyaltyInfo } from '../../types';

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isReadOnly: boolean; // Mode lecture seule (si session expirée ou hors ligne non identifié)
  isLoading: boolean; // Pour le chargement initial
  isLoggingIn: boolean; // Pour la connexion
  sessionExpired: boolean;
  error: string | null;
  loyaltyInfo: LoyaltyInfo | null;
  isLoadingLoyalty: boolean;
}

const initialState: AuthState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isReadOnly: false,
  isLoading: true,
  isLoggingIn: false,
  sessionExpired: false,
  error: null,
  loyaltyInfo: null,
  isLoadingLoyalty: false,
};

// Thunk pour la connexion
export const loginAsync = createAsyncThunk(
  'auth/login',
  async (credentials: { email: string; password: string }, { rejectWithValue }) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN, {
        email: credentials.email,
        password: credentials.password,
      });

      const { access, refresh } = response.data;
      
      // Stocker les tokens de manière sécurisée
      await Promise.all([
        SecureStore.setItemAsync(STORAGE_KEYS.AUTH_TOKEN, access),
        SecureStore.setItemAsync(STORAGE_KEYS.AUTH_REFRESH_TOKEN, refresh),
      ]);

      // Récupérer le profil utilisateur
      const profileResponse = await apiClient.get(API_ENDPOINTS.PROFILE);
      const { mapUserFromBackend } = await import('../../utils/mappers');
      const user = mapUserFromBackend(profileResponse.data);

      await AsyncStorage.setItem(STORAGE_KEYS.AUTH_USER, JSON.stringify(user));

      return { access, refresh, user };
    } catch (error: any) {
      // Gestion améliorée des erreurs de connexion
      let errorMessage = 'Erreur de connexion';
      
      if (error.response?.data) {
        const data = error.response.data;
        
        // Priorité aux messages spécifiques
        if (data.detail) {
          const detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
          
          // Détecter les erreurs de mot de passe/email incorrect
          if (
            detail.toLowerCase().includes('no active account') ||
            detail.toLowerCase().includes('unable to log in') ||
            detail.toLowerCase().includes('invalid credentials') ||
            detail.toLowerCase().includes('incorrect') ||
            detail.toLowerCase().includes('invalid password')
          ) {
            errorMessage = 'Email ou mot de passe incorrect. Veuillez vérifier vos identifiants.';
          } else {
            errorMessage = detail;
          }
        } else if (data.non_field_errors) {
          const errors = Array.isArray(data.non_field_errors)
            ? data.non_field_errors.join(', ')
            : data.non_field_errors;
          
          if (
            errors.toLowerCase().includes('no active account') ||
            errors.toLowerCase().includes('unable to log in') ||
            errors.toLowerCase().includes('invalid credentials') ||
            errors.toLowerCase().includes('incorrect')
          ) {
            errorMessage = 'Email ou mot de passe incorrect. Veuillez vérifier vos identifiants.';
          } else {
            errorMessage = errors;
          }
        } else if (data.password) {
          errorMessage = Array.isArray(data.password) ? data.password.join(', ') : data.password;
        } else if (data.email) {
          errorMessage = Array.isArray(data.email) ? data.email.join(', ') : data.email;
        } else if (data.message) {
          errorMessage = data.message;
        } else if (data.error) {
          errorMessage = data.error;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      return rejectWithValue(errorMessage);
    }
  }
);

// Thunk pour le refresh token
export const refreshTokenAsync = createAsyncThunk(
  'auth/refreshToken',
  async (_, { rejectWithValue }) => {
    try {
      const refreshToken = await SecureStore.getItemAsync(STORAGE_KEYS.AUTH_REFRESH_TOKEN);
      
      if (!refreshToken) {
        throw new Error('Aucun refresh token disponible');
      }

      const response = await apiClient.post(API_ENDPOINTS.AUTH.REFRESH, {
        refresh: refreshToken,
      });

      const { access } = response.data;
      await SecureStore.setItemAsync(STORAGE_KEYS.AUTH_TOKEN, access);

      return access;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Erreur de rafraîchissement');
    }
  }
);

// Thunk pour charger l'utilisateur au démarrage
export const loadUserAsync = createAsyncThunk(
  'auth/loadUser',
  async (_, { rejectWithValue }) => {
    try {
      const [token, userJson] = await Promise.all([
        SecureStore.getItemAsync(STORAGE_KEYS.AUTH_TOKEN),
        AsyncStorage.getItem(STORAGE_KEYS.AUTH_USER),
      ]);

      if (!token || !userJson) {
        return null;
      }

      const user = JSON.parse(userJson);

      // Si on est en ligne, on vérifie le token
      const { connectivityService } = await import('../../services/connectivityService');
      const isOnline = connectivityService.getIsOnline();

      if (isOnline) {
        try {
        const response = await apiClient.get(API_ENDPOINTS.PROFILE);
        const { mapUserFromBackend } = await import('../../utils/mappers');
          const freshUser = mapUserFromBackend(response.data);
          await AsyncStorage.setItem(STORAGE_KEYS.AUTH_USER, JSON.stringify(freshUser));
          return { token, user: freshUser, isReadOnly: false };
      } catch (error) {
          return { token, user, isReadOnly: true, expired: true };
      }
      }
    } catch (error: any) {
      return rejectWithValue(error.message || 'Erreur de chargement');
    }
  }
);

// Thunk pour mettre à jour le profil
export const updateProfileAsync = createAsyncThunk(
  'auth/updateProfile',
  async (data: Partial<User>, { rejectWithValue }) => {
    try {
      // Utiliser l'endpoint profile directement avec PATCH (ProfileView supporte PATCH)
      const endpoint = API_ENDPOINTS.PROFILE;
      
      const response = await apiClient.patch(endpoint, data);
      
      const { mapUserFromBackend } = await import('../../utils/mappers');
      const user = mapUserFromBackend(response.data);
      
      await AsyncStorage.setItem(STORAGE_KEYS.AUTH_USER, JSON.stringify(user));
      
      return user;
    } catch (error: any) {
      const errorMsg = cleanErrorForLog(error);
      console.error('[authSlice] updateProfileAsync - Erreur:', errorMsg);
      if (error.response?.status) {
        console.error('[authSlice] Status:', error.response.status);
      }
      
      const errorMessage = error.response?.data?.detail 
        || error.response?.data?.password?.[0] 
        || error.response?.data?.non_field_errors?.[0]
        || error.message 
        || 'Erreur de mise à jour du profil';
      
      return rejectWithValue(errorMessage);
    }
  }
);

// Thunk pour charger le profil utilisateur
export const fetchProfileAsync = createAsyncThunk(
  'auth/fetchProfile',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.PROFILE);
      const { mapUserFromBackend } = await import('../../utils/mappers');
      const user = mapUserFromBackend(response.data);
      
      await AsyncStorage.setItem(STORAGE_KEYS.AUTH_USER, JSON.stringify(user));
      
      return user;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Erreur de chargement du profil');
    }
  }
);

// Thunk pour récupérer les informations de fidélité
export const fetchLoyaltyInfoAsync = createAsyncThunk(
  'auth/fetchLoyaltyInfo',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.LOYALTY);
      return response.data as LoyaltyInfo;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Erreur de chargement des informations de fidélité');
    }
  }
);

// Thunk pour la déconnexion
export const logoutAsync = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      // Appeler l'endpoint de déconnexion si disponible
      try {
        await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
      } catch (error) {
        // Ignorer les erreurs de déconnexion
      }

      // Nettoyer le stockage local
      await Promise.all([
        SecureStore.deleteItemAsync(STORAGE_KEYS.AUTH_TOKEN),
        SecureStore.deleteItemAsync(STORAGE_KEYS.AUTH_REFRESH_TOKEN),
        AsyncStorage.removeItem(STORAGE_KEYS.AUTH_USER),
      ]);

      return null;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Erreur de déconnexion');
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setSessionExpired: (state, action: PayloadAction<boolean>) => {
      state.sessionExpired = action.payload;
      if (action.payload) {
        state.isAuthenticated = false;
        state.isReadOnly = true; // On passe en lecture seule
      }
    },
    setReadOnly: (state, action: PayloadAction<boolean>) => {
      state.isReadOnly = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(loginAsync.pending, (state) => {
        state.isLoggingIn = true;
        state.error = null;
      })
      .addCase(loginAsync.fulfilled, (state, action) => {
        state.isLoggingIn = false;
        state.isAuthenticated = true;
        state.isReadOnly = false; // Reset read-only on login
        state.token = action.payload.access;
        state.refreshToken = action.payload.refresh;
        state.user = action.payload.user;
        state.error = null;
        state.sessionExpired = false;
      })
      .addCase(loginAsync.rejected, (state, action) => {
        state.isLoggingIn = false;
        state.isAuthenticated = false;
        state.error = action.payload as string;
      })
      // Refresh token
      .addCase(refreshTokenAsync.fulfilled, (state, action) => {
        state.token = action.payload;
      })
      .addCase(refreshTokenAsync.rejected, (state) => {
        state.isAuthenticated = false;
        state.token = null;
        state.refreshToken = null;
        state.user = null;
      })
      // Load user
      .addCase(loadUserAsync.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(loadUserAsync.fulfilled, (state, action) => {
        state.isLoading = false;
        if (action.payload) {
          state.isAuthenticated = !action.payload.expired;
          state.token = action.payload.token;
          state.user = action.payload.user;
          state.isReadOnly = action.payload.isReadOnly;
          state.sessionExpired = !!action.payload.expired;
        } else {
          state.isAuthenticated = false;
          state.user = null;
          state.token = null;
          state.isReadOnly = false;
        }
      })
      .addCase(loadUserAsync.rejected, (state) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
      })
      // Update profile
      .addCase(updateProfileAsync.pending, (state) => {
        state.error = null;
      })
      .addCase(updateProfileAsync.fulfilled, (state, action) => {
        state.user = action.payload;
        state.error = null;
      })
      .addCase(updateProfileAsync.rejected, (state, action) => {
        state.error = action.payload as string;
      })
      // Fetch profile
      .addCase(fetchProfileAsync.pending, (state) => {
        state.error = null;
      })
      .addCase(fetchProfileAsync.fulfilled, (state, action) => {
        state.user = action.payload;
        state.error = null;
      })
      .addCase(fetchProfileAsync.rejected, (state, action) => {
        state.error = action.payload as string;
      })
      // Fetch loyalty info
      .addCase(fetchLoyaltyInfoAsync.pending, (state) => {
        state.isLoadingLoyalty = true;
      })
      .addCase(fetchLoyaltyInfoAsync.fulfilled, (state, action) => {
        state.isLoadingLoyalty = false;
        state.loyaltyInfo = action.payload;
      })
      .addCase(fetchLoyaltyInfoAsync.rejected, (state) => {
        state.isLoadingLoyalty = false;
        // Ne pas afficher d'erreur si l'utilisateur n'a pas encore de commandes
      })
      // Logout
      .addCase(logoutAsync.fulfilled, (state) => {
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        state.sessionExpired = false;
        state.error = null;
        state.loyaltyInfo = null;
      });
  },
});

// Configurer le callback de session expirée
setSessionExpiredCallback(() => {
  // Cette fonction sera appelée depuis le service API
  // Le store sera mis à jour via le reducer
});

export const { setSessionExpired, clearError } = authSlice.actions;
export default authSlice.reducer;
