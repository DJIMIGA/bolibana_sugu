import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiClient from '../../services/api';
import { API_ENDPOINTS, CACHE_KEYS } from '../../utils/constants';
import { Product, Category } from '../../types';
import { offlineCacheService } from '../../services/offlineCacheService';
import { connectivityService } from '../../services/connectivityService';
import { mapProductFromBackend, mapCategoryFromBackend } from '../../utils/mappers';
import { cleanErrorForLog, cleanLogData } from '../../utils/helpers';

interface ProductState {
  products: Product[];
  categories: Category[];
  selectedProduct: Product | null;
  similarProducts: Product[];
  isFetchingSimilarProducts: boolean;
  b2bProducts: Product[];
  isFetchingB2B: boolean;
  filters: {
    category?: number;
    brand?: string;
    minPrice?: number;
    maxPrice?: number;
    isAvailable?: boolean;
  };
  searchQuery: string;
  isLoading: boolean;
  isFetchingMore: boolean;
  error: string | null;
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    hasNext: boolean;
  };
}

const initialState: ProductState = {
  products: [],
  categories: [],
  selectedProduct: null,
  similarProducts: [],
  isFetchingSimilarProducts: false,
  b2bProducts: [],
  isFetchingB2B: false,
  filters: {},
  searchQuery: '',
  isLoading: false,
  isFetchingMore: false,
  error: null,
  pagination: {
    page: 1,
    pageSize: 10,
    total: 0,
    hasNext: false,
  },
};

// Thunk pour récupérer les produits
export const fetchProducts = createAsyncThunk(
  'product/fetchProducts',
  async (params: { page?: number; search?: string; filters?: any; append?: boolean } = {}, { rejectWithValue }) => {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.search) queryParams.append('search', params.search);
      
      if (params.filters) {
        Object.entries(params.filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            queryParams.append(key, value.toString());
          }
        });
      }

      const endpoint = `${API_ENDPOINTS.PRODUCTS}?${queryParams.toString()}`;
      const response = await apiClient.get(endpoint);

      // Mapper les produits du backend
      const products = (response.data.results || response.data).map((p: any) => mapProductFromBackend(p));

      // Mettre en cache si en ligne
      if (connectivityService.getIsOnline()) {
        await offlineCacheService.set(CACHE_KEYS.PRODUCTS, products);
      }

      return {
        ...response.data,
        results: products,
        append: params.append || false,
      };
    } catch (error: any) {
      // Si c'est une erreur de mode hors ligne bloqué, utiliser le cache
      if (error.isOfflineBlocked) {
        const cached = await offlineCacheService.get<Product[]>(CACHE_KEYS.PRODUCTS);
        if (cached) {
          return { results: cached, count: cached.length, append: false };
        }
        return rejectWithValue('Mode hors ligne - Aucune donnée en cache disponible');
      }
      
      // Essayer de récupérer depuis le cache
      const cached = await offlineCacheService.get<Product[]>(CACHE_KEYS.PRODUCTS);
      if (cached) {
        return { results: cached, count: cached.length, append: false };
      }
      const errorMsg = cleanErrorForLog(error);
      return rejectWithValue(errorMsg || 'Erreur de chargement des produits');
    }
  }
);

// Thunk pour récupérer les catégories
export const fetchCategories = createAsyncThunk(
  'product/fetchCategories',
  async (_, { rejectWithValue }) => {
  try {
      let allCategories: any[] = [];
      let nextUrl: string | null = API_ENDPOINTS.CATEGORIES;

      // Charger toutes les pages de catégories normales
      while (nextUrl) {
        const response = await apiClient.get(nextUrl);
        const categoriesData = response.data.results || [];
        allCategories = [...allCategories, ...categoriesData];
        
        // Vérifier s'il y a une page suivante
        nextUrl = response.data.next ? response.data.next.replace(apiClient.defaults.baseURL || '', '') : null;
        if (nextUrl && !nextUrl.startsWith('/')) {
          nextUrl = '/' + nextUrl;
        }
      }

      // Récupérer aussi les catégories synchronisées depuis B2B
      try {
        const b2bResponse = await apiClient.get(API_ENDPOINTS.B2B.CATEGORIES);
        const b2bCategoriesData = b2bResponse.data.results || [];
        
        // Fusionner les catégories B2B avec les catégories normales
        // Utiliser un Map pour éviter les doublons par ID
        const categoriesMap = new Map<number, any>();
        
        // Ajouter d'abord les catégories normales
        allCategories.forEach((cat: any) => {
          if (cat.id) {
            categoriesMap.set(cat.id, cat);
          }
        });
        
        // Ajouter les catégories B2B (elles remplaceront les doublons si même ID)
        b2bCategoriesData.forEach((cat: any) => {
          if (cat.id) {
            categoriesMap.set(cat.id, cat);
          }
        });
        
        // Convertir le Map en tableau
        allCategories = Array.from(categoriesMap.values());
      } catch (b2bError: any) {
        // Si l'endpoint B2B n'est pas disponible, continuer avec les catégories normales
        // Warning désactivé pour réduire la pollution de la console
        // const { cleanErrorForLog } = require('../../utils/helpers');
        // const errorMessage = cleanErrorForLog(b2bError);
        // console.warn('[productSlice] ⚠️ Catégories B2B non disponibles:', errorMessage);
        // Ne pas rejeter, continuer avec les catégories normales
      }

      if (!Array.isArray(allCategories) || allCategories.length === 0) {
        return rejectWithValue('Aucune catégorie trouvée');
      }

      // Mapper les catégories du backend
      const categories = allCategories.map((c: any) => mapCategoryFromBackend(c));

      // Mettre en cache si en ligne
    if (connectivityService.getIsOnline()) {
        await offlineCacheService.set(CACHE_KEYS.CATEGORIES, categories);
    }

      return categories;
  } catch (error: any) {
      // Si c'est une erreur de mode hors ligne bloqué, utiliser le cache
      if (error.isOfflineBlocked) {
        const cached = await offlineCacheService.get<Category[]>(CACHE_KEYS.CATEGORIES);
        if (cached) {
          return cached;
        }
        return rejectWithValue('Mode hors ligne - Aucune catégorie en cache disponible');
      }
      
      if (error.code === 'OFFLINE_MODE_FORCED' || error.message === 'OFFLINE_MODE_FORCED' || error.isOfflineBlocked) {
        // En mode hors ligne forcé, ne pas logger d'erreur, juste essayer le cache
      } else {
        console.error('❌ Error fetching categories:', error);
        console.error('❌ Error details:', cleanErrorForLog(error));
      }
      
      // Essayer de récupérer depuis le cache
      const cached = await offlineCacheService.get<Category[]>(CACHE_KEYS.CATEGORIES);
      if (cached) {
        // Log désactivé pour réduire la pollution de la console
        // console.log('📦 Using cached categories:', cached.length);
        return cached;
      }
      return rejectWithValue(error.response?.data?.detail || error.message || 'Erreur de chargement des catégories');
    }
  }
);

// Thunk pour récupérer les détails d'un produit
export const fetchProductDetail = createAsyncThunk(
  'product/fetchProductDetail',
  async (slug: string, { rejectWithValue }) => {
    try {
      const response = await apiClient.get(`${API_ENDPOINTS.PRODUCTS}${slug}/`);
      return mapProductFromBackend(response.data);
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Erreur de chargement du produit');
    }
  }
);

// Thunk pour récupérer les produits similaires
export const fetchSimilarProducts = createAsyncThunk(
  'product/fetchSimilarProducts',
  async (productId: number, { rejectWithValue }) => {
    try {
      const response = await apiClient.get(`${API_ENDPOINTS.PRODUCTS}${productId}/similar_products/`);
      return response.data.map((p: any) => mapProductFromBackend(p));
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Erreur de chargement des produits similaires');
    }
  }
);

// Thunk pour rechercher des produits
export const searchProducts = createAsyncThunk(
  'product/searchProducts',
  async (query: string, { rejectWithValue }) => {
    try {
      const response = await apiClient.get(`${API_ENDPOINTS.PRODUCTS}?search=${encodeURIComponent(query)}`);
      const products = (response.data.results || response.data).map((p: any) => mapProductFromBackend(p));
      return products;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Erreur de recherche');
    }
  }
);

// Thunk pour récupérer les produits B2B synchronisés
export const fetchB2BProducts = createAsyncThunk(
  'product/fetchB2BProducts',
  async (params: { page?: number; pageSize?: number } = {}, { rejectWithValue }) => {
    try {
      // L'endpoint synced ne supporte pas la pagination, on récupère tout
      const endpoint = API_ENDPOINTS.B2B.PRODUCTS;
      // Logs désactivés pour réduire la pollution de la console
      // console.log('[B2B] 🚀 Début fetchB2BProducts, endpoint:', endpoint);
      
      const response = await apiClient.get(endpoint);

      // Mapper les produits du backend
      const rawProducts = response.data.results || response.data || [];
      // console.log(`[B2B] 📊 Réponse API - count: ${response.data.count || 'N/A'}, results length: ${Array.isArray(rawProducts) ? rawProducts.length : 'N/A'}`);
      
      // Logger les IDs bruts avant mapping (désactivé)
      // if (Array.isArray(rawProducts) && rawProducts.length > 0) {
      //   const rawIds = rawProducts.map((p: any) => p.id).filter((id: any) => id !== undefined);
      //   console.log(`[B2B] 🔢 IDs produits bruts depuis API: [${rawIds.join(', ')}]`);
      // }
      
      const allProducts = (Array.isArray(rawProducts) ? rawProducts : []).map((p: any) => {
        try {
          const mapped = mapProductFromBackend(p);
          // Vérifier que le produit mappé a les champs essentiels
          if (!mapped.title || !mapped.id) {
            console.warn(`[B2B] ⚠️ Produit ignoré (pas de titre ou ID):`, { id: p.id, title: p.title });
            return null;
          }
          return mapped;
        } catch (error) {
          console.warn(`[B2B] ⚠️ Erreur mapping produit ID ${p.id}:`, error);
          return null;
        }
      }).filter((p: Product | null): p is Product => p !== null);
      
      // Logger les IDs après mapping (désactivé pour réduire la pollution)
      // if (allProducts.length > 0) {
      //   const mappedIds = allProducts.map(p => p.id);
      //   console.log(`[B2B] ✅ ${allProducts.length} produits mappés avec succès`);
      //   console.log(`[B2B] 🔢 IDs produits mappés: [${mappedIds.join(', ')}]`);
      //   if (allProducts.length > 0) {
      //     console.log(`[B2B] 📦 Premier produit: ID=${allProducts[0].id}, Title="${allProducts[0].title}"`);
      //   }
      // }
      
      // Limiter côté client si un pageSize est demandé
      const products = params.pageSize && params.pageSize > 0 
        ? allProducts.slice(0, params.pageSize)
        : allProducts;
      
      // Log silencieux si pas de changement significatif

      return {
        ...response.data,
        results: products,
      };
    } catch (error: any) {
      const status = error.response?.status;
      const errorMessage = cleanErrorForLog(error) || 'Erreur de chargement des produits B2B';
      
      // Logger uniquement les infos essentielles (sans HTML)
      if (status) {
        console.error(`[B2B] ❌ Erreur ${status}: ${errorMessage}`);
      } else {
        console.error(`[B2B] ❌ Erreur: ${errorMessage}`);
      }
      
      // Essayer de récupérer depuis le cache en cas d'erreur
      const cached = await offlineCacheService.get<Product[]>(CACHE_KEYS.PRODUCTS);
      if (cached) {
        return { results: cached, count: cached.length };
      }
      
      return rejectWithValue(errorMessage);
    }
  }
);

const productSlice = createSlice({
  name: 'product',
  initialState,
  reducers: {
    setSelectedProduct: (state, action: PayloadAction<Product | null>) => {
      state.selectedProduct = action.payload;
    },
    setFilters: (state, action: PayloadAction<ProductState['filters']>) => {
      state.filters = { ...state.filters, ...action.payload };
      state.pagination.page = 1; // Reset à la première page
    },
    clearFilters: (state) => {
      state.filters = {};
      state.pagination.page = 1;
    },
    setSearchQuery: (state, action: PayloadAction<string>) => {
      state.searchQuery = action.payload;
      state.pagination.page = 1;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch products
      .addCase(fetchProducts.pending, (state, action) => {
        const isAppend = action.meta.arg?.append;
        if (isAppend) {
          state.isFetchingMore = true;
        } else {
          state.isLoading = true;
        }
        state.error = null;
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isFetchingMore = false;
        const data = action.payload;
        const isAppend = data.append;

        if (Array.isArray(data)) {
          state.products = data;
        } else {
          if (isAppend) {
            // Éviter les doublons
            const existingIds = new Set(state.products.map(p => p.id));
            const newProducts = (data.results || []).filter((p: Product) => !existingIds.has(p.id));
            state.products = [...state.products, ...newProducts];
          } else {
            state.products = data.results || [];
          }

          state.pagination = {
            page: data.page || (isAppend ? state.pagination.page + 1 : 1),
            pageSize: data.page_size || state.pagination.pageSize,
            total: data.count || data.results?.length || 0,
            hasNext: !!data.next,
          };
        }
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.isLoading = false;
        state.isFetchingMore = false;
        state.error = action.payload as string;
      })
      // Fetch categories
      .addCase(fetchCategories.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.isLoading = false;
        state.categories = action.payload;
      })
      .addCase(fetchCategories.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch product detail
      .addCase(fetchProductDetail.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchProductDetail.fulfilled, (state, action) => {
        state.isLoading = false;
        state.selectedProduct = action.payload;
      })
      .addCase(fetchProductDetail.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch similar products
      .addCase(fetchSimilarProducts.pending, (state) => {
        state.isFetchingSimilarProducts = true;
      })
      .addCase(fetchSimilarProducts.fulfilled, (state, action) => {
        state.isFetchingSimilarProducts = false;
        state.similarProducts = action.payload;
      })
      .addCase(fetchSimilarProducts.rejected, (state, action) => {
        state.isFetchingSimilarProducts = false;
        state.error = action.payload as string;
      })
      // Search products
      .addCase(searchProducts.fulfilled, (state, action) => {
        state.products = action.payload;
      })
      // Fetch B2B products
      .addCase(fetchB2BProducts.pending, (state) => {
        state.isFetchingB2B = true;
        state.error = null;
      })
      .addCase(fetchB2BProducts.fulfilled, (state, action) => {
        state.isFetchingB2B = false;
        const data = action.payload;
        const products = data.results || [];
        // Logs désactivés pour réduire la pollution de la console
        // console.log(`[B2B] 📥 Reducer - Produits reçus: ${products.length}, count API: ${data.count || 'N/A'}`);
        
        // S'assurer que seuls les produits valides sont stockés
        const validProducts = products.filter((p: Product) => p && p.id && p.title);
        // console.log(`[B2B] ✅ Reducer - Produits valides après filtre: ${validProducts.length}`);
        
        if (validProducts.length > 0) {
          const validIds = validProducts.map(p => p.id);
          // console.log(`[B2B] 🔢 Reducer - IDs produits valides: [${validIds.join(', ')}]`);
          
          // Vérifier que tous les produits ont bien un ID unique
          const uniqueIds = new Set(validProducts.map(p => p.id));
          if (uniqueIds.size !== validProducts.length) {
            console.warn(`[B2B] ⚠️ Produits dupliqués détectés! Unique: ${uniqueIds.size}, Total: ${validProducts.length}`);
          }
        }
        
        state.b2bProducts = validProducts;
      })
      .addCase(fetchB2BProducts.rejected, (state, action) => {
        state.isFetchingB2B = false;
        state.error = action.payload as string;
        // Ne logger que le message d'erreur nettoyé (sans HTML)
        const errorMsg = cleanLogData(action.payload as string);
        console.error('[B2B] ❌ Erreur:', errorMsg);
      });
  },
});

export const {
  setSelectedProduct,
  setFilters,
  clearFilters,
  setSearchQuery,
  clearError,
} = productSlice.actions;
export default productSlice.reducer;
