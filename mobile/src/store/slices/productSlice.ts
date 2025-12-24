import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiClient from '../../services/api';
import { API_ENDPOINTS, CACHE_KEYS } from '../../utils/constants';
import { Product, Category } from '../../types';
import { offlineCacheService } from '../../services/offlineCacheService';
import { connectivityService } from '../../services/connectivityService';
import { mapProductFromBackend, mapCategoryFromBackend } from '../../utils/mappers';

interface ProductState {
  products: Product[];
  categories: Category[];
  selectedProduct: Product | null;
  similarProducts: Product[];
  isFetchingSimilarProducts: boolean;
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
      // Essayer de récupérer depuis le cache
      const cached = await offlineCacheService.get<Product[]>(CACHE_KEYS.PRODUCTS);
      if (cached) {
        return { results: cached, count: cached.length, append: false };
      }
      return rejectWithValue(error.response?.data?.detail || 'Erreur de chargement des produits');
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

      // Charger toutes les pages de catégories
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
      console.error('❌ Error fetching categories:', error);
      console.error('❌ Error details:', error.response?.data || error.message);
      
      // Essayer de récupérer depuis le cache
    const cached = await offlineCacheService.get<Category[]>(CACHE_KEYS.CATEGORIES);
    if (cached) {
        console.log('📦 Using cached categories:', cached.length);
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
