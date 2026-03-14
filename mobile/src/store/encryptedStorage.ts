import AsyncStorage from '@react-native-async-storage/async-storage';
import 'react-native-get-random-values'; // Polyfill nécessaire pour crypto-js dans React Native
import CryptoJS from 'crypto-js';
import { REDUX_PERSIST_SECRET_KEY } from '../utils/constants';

/**
 * Storage personnalisé qui chiffre/déchiffre automatiquement toutes les données
 * avant de les stocker dans AsyncStorage.
 */
export const createEncryptedStorage = () => {
  return {
    getItem: async (key: string): Promise<string | null> => {
      try {
        const encrypted = await AsyncStorage.getItem(key);
        if (!encrypted) return null;
        
        // Essayer de déchiffrer
        try {
          const decrypted = CryptoJS.AES.decrypt(encrypted, REDUX_PERSIST_SECRET_KEY).toString(CryptoJS.enc.Utf8);
          if (!decrypted) {
            // Si le déchiffrement échoue, peut-être que c'est déjà en clair (migration)
            console.warn(`⚠️ Failed to decrypt ${key}, trying as plain text`);
            return encrypted;
          }
          return decrypted;
        } catch (error) {
          // Si ce n'est pas chiffré, retourner tel quel (pour migration)
          console.warn(`⚠️ Decryption error for ${key}, returning as-is:`, error);
          return encrypted;
        }
      } catch (error) {
        console.error(`Error getting item ${key}:`, error);
        return null;
      }
    },
    
    setItem: async (key: string, value: string): Promise<void> => {
      try {
        // Chiffrer avant de stocker
        const encrypted = CryptoJS.AES.encrypt(value, REDUX_PERSIST_SECRET_KEY).toString();
        await AsyncStorage.setItem(key, encrypted);
        // Logs de chiffrement désactivés pour réduire le bruit
      } catch (error) {
        console.error(`❌ Error setting item ${key}:`, error);
        throw error;
      }
    },
    
    removeItem: async (key: string): Promise<void> => {
      try {
        await AsyncStorage.removeItem(key);
      } catch (error) {
        console.error(`Error removing item ${key}:`, error);
        throw error;
      }
    },
  };
};

