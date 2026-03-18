import { configureStore, combineReducers } from '@reduxjs/toolkit';
import { 
  persistStore, 
  persistReducer,
  FLUSH,
  REHYDRATE,
  PAUSE,
  PERSIST,
  PURGE,
  REGISTER,
} from 'redux-persist';
import { createEncryptedStorage, warmEncryptionKey } from './encryptedStorage';

// Pré-charger la clé avant la réhydratation des slices pour éviter
// les appels SecureStore concurrents qui déclenchent le timeout redux-persist
warmEncryptionKey();
import authReducer from './slices/authSlice';
import productReducer from './slices/productSlice';
import cartReducer from './slices/cartSlice';
import favoritesReducer from './slices/favoritesSlice';
import notificationReducer from './slices/notificationSlice';

// Créer le storage chiffré personnalisé
const encryptedStorage = createEncryptedStorage();

// timeout: 0 désactive le timeout redux-persist (évite les warnings quand le
// storage chiffré prend plus de 5s lors de la réhydratation simultanée des slices)
const PERSIST_TIMEOUT = 0;

// Configuration pour la slice auth
const authPersistConfig = {
  key: 'auth',
  storage: encryptedStorage,
  timeout: PERSIST_TIMEOUT,
  // token et refreshToken exclus : ils vivent uniquement dans expo-secure-store (hardware-backed)
  blacklist: ['isLoading', 'isLoggingIn', 'error', 'isLoadingLoyalty', 'sessionExpired', 'token', 'refreshToken'],
};

// Configuration pour la slice cart
const cartPersistConfig = {
  key: 'cart',
  storage: encryptedStorage,
  timeout: PERSIST_TIMEOUT,
  blacklist: ['isLoading', 'error'],
};

// Configuration pour la slice product
const productPersistConfig = {
  key: 'product',
  storage: encryptedStorage,
  timeout: PERSIST_TIMEOUT,
  blacklist: ['isLoading', 'isFetchingMore', 'isFetchingSimilarProducts', 'error'],
};

// Configuration pour la slice favorites
const favoritesPersistConfig = {
  key: 'favorites',
  storage: encryptedStorage,
  timeout: PERSIST_TIMEOUT,
  blacklist: ['isLoading', 'isToggling', 'error'],
};

// Configuration pour la slice notification
const notificationPersistConfig = {
  key: 'notification',
  storage: encryptedStorage,
  timeout: PERSIST_TIMEOUT,
};

// Combinaison des reducers avec persistance individuelle
const rootReducer = combineReducers({
  auth: persistReducer(authPersistConfig, authReducer),
  product: persistReducer(productPersistConfig, productReducer),
  cart: persistReducer(cartPersistConfig, cartReducer),
  favorites: persistReducer(favoritesPersistConfig, favoritesReducer),
  notification: persistReducer(notificationPersistConfig, notificationReducer),
});

// Configuration de la persistance racine (optionnelle si tout est géré au niveau slice)
const persistConfig = {
  key: 'root',
  storage: encryptedStorage,
  whitelist: [], // On ne persiste rien d'autre au niveau racine
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
});

export const persistor = persistStore(store);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

