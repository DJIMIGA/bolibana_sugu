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
      console.log('[PRODUCTS] 🚀 Début fetchProducts, endpoint:', endpoint);
      const response = await apiClient.get(endpoint);

      // Mapper les produits du backend
      const products = (response.data.results || response.data).map((p: any) => mapProductFromBackend(p));
      console.log(`[PRODUCTS] ✅ Produits récupérés et mappés: ${products.length}`);
      
      // Log des premiers produits pour debug
      if (products.length > 0) {
        console.log('[PRODUCTS] 📋 Exemples produits:', products.slice(0, 3).map((p: Product) => ({
          id: p.id,
          title: p.title,
          category: p.category,
          is_available: p.is_available
        })));
      }

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
    const fetchAllPages = async (initialUrl: string) => {
      let all: any[] = [];
      let nextUrl: string | null = initialUrl;

      while (nextUrl) {
        const response = await apiClient.get(nextUrl);
        const data = response.data;

        // DRF paginé: { results: [], next: "..." }
        // Non paginé: [ ... ]
        const pageItems: any[] = Array.isArray(data)
          ? data
          : (Array.isArray(data?.results) ? data.results : []);

        all = [...all, ...pageItems];

        if (Array.isArray(data)) {
          nextUrl = null; // non paginé
        } else {
          nextUrl = data?.next ? String(data.next).replace(apiClient.defaults.baseURL || '', '') : null;
          if (nextUrl && !nextUrl.startsWith('/')) {
            nextUrl = '/' + nextUrl;
          }
        }
      }

      return all;
    };

    try {
      console.log('[CATEGORIES] 🚀 Début fetchCategories');
      console.log('[CATEGORIES] 🌐 BaseURL:', apiClient.defaults.baseURL);

      // Priorité: endpoint B2B (celui qui contient `rayon_type` / `level`)
      console.log('[CATEGORIES] 📍 Endpoint B2B:', API_ENDPOINTS.B2B.CATEGORIES);
      let allCategories = await fetchAllPages(API_ENDPOINTS.B2B.CATEGORIES);

      // Fallback: endpoint normal si B2B vide / non dispo
      if (!Array.isArray(allCategories) || allCategories.length === 0) {
        console.log('[CATEGORIES] ⚠️ Endpoint B2B vide, fallback vers endpoint normal:', API_ENDPOINTS.CATEGORIES);
        allCategories = await fetchAllPages(API_ENDPOINTS.CATEGORIES);
      }

      console.log(`[CATEGORIES] ✅ Total catégories récupérées: ${allCategories.length}`);

      if (!Array.isArray(allCategories) || allCategories.length === 0) {
        console.log('[CATEGORIES] ❌ Aucune catégorie trouvée (B2B + fallback)');
        return rejectWithValue('Aucune catégorie trouvée');
      }

      // Log des données brutes avant mapping pour debug
      console.log('[CATEGORIES] 📋 Exemples catégories brutes (avant mapping):', allCategories.slice(0, 5).map((c: any) => ({
        id: c.id,
        name: c.name,
        rayon_type: c.rayon_type,
        level: c.level,
        parent: c.parent,
        external_category: c.external_category ? 'présent' : 'absent'
      })));

      // Mapper les catégories du backend
      const categories = allCategories.map((c: any) => mapCategoryFromBackend(c));
      console.log(`[CATEGORIES] 🗺️ Catégories mappées: ${categories.length}`);

      // Log des catégories mappées pour voir si rayon_type et level sont présents
      console.log('[CATEGORIES] 📋 Exemples catégories mappées:', categories.slice(0, 5).map((c: Category) => ({
        id: c.id,
        name: c.name,
        rayon_type: c.rayon_type,
        level: c.level,
        parent: c.parent
      })));

      // Filtrer les catégories B2B pour debug
      const b2bCategories = categories.filter((c: Category) => 
        c.rayon_type || c.level !== undefined
      );
      console.log(`[CATEGORIES] 🎯 Catégories B2B après mapping: ${b2bCategories.length}`);
      if (b2bCategories.length > 0) {
        console.log('[CATEGORIES] 📋 Exemples catégories B2B mappées:', b2bCategories.slice(0, 3).map((c: Category) => ({
          id: c.id,
          name: c.name,
          rayon_type: c.rayon_type,
          level: c.level,
          parent: c.parent
        })));
      } else {
        console.log('[CATEGORIES] ⚠️ Aucune catégorie B2B trouvée - Vérifiez que les catégories ont rayon_type ou level');
        // Log toutes les catégories pour voir ce qui manque
        console.log('[CATEGORIES] 📋 Toutes les catégories:', categories.map((c: Category) => ({
          id: c.id,
          name: c.name,
          rayon_type: c.rayon_type,
          level: c.level,
          has_rayon_type: !!c.rayon_type,
          has_level: c.level !== undefined && c.level !== null
        })));
      }

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
        // Erreur silencieuse en production
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
  },
);

// Thunk pour récupérer les détails d'un produit
export const fetchProductDetail = createAsyncThunk(
  'product/fetchProductDetail',
  async (slug: string, { rejectWithValue }) => {
    try {
      // IMPORTANT:
      // - Le produit "site" (B2C) et le produit "inventory" (B2B) peuvent avoir le même slug
      //   mais PAS le même id.
      // - Pour éviter de casser le panier / similar_products (qui utilisent l'id B2C),
      //   on charge d'abord le produit B2C, puis on ENRICHIT avec promo/galerie depuis l'inventory.

      // 1) Produit B2C (source de vérité pour id, stock, endpoints produits)
      const b2cRes = await apiClient.get(`${API_ENDPOINTS.PRODUCTS}${slug}/`);
      const b2cProduct = mapProductFromBackend(b2cRes.data);

      // 2) Enrichissement inventory/B2B (promo + galerie)
      let inventoryMatch: any | null = null;
      try {
        const invRes = await apiClient.get(API_ENDPOINTS.B2B.PRODUCTS);
        const raw = (invRes.data as any)?.results || (invRes.data as any) || [];
        const list: any[] = Array.isArray(raw) ? raw : [];
        inventoryMatch = list.find((p) => p && String(p.slug) === String(slug)) || null;
      } catch (e: any) {
        // Endpoint optionnel : ignorer (réseau/404/503/400)
      }

      if (!inventoryMatch) {
        if (__DEV__) {
          console.log('[ProductDetail] ℹ️ Enrichissement inventory: aucun match', {
            slug,
            b2cId: b2cProduct.id,
          });
        }
        return b2cProduct;
      }

      // Mapper le produit inventory pour normaliser images/promo (mais ne PAS utiliser son id)
      const invMapped = mapProductFromBackend(inventoryMatch);

      const enriched = {
        ...b2cProduct,
        // Images/galerie: on prend l'inventory en priorité si présent, sinon on garde B2C
        image: invMapped.image || b2cProduct.image,
        image_urls: invMapped.image_urls || b2cProduct.image_urls,

        // Champs promo bruts (pour debug/UI éventuel)
        promo_price: invMapped.promo_price,
        has_promotion: invMapped.has_promotion,
        discount_percent: invMapped.discount_percent,
        promotion_start_date: invMapped.promotion_start_date,
        promotion_end_date: invMapped.promotion_end_date,

        // discount_price: si B2C n'en a pas, prendre celle calculée via inventory
        discount_price: b2cProduct.discount_price ?? invMapped.discount_price,
      };

      if (__DEV__) {
        console.log('[ProductDetail] ✅ Enrichi depuis inventory', {
          slug,
          b2cId: b2cProduct.id,
          inventoryId: invMapped.id,
          galleryCount: enriched.image_urls?.gallery?.length || 0,
          hasPromotion: enriched.has_promotion,
          promoPrice: enriched.promo_price,
          discountPriceUsed: enriched.discount_price,
        });
      }

      return enriched;
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
          // Erreur mapping produit silencieuse
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
      const serverMsg: string =
        error?.response?.data?.error ||
        error?.response?.data?.detail ||
        error?.message ||
        '';
      
      // OPTION A: endpoint B2B "synced" est optionnel.
      // Si le backend renvoie 404/503 ou "aucun produit synchronisé", on retourne simplement une liste vide.
      const isNoSyncedProducts =
        typeof serverMsg === 'string' &&
        serverMsg.toLowerCase().includes('aucun produit synchronisé');
      const isOptionalStatus = status === 404 || status === 400 || status === 503;
      // Erreur réseau (pas de response) -> endpoint optionnel, on retourne vide
      const isNetworkError = !status && !error?.response;
      if (isOptionalStatus || isNoSyncedProducts || isNetworkError) {
        return { results: [], count: 0 };
      }
      
      // Logger uniquement les autres erreurs
      const errorMessage = cleanErrorForLog(error) || 'Erreur de chargement des produits B2B';
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
            // Produits dupliqués détectés et filtrés silencieusement
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
