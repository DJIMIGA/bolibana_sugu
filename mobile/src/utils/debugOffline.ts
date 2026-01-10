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

    // Vérifier persist:root (maintenant chiffré au niveau storage)
    const persistRootRaw = await AsyncStorage.getItem('persist:root');
    if (persistRootRaw) {
      console.log('✅ persist:root found in AsyncStorage.');
      
      // Vérifier si c'est chiffré (ne devrait pas être du JSON lisible directement)
      try {
        // Si on peut parser directement, c'est en clair
        const parsed = JSON.parse(persistRootRaw);
        console.warn('⚠️ persist:root is stored in CLEAR TEXT in AsyncStorage!');
        console.warn('   This means the encrypted storage is not working properly.');
      } catch (e) {
        // Si on ne peut pas parser, c'est probablement chiffré
        console.log('🔒 persist:root is ENCRYPTED in AsyncStorage ✅');
        console.log(`   Encrypted data length: ${persistRootRaw.length} characters`);
        console.log(`   First 50 chars (encrypted): ${persistRootRaw.substring(0, 50)}...`);
        
        // Essayer de déchiffrer pour vérifier
        try {
          const CryptoJS = require('crypto-js');
          const { REDUX_PERSIST_SECRET_KEY } = require('./constants');
          const decrypted = CryptoJS.AES.decrypt(persistRootRaw, REDUX_PERSIST_SECRET_KEY).toString(CryptoJS.enc.Utf8);
          if (decrypted) {
            const rootData = JSON.parse(decrypted);
            console.log('✅ Decryption successful! Structure:', Object.keys(rootData));
            console.log('🎉 ENCRYPTION STATUS: ALL DATA IS PROPERLY ENCRYPTED ✅');
          } else {
            console.warn('⚠️ Decryption returned empty string');
          }
        } catch (decryptError) {
          console.warn('⚠️ Could not decrypt (might be using different key or format):', decryptError);
        }
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
  const isKeyConfigured = REDUX_PERSIST_SECRET_KEY !== 'sagakore-offline-secret-key-change-me' && 
                          REDUX_PERSIST_SECRET_KEY.includes('sagakore');
  console.log(`🔐 Redux Persist Secret Key configured: ${isKeyConfigured ? 'YES' : 'NO (Default)'}`);

  console.log('--- END DEBUG ---\n');
};

/**
 * Nettoie le cache Redux Persist existant pour forcer le re-chiffrement.
 * À utiliser si des données en clair ont été détectées.
 */
export const clearPersistCache = async () => {
  console.log('\n--- 🧹 CLEARING PERSIST CACHE ---');
  try {
    // Récupérer toutes les clés pour trouver toutes les clés persist
    const allKeys = await AsyncStorage.getAllKeys();
    const persistKeys = allKeys.filter(key => key.startsWith('persist:'));
    
    if (persistKeys.length > 0) {
      await AsyncStorage.multiRemove(persistKeys);
      console.log(`✅ ${persistKeys.length} clé(s) Redux Persist supprimée(s):`, persistKeys);
    } else {
      console.log('ℹ️ Aucune clé persist trouvée.');
    }
    
    console.log('✅ Cache Redux Persist nettoyé. Les données seront re-chiffrées au prochain démarrage.');
    console.log('--- END CLEAR ---\n');
  } catch (error) {
    console.error('❌ Erreur lors du nettoyage du cache:', error);
  }
};