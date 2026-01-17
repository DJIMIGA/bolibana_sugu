import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiClient from '../../services/api';
import { API_ENDPOINTS, CACHE_KEYS } from '../../utils/constants';
import { Cart, CartItem } from '../../types';
import { offlineCacheService } from '../../services/offlineCacheService';
import { connectivityService } from '../../services/connectivityService';
import { syncService } from '../../services/syncService';
import { mapCartFromBackend, mapProductFromBackend } from '../../utils/mappers';

interface CartState {
  cart: Cart | null;
  items: CartItem[];
  total: number;
  itemsCount: number; // Nombre total d'articles (produits au poids comptés comme 1)
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

// Déterminer si un item est vendu au poids
const isWeightedCartItem = (item: CartItem): boolean => {
  const specs = item?.product?.specifications || {};
  return specs.sold_by_weight === true ||
    specs.unit_type === 'weight' ||
    specs.unit_type === 'kg' ||
    specs.unit_type === 'kilogram';
};

const getCartItemUnitPrice = (item: CartItem): number => {
  if (!item || !item.product) return 0;
  if (isWeightedCartItem(item)) {
    const specs = item.product.specifications || {};
    const discountPricePerKg = specs.discount_price_per_kg;
    if (discountPricePerKg && discountPricePerKg > 0) {
      return discountPricePerKg;
    }
    const pricePerKg = specs.price_per_kg;
    if (pricePerKg && pricePerKg > 0) {
      return pricePerKg;
    }
  }
  return item.product.discount_price || item.product.price || 0;
};

// Fonction utilitaire pour calculer le nombre total d'articles
const calculateItemsCount = (items: CartItem[]): number => {
  return items.reduce((sum, item) => {
    if (!item || !item.product) return sum;
    const quantity = typeof item.quantity === 'number' && !isNaN(item.quantity) ? item.quantity : 0;
    if (isWeightedCartItem(item)) {
      return sum + (quantity > 0 ? 1 : 0);
    }
    return sum + Math.round(quantity);
  }, 0);
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
  async (data: { product: number; quantity: number; variant?: number; colors?: number[]; sizes?: number[] }, { rejectWithValue, getState }) => {
    try {
      if (data.quantity <= 0) return rejectWithValue('La quantité doit être supérieure à 0');

      if (connectivityService.getIsOnline()) {
        // S'assurer que la quantité est bien un nombre (préserver les décimales pour les produits au poids)
        const quantity = typeof data.quantity === 'number' ? data.quantity : parseFloat(String(data.quantity));
        
        if (__DEV__) {
          console.log('[cartSlice] ⚖️ Ajout au panier - quantité envoyée:', {
            productId: data.product,
            quantity: data.quantity,
            quantityType: typeof data.quantity,
            parsedQuantity: quantity,
          });
        }

        const payload: any = { product: data.product, quantity: quantity };
        if (data.variant) payload.variant = data.variant;
        if (data.colors?.length) payload.colors = data.colors;
        if (data.sizes?.length) payload.sizes = data.sizes;

        const response = await apiClient.post(API_ENDPOINTS.CART, payload);
        
        if (__DEV__) {
          console.log('[cartSlice] ⚖️ Réponse backend après ajout:', {
            responseData: response.data,
            items: response.data?.items || response.data?.cart_items || [],
            sentQuantity: quantity,
          });
        }
        
        // Mapper le panier et corriger les quantités à 0 si nécessaire
        const cart = mapCartFromBackend(response.data);
        
        // Si le backend retourne quantity: 0, utiliser la quantité envoyée
        if (cart && cart.items) {
          cart.items.forEach((item: CartItem) => {
            if (item.quantity === 0 && item.product.id === data.product) {
              if (__DEV__) {
                console.warn('[cartSlice] ⚠️ Backend retourne quantity: 0, correction avec quantité envoyée:', {
                  itemId: item.id,
                  productId: item.product.id,
                  backendQuantity: 0,
                  correctedQuantity: quantity,
                });
              }
              item.quantity = quantity;
            }
          });
        }
        
        return cart;
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
      if (connectivityService.getIsOnline()) {
        // S'assurer que la quantité est bien un nombre (préserver les décimales pour les produits au poids)
        const quantity = typeof data.quantity === 'number' ? data.quantity : parseFloat(String(data.quantity));
        
        const response = await apiClient.patch(`${API_ENDPOINTS.CART}${data.itemId}/`, {
          quantity: quantity,
        });

        return mapCartFromBackend(response.data);
      }
      return null;
    } catch (error: any) {
      console.error(`[cartSlice] ❌ Erreur API updateCartItem:`, cleanErrorForLog(error));
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.detail || 
                          error.message || 
                          'Erreur lors de la mise à jour';
      return rejectWithValue(errorMessage);
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
        const response = await apiClient.delete(url);
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

// Thunk pour enrichir les produits du panier avec leurs spécifications
export const enrichCartProducts = createAsyncThunk(
  'cart/enrichCartProducts',
  async (_, { getState, rejectWithValue }) => {
    try {
      const state = getState() as { cart: CartState };
      const items = state.cart.items || [];
      
      if (items.length === 0 || !connectivityService.getIsOnline()) {
        return null;
      }

      // Enrichir les produits qui n'ont pas de spécifications
      const enrichedItems = await Promise.all(
        items.map(async (item: CartItem) => {
          // Si le produit a déjà des spécifications, ne pas le réenrichir
          if (item.product.specifications && Object.keys(item.product.specifications).length > 0) {
            return item;
          }

          try {
            // L'API utilise le slug, pas l'ID pour récupérer un produit
            const productSlug = item.product.slug;
            if (!productSlug) {
              if (__DEV__) {
                console.warn('[cartSlice] ⚠️ Produit sans slug, impossible d\'enrichir:', item.product.id);
              }
              return item;
            }

            // Récupérer les détails complets du produit via son slug
            const productResponse = await apiClient.get(`${API_ENDPOINTS.PRODUCTS}${productSlug}/`);
            const enrichedProduct = mapProductFromBackend(productResponse.data);
            
            // Mettre à jour le produit avec les spécifications enrichies
            return {
              ...item,
              product: {
                ...item.product,
                specifications: enrichedProduct.specifications || item.product.specifications,
              },
            };
          } catch (error: any) {
            // En cas d'erreur, retourner l'item tel quel
            if (__DEV__) {
              console.warn('[cartSlice] ⚠️ Impossible d\'enrichir le produit:', {
                productId: item.product.id,
                productSlug: item.product.slug,
                error: error?.message || error,
                status: error?.response?.status,
              });
            }
            return item;
          }
        })
      );

      // Retourner les items enrichis
      return enrichedItems;
    } catch (error: any) {
      return rejectWithValue('Erreur lors de l\'enrichissement des produits');
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
        const unitPrice = getCartItemUnitPrice(item);
        state.total = state.total + (unitPrice * (quantity - oldQuantity));
      }
    }
  },
  extraReducers: (builder) => {
    const handleFulfilled = (state: CartState, action: PayloadAction<Cart | null>) => {
      // Ignorer si une mise à jour plus récente a été faite localement (moins de 2 secondes)
      if (Date.now() - state.lastUpdateTimestamp < 2000 && action.type.includes('updateCartItem')) {
        state.isLoading = false;
        return;
      }
      
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
      const newItems = (action.payload.items || []).filter(
        (item: any) => item && item.id && item.product && item.product.id
      );
      
      // Si on vient d'ajouter un produit et que le backend retourne quantity: 0,
      // préserver la quantité optimiste si elle existe
      if (action.type.includes('addToCart')) {
        // Trouver le dernier item ajouté (généralement le dernier dans la liste)
        // ou chercher par productId si on connaît le produit ajouté
        newItems.forEach((newItem: CartItem) => {
          // Si le backend retourne quantity: 0, chercher dans les items précédents
          if (newItem.quantity === 0) {
            // Chercher un item avec le même productId dans l'ancien state
            const existingItem = state.items.find(i => 
              i.product.id === newItem.product.id
            );
            // Si on trouve un item existant avec une quantité > 0, préserver cette quantité
            if (existingItem && existingItem.quantity > 0) {
              if (__DEV__) {
                console.warn('[cartSlice] ⚠️ Backend retourne quantity: 0, préservation de la quantité optimiste:', {
                  itemId: newItem.id,
                  productId: newItem.product.id,
                  backendQuantity: newItem.quantity,
                  preservedQuantity: existingItem.quantity,
                });
              }
              newItem.quantity = existingItem.quantity;
            } else {
              // Si pas d'item existant, c'est un nouveau produit
              // Le backend devrait retourner la bonne quantité, mais si c'est 0,
              // on peut essayer de récupérer depuis l'action si disponible
              if (__DEV__) {
                console.warn('[cartSlice] ⚠️ Backend retourne quantity: 0 pour un nouveau produit:', {
                  itemId: newItem.id,
                  productId: newItem.product.id,
                });
              }
            }
          }
        });
      }
      
      state.items = newItems;
      state.total = action.payload.total_price || 0;
      state.itemsCount = calculateItemsCount(state.items);
    };

    builder
      // Fetch cart
      .addCase(fetchCart.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchCart.fulfilled, handleFulfilled)
      // Enrich cart products
      .addCase(enrichCartProducts.fulfilled, (state, action) => {
        if (action.payload && Array.isArray(action.payload)) {
          // Mettre à jour les items avec les produits enrichis
          state.items = action.payload;
        }
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
