import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../utils/constants';
import { Product } from '../../types';
import { logoutAsync } from './authSlice';
import { mapProductFromBackend } from '../../utils/mappers';

interface Favorite {
  id: number;
  product: Product;
  created_at: string;
}

interface FavoritesState {
  favorites: Favorite[];
  favoriteProductIds: number[];
  isLoading: boolean;
  isToggling: boolean;
  error: string | null;
}

const initialState: FavoritesState = {
  favorites: [],
  favoriteProductIds: [],
  isLoading: false,
  isToggling: false,
  error: null,
};

export const fetchFavorites = createAsyncThunk(
  'favorites/fetchFavorites',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.FAVORITES);
      const raw = response.data.results ?? response.data;
      // Mapper chaque produit imbriqué pour normaliser image/image_urls
      return (raw as any[]).map((fav) => ({
        ...fav,
        product: mapProductFromBackend(fav.product),
      }));
    } catch (error: any) {
      // Silencieux : ne pas afficher d'erreur si l'endpoint n'est pas encore disponible
      return rejectWithValue(null);
    }
  }
);

export const toggleFavorite = createAsyncThunk(
  'favorites/toggleFavorite',
  async (productId: number, { rejectWithValue }) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.FAVORITES_TOGGLE, { product_id: productId });
      return { productId, ...response.data };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Erreur lors de la mise à jour des favoris');
    }
  }
);

const favoritesSlice = createSlice({
  name: 'favorites',
  initialState,
  reducers: {
    clearFavorites(state) {
      state.favorites = [];
      state.favoriteProductIds = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchFavorites.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchFavorites.fulfilled, (state, action: PayloadAction<Favorite[]>) => {
        state.isLoading = false;
        state.favorites = action.payload;
        state.favoriteProductIds = action.payload.map((f) => f.product.id);
      })
      .addCase(fetchFavorites.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(toggleFavorite.pending, (state) => {
        state.isToggling = true;
      })
      .addCase(toggleFavorite.fulfilled, (state, action) => {
        state.isToggling = false;
        const { productId, is_favorite, id } = action.payload;
        if (is_favorite) {
          if (!state.favoriteProductIds.includes(productId)) {
            state.favoriteProductIds.push(productId);
          }
        } else {
          state.favoriteProductIds = state.favoriteProductIds.filter((pid) => pid !== productId);
          state.favorites = state.favorites.filter((f) => f.product.id !== productId);
        }
      })
      .addCase(toggleFavorite.rejected, (state, action) => {
        state.isToggling = false;
        state.error = action.payload as string;
      })
      // Logout : vider les favoris
      .addCase(logoutAsync.fulfilled, (state) => {
        state.favorites = [];
        state.favoriteProductIds = [];
        state.isLoading = false;
        state.isToggling = false;
        state.error = null;
      });
  },
});

export const { clearFavorites } = favoritesSlice.actions;
export default favoritesSlice.reducer;
