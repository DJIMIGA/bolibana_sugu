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
  isLoading: boolean;
  error: string | null;
}

const initialState: CartState = {
  cart: null,
  items: [],
  total: 0,
  isLoading: false,
  error: null,
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
  async (data: { product: number; quantity: number; colors?: number[]; sizes?: number[] }, { rejectWithValue, dispatch }) => {
    try {
      if (connectivityService.getIsOnline()) {
        const response = await apiClient.post(API_ENDPOINTS.CART, data);
        await dispatch(fetchCart());
        return response.data;
      } else {
        // Mode hors ligne : ajouter à la file de synchronisation
        await syncService.addToQueue('CREATE', API_ENDPOINTS.CART, 'POST', data);
        // Mettre à jour le cache local
        const cached = await offlineCacheService.get<Cart>(CACHE_KEYS.CART);
        if (cached) {
          // Ajouter l'item localement (simulation)
          const newItem: CartItem = {
            id: Date.now(), // ID temporaire
            product: data.product as any,
            quantity: data.quantity,
            colors: data.colors,
            sizes: data.sizes,
          };
          cached.items.push(newItem);
          await offlineCacheService.set(CACHE_KEYS.CART, cached);
          return cached;
        }
        return rejectWithValue('Mode hors ligne - action en attente de synchronisation');
      }
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Erreur lors de l\'ajout au panier');
    }
  }
);

// Thunk pour mettre à jour un article du panier
export const updateCartItem = createAsyncThunk(
  'cart/updateCartItem',
  async (data: { itemId: number; quantity: number }, { rejectWithValue, dispatch }) => {
    try {
      if (connectivityService.getIsOnline()) {
        const response = await apiClient.patch(`${API_ENDPOINTS.CART}${data.itemId}/`, {
          quantity: data.quantity,
        });
        await dispatch(fetchCart());
        return response.data;
      } else {
        // Mode hors ligne
        await syncService.addToQueue('UPDATE', `${API_ENDPOINTS.CART}${data.itemId}/`, 'PATCH', { quantity: data.quantity });
        const cached = await offlineCacheService.get<Cart>(CACHE_KEYS.CART);
        if (cached) {
          const item = cached.items.find((i) => i.id === data.itemId);
          if (item) {
            item.quantity = data.quantity;
            await offlineCacheService.set(CACHE_KEYS.CART, cached);
          }
          return cached;
        }
        return rejectWithValue('Mode hors ligne - action en attente de synchronisation');
      }
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Erreur lors de la mise à jour');
    }
  }
);

// Thunk pour supprimer un article du panier
export const removeFromCart = createAsyncThunk(
  'cart/removeFromCart',
  async (itemId: number, { rejectWithValue, dispatch }) => {
    try {
      if (connectivityService.getIsOnline()) {
        await apiClient.delete(`${API_ENDPOINTS.CART}${itemId}/`);
        await dispatch(fetchCart());
        return itemId;
      } else {
        // Mode hors ligne
        await syncService.addToQueue('DELETE', `${API_ENDPOINTS.CART}${itemId}/`, 'DELETE', {});
        const cached = await offlineCacheService.get<Cart>(CACHE_KEYS.CART);
        if (cached) {
          cached.items = cached.items.filter((i) => i.id !== itemId);
          await offlineCacheService.set(CACHE_KEYS.CART, cached);
        }
        return itemId;
      }
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Erreur lors de la suppression');
    }
  }
);

// Thunk pour vider le panier
export const clearCart = createAsyncThunk(
  'cart/clearCart',
  async (_, { rejectWithValue, dispatch }) => {
    try {
      if (connectivityService.getIsOnline()) {
        await apiClient.delete(API_ENDPOINTS.CART);
        await dispatch(fetchCart());
        return null;
      } else {
        // Mode hors ligne
        const cached = await offlineCacheService.get<Cart>(CACHE_KEYS.CART);
        if (cached) {
          cached.items = [];
          await offlineCacheService.set(CACHE_KEYS.CART, cached);
        }
        return null;
      }
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Erreur lors du vidage du panier');
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
  },
  extraReducers: (builder) => {
    builder
      // Fetch cart
      .addCase(fetchCart.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchCart.fulfilled, (state, action) => {
        state.isLoading = false;
        state.cart = action.payload;
        state.items = action.payload.items || [];
        state.total = action.payload.total_price || 0;
      })
      .addCase(fetchCart.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Add to cart
      .addCase(addToCart.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(addToCart.fulfilled, (state, action) => {
        state.isLoading = false;
        if (action.payload) {
          state.cart = action.payload;
          state.items = action.payload.items || [];
          state.total = action.payload.total_price || 0;
        }
      })
      .addCase(addToCart.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Update cart item
      .addCase(updateCartItem.fulfilled, (state, action) => {
        if (action.payload) {
          state.cart = action.payload;
          state.items = action.payload.items || [];
          state.total = action.payload.total_price || 0;
        }
      })
      // Remove from cart
      .addCase(removeFromCart.fulfilled, (state) => {
        // Le panier sera rechargé via fetchCart
      })
      // Clear cart
      .addCase(clearCart.fulfilled, (state) => {
        state.cart = null;
        state.items = [];
        state.total = 0;
      });
  },
});

export const { clearError } = cartSlice.actions;
export default cartSlice.reducer;
