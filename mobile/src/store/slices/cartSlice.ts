import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiClient from '../../services/api';
import { API_ENDPOINTS, CACHE_KEYS } from '../../utils/constants';
import { Cart, CartItem } from '../../types';
import { offlineCacheService } from '../../services/offlineCacheService';
import { connectivityService } from '../../services/connectivityService';
import { syncService } from '../../services/syncService';
import { mapCartFromBackend } from '../../utils/mappers';

interface CartState {
  cart: Cart | null;
  items: CartItem[];
  total: number;
  itemsCount: number; // Nombre total d'articles (somme des quantités)
  isLoading: boolean;
  error: string | null;
  lastUpdateTimestamp: number;
}

const initialState: CartState = {
  cart: null,
  items: [],
  total: 0,
  itemsCount: 0, // Nombre total d'articles
  isLoading: false,
  error: null,
  lastUpdateTimestamp: 0,
};

// Fonction utilitaire pour calculer le nombre total d'articles
const calculateItemsCount = (items: CartItem[]): number => {
  return items.reduce((sum, item) => sum + (item.quantity || 0), 0);
};

// Thunk pour récupérer le panier
export const fetchCart = createAsyncThunk(
  'cart/fetchCart',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.CART);

      // Mapper le panier du backend
      const cart = mapCartFromBackend(response.data);

      // Mettre en cache si en ligne
      if (connectivityService.getIsOnline()) {
        await offlineCacheService.set(CACHE_KEYS.CART, cart);
      }

      return cart;
    } catch (error: any) {
      // Essayer de récupérer depuis le cache
      const cached = await offlineCacheService.get<Cart>(CACHE_KEYS.CART);
      if (cached) {
        return cached;
      }
      return rejectWithValue(error.response?.data?.detail || 'Erreur de chargement du panier');
    }
  }
);

// Thunk pour ajouter un article au panier
export const addToCart = createAsyncThunk(
  'cart/addToCart',
  async (data: { product: number; quantity: number; variant?: number; colors?: number[]; sizes?: number[] }, { rejectWithValue }) => {
    try {
      if (data.quantity <= 0) return rejectWithValue('La quantité doit être supérieure à 0');

      if (connectivityService.getIsOnline()) {
        const payload: any = { product: data.product, quantity: data.quantity };
        if (data.variant) payload.variant = data.variant;
        if (data.colors?.length) payload.colors = data.colors;
        if (data.sizes?.length) payload.sizes = data.sizes;

        const response = await apiClient.post(API_ENDPOINTS.CART, payload);
        return mapCartFromBackend(response.data);
      } else {
        // Mode hors ligne (logique simplifiée pour l'exemple)
        await syncService.addToQueue('CREATE', API_ENDPOINTS.CART, 'POST', data);
        return null; // On attendra la synchro
      }
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error || 'Erreur lors de l\'ajout');
    }
  }
);

// Thunk pour mettre à jour un article
export const updateCartItem = createAsyncThunk(
  'cart/updateCartItem',
  async (data: { itemId: number; quantity: number }, { rejectWithValue }) => {
    try {
      console.log(`[cartSlice] 🛠️ Thunk updateCartItem démarré: Item ${data.itemId}, Quantité ${data.quantity}`);
      if (connectivityService.getIsOnline()) {
        const response = await apiClient.patch(`${API_ENDPOINTS.CART}${data.itemId}/`, {
          quantity: data.quantity,
        });
        console.log(`[cartSlice] ✅ Réponse API reçue pour updateCartItem`);
        return mapCartFromBackend(response.data);
      }
      console.log(`[cartSlice] 🔌 Mode hors ligne détecté`);
      return null;
    } catch (error: any) {
      console.error(`[cartSlice] ❌ Erreur API updateCartItem:`, cleanErrorForLog(error));
      return rejectWithValue(error.response?.data?.error || 'Erreur lors de la mise à jour');
    }
  }
);

// Thunk pour supprimer un article
export const removeFromCart = createAsyncThunk(
  'cart/removeFromCart',
  async (itemId: number, { rejectWithValue }) => {
    try {
      if (connectivityService.getIsOnline()) {
        const response = await apiClient.delete(`${API_ENDPOINTS.CART}${itemId}/`);
        return mapCartFromBackend(response.data);
      }
      return null;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error || 'Erreur lors de la suppression');
    }
  }
);

// Thunk pour vider le panier
export const clearCart = createAsyncThunk(
  'cart/clearCart',
  async (_, { rejectWithValue }) => {
    try {
      if (connectivityService.getIsOnline()) {
        const url = `${API_ENDPOINTS.CART}clear/`;
        console.log(`[cartSlice] 🧹 Vidage du panier: DELETE ${url}`);
        const response = await apiClient.delete(url);
        console.log(`[cartSlice] ✅ Réponse vidage reçue`);
        return mapCartFromBackend(response.data);
      } else {
        // Mode hors ligne
        await offlineCacheService.remove(CACHE_KEYS.CART);
        return null;
      }
    } catch (error: any) {
      console.error(`[cartSlice] ❌ Erreur vidage panier:`, cleanErrorForLog(error));
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.detail || 
                          error.message || 
                          'Erreur lors du vidage du panier';
      return rejectWithValue(errorMessage);
    }
  }
);

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    // Action pour mise à jour optimiste de la quantité
    optimisticUpdateQuantity: (state, action: PayloadAction<{ itemId: number; quantity: number }>) => {
      const { itemId, quantity } = action.payload;
      state.lastUpdateTimestamp = Date.now(); // Marquer le moment de la mise à jour
      const item = state.items.find(i => i.id === itemId);
      if (item) {
        const oldQuantity = item.quantity;
        item.quantity = quantity;
        state.itemsCount = calculateItemsCount(state.items);
        
        // Recalculer le prix total approximatif
        const unitPrice = item.product.discount_price || item.product.price;
        state.total = state.total + (unitPrice * (quantity - oldQuantity));
      }
    }
  },
  extraReducers: (builder) => {
    const handleFulfilled = (state: CartState, action: PayloadAction<Cart | null>) => {
      // Ignorer si une mise à jour plus récente a été faite localement (moins de 2 secondes)
      if (Date.now() - state.lastUpdateTimestamp < 2000 && action.type.includes('updateCartItem')) {
        console.log(`[cartSlice] 🛡️ Réponse serveur ignorée pour protéger l'UI optimiste`);
        state.isLoading = false;
        return;
      }
      
      console.log(`[cartSlice] 💾 Mise à jour du state Redux avec les nouvelles données`);
      state.isLoading = false;
      
      // Si on reçoit null (souvent en mode hors ligne ou après un vidage sans retour)
      // on vide le panier localement par sécurité si c'est une action de vidage
      if (!action.payload) {
        if (action.type.includes('clearCart')) {
          state.cart = null;
          state.items = [];
          state.total = 0;
          state.itemsCount = 0;
        }
        return;
      }

      state.cart = action.payload;
      // Filtrer les items invalides
      state.items = (action.payload.items || []).filter(
        (item: any) => item && item.id && item.product && item.product.id
      );
      state.total = action.payload.total_price || 0;
      state.itemsCount = calculateItemsCount(state.items);
      console.log(`[cartSlice] 📊 Nouveau total: ${state.total}, Nouveaux articles: ${state.itemsCount}`);
    };

    builder
      // Fetch cart
      .addCase(fetchCart.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchCart.fulfilled, handleFulfilled)
      .addCase(fetchCart.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Add to cart
      .addCase(addToCart.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(addToCart.fulfilled, handleFulfilled)
      .addCase(addToCart.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Update cart item
      .addCase(updateCartItem.pending, (state) => {
        // Ne pas mettre isLoading à true pour les petites mises à jour pour éviter les sauts d'UI
        state.error = null;
      })
      .addCase(updateCartItem.fulfilled, handleFulfilled)
      .addCase(updateCartItem.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Remove from cart
      .addCase(removeFromCart.pending, (state) => {
        // Snappy UI
        state.error = null;
      })
      .addCase(removeFromCart.fulfilled, handleFulfilled)
      .addCase(removeFromCart.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Clear cart
      .addCase(clearCart.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(clearCart.fulfilled, handleFulfilled)
      .addCase(clearCart.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError, optimisticUpdateQuantity } = cartSlice.actions;
export default cartSlice.reducer;
