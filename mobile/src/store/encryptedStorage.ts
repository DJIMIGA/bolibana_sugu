import AsyncStorage from '@react-native-async-storage/async-storage';
import 'react-native-get-random-values'; // Polyfill nécessaire pour crypto-js dans React Native
import CryptoJS from 'crypto-js';
import * as SecureStore from 'expo-secure-store';

// Clé SecureStore où la clé de chiffrement est stockée (hardware-backed sur iOS/Android)
const ENC_KEY_STORE = 'bb_redux_enc_key';
let _cachedKey: string | null = null;

/**
 * Récupère (ou génère) la clé de chiffrement unique par installation.
 * Stockée dans expo-secure-store (Keychain iOS / Keystore Android).
 */
async function getEncryptionKey(): Promise<string> {
  if (_cachedKey) return _cachedKey;

  let key = await SecureStore.getItemAsync(ENC_KEY_STORE);
  if (!key) {
    // Générer une clé aléatoire 256 bits à la première installation
    const bytes = new Uint8Array(32);
    global.crypto.getRandomValues(bytes);
    key = Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
    await SecureStore.setItemAsync(ENC_KEY_STORE, key);
  }

  _cachedKey = key;
  return key;
}

/**
 * Chiffre une valeur et la stocke dans AsyncStorage.
 * Utilise la même clé dérivée de l'appareil que le Redux Persist.
 */
export const encryptAndStore = async (key: string, value: string): Promise<void> => {
  const encKey = await getEncryptionKey();
  const encrypted = CryptoJS.AES.encrypt(value, encKey).toString();
  await AsyncStorage.setItem(key, encrypted);
};

/**
 * Lit et déchiffre une valeur depuis AsyncStorage.
 */
export const decryptAndGet = async (key: string): Promise<string | null> => {
  const raw = await AsyncStorage.getItem(key);
  if (!raw) return null;
  try {
    const encKey = await getEncryptionKey();
    const decrypted = CryptoJS.AES.decrypt(raw, encKey).toString(CryptoJS.enc.Utf8);
    return decrypted || null;
  } catch {
    return null;
  }
};

/**
 * Storage personnalisé qui chiffre/déchiffre automatiquement toutes les données
 * avant de les stocker dans AsyncStorage, avec une clé dérivée de l'appareil.
 */
export const createEncryptedStorage = () => {
  return {
    getItem: async (key: string): Promise<string | null> => {
      try {
        const encrypted = await AsyncStorage.getItem(key);
        if (!encrypted) return null;

        try {
          const encKey = await getEncryptionKey();
          const decrypted = CryptoJS.AES.decrypt(encrypted, encKey).toString(CryptoJS.enc.Utf8);
          if (!decrypted) {
            if (__DEV__) console.warn(`⚠️ Failed to decrypt ${key}, trying as plain text`);
            return encrypted;
          }
          return decrypted;
        } catch (error) {
          if (__DEV__) console.warn(`⚠️ Decryption error for ${key}, returning as-is:`, error);
          return encrypted;
        }
      } catch (error) {
        if (__DEV__) console.error(`Error getting item ${key}:`, error);
        return null;
      }
    },

    setItem: async (key: string, value: string): Promise<void> => {
      try {
        const encKey = await getEncryptionKey();
        const encrypted = CryptoJS.AES.encrypt(value, encKey).toString();
        await AsyncStorage.setItem(key, encrypted);
      } catch (error) {
        if (__DEV__) console.error(`❌ Error setting item ${key}:`, error);
        throw error;
      }
    },

    removeItem: async (key: string): Promise<void> => {
      try {
        await AsyncStorage.removeItem(key);
      } catch (error) {
        if (__DEV__) console.error(`Error removing item ${key}:`, error);
        throw error;
      }
    },
  };
};

