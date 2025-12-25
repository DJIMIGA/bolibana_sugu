import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import { STORAGE_KEYS, REDUX_PERSIST_SECRET_KEY } from './constants';

/**
 * Utilitaire de debug pour vérifier le fonctionnement du mode hors ligne et du chiffrement.
 */
export const debugOfflineStorage = async () => {
  console.log('\n--- 🛠️ DEBUG OFFLINE STORAGE ---');

  // 1. Vérification d'AsyncStorage (Redux Persist)
  try {
    const allKeys = await AsyncStorage.getAllKeys();
    console.log('Keys in AsyncStorage:', allKeys);

    const persistRoot = await AsyncStorage.getItem('persist:root');
    if (persistRoot) {
      console.log('✅ persist:root found.');
      // Vérifier si c'est chiffré (ne devrait pas être du JSON lisible si chiffré par le transform)
      try {
        JSON.parse(persistRoot);
        console.warn('⚠️ persist:root is in CLEAR TEXT (JSON parseable). Check encryption config!');
      } catch (e) {
        console.log('🔒 persist:root seems encrypted (Not JSON parseable).');
      }
    } else {
      console.warn('❌ persist:root not found. Redux persist might not have run yet.');
    }
  } catch (error) {
    console.error('Error reading AsyncStorage:', error);
  }

  // 2. Vérification de SecureStore (Tokens)
  try {
    const token = await SecureStore.getItemAsync(STORAGE_KEYS.AUTH_TOKEN);
    console.log(`🔑 Auth Token in SecureStore: ${token ? 'PRESENT (Encrypted by System)' : 'ABSENT'}`);
    
    const refreshToken = await SecureStore.getItemAsync(STORAGE_KEYS.AUTH_REFRESH_TOKEN);
    console.log(`🔑 Refresh Token in SecureStore: ${refreshToken ? 'PRESENT (Encrypted by System)' : 'ABSENT'}`);
  } catch (error) {
    console.error('Error reading SecureStore:', error);
  }

  // 3. Vérification de la clé secrète
  console.log(`🔐 Redux Persist Secret Key configured: ${REDUX_PERSIST_SECRET_KEY !== 'sagakore-offline-secret-key-change-me' ? 'YES (Custom)' : 'NO (Default)'}`);

  console.log('--- END DEBUG ---\n');
};

