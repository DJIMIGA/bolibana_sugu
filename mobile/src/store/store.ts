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
import AsyncStorage from '@react-native-async-storage/async-storage';
import createEncryptor from 'redux-persist-transform-encrypt';
import authReducer from './slices/authSlice';
import productReducer from './slices/productSlice';
import cartReducer from './slices/cartSlice';
import { REDUX_PERSIST_SECRET_KEY } from '../utils/constants';

// Configuration du chiffrement
const encryptor = createEncryptor({
  secretKey: REDUX_PERSIST_SECRET_KEY,
  onError: function (error) {
    console.error('Erreur de chiffrement de la persistance Redux:', error);
  },
});

// Combinaison des reducers
const rootReducer = combineReducers({
  auth: authReducer,
  product: productReducer,
  cart: cartReducer,
});

// Configuration de la persistance
const persistConfig = {
  key: 'root',
  storage: AsyncStorage,
  transforms: [encryptor],
  // Ne pas persister les états de chargement ou d'erreur
  blacklist: ['isLoading', 'error'], 
  // On pourrait aussi utiliser whitelist pour ne persister que certains slices
  // whitelist: ['auth', 'product', 'cart'],
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

