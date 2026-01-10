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
import { createEncryptedStorage } from './encryptedStorage';
import authReducer from './slices/authSlice';
import productReducer from './slices/productSlice';
import cartReducer from './slices/cartSlice';

// Créer le storage chiffré personnalisé
const encryptedStorage = createEncryptedStorage();

console.log('🔐 Redux Persist Encryption configured at storage level');

// Configuration pour la slice auth
const authPersistConfig = {
  key: 'auth',
  storage: encryptedStorage,
  blacklist: ['isLoading', 'isLoggingIn', 'error', 'isLoadingLoyalty', 'sessionExpired'],
};

// Configuration pour la slice cart
const cartPersistConfig = {
  key: 'cart',
  storage: encryptedStorage,
  blacklist: ['isLoading', 'error'],
};

// Configuration pour la slice product
const productPersistConfig = {
  key: 'product',
  storage: encryptedStorage,
  blacklist: ['isLoading', 'isFetchingMore', 'isFetchingSimilarProducts', 'error'],
};

// Combinaison des reducers avec persistance individuelle
const rootReducer = combineReducers({
  auth: persistReducer(authPersistConfig, authReducer),
  product: persistReducer(productPersistConfig, productReducer),
  cart: persistReducer(cartPersistConfig, cartReducer),
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

