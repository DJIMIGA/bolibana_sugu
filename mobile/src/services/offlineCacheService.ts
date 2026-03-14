import AsyncStorage from '@react-native-async-storage/async-storage';
import { CACHE_KEYS, CACHE_TTL } from '../utils/constants';
import { CacheItem } from '../types';
import { isExpired } from '../utils/helpers';

const CACHE_VERSION = '1.0.0';

class OfflineCacheService {
  private async getItem<T>(key: string): Promise<CacheItem<T> | null> {
    try {
      const cached = await AsyncStorage.getItem(key);
      if (!cached) return null;

      const item: CacheItem<T> = JSON.parse(cached);
      
      // Vérifier l'expiration
      if (isExpired(item.timestamp, CACHE_TTL)) {
        await AsyncStorage.removeItem(key);
        return null;
      }

      // Vérifier la version
      if (item.version !== CACHE_VERSION) {
        await AsyncStorage.removeItem(key);
        return null;
      }

      return item;
    } catch (error) {
      console.error(`Erreur lors de la récupération du cache ${key}:`, error);
      return null;
    }
  }

  private async setItem<T>(key: string, data: T): Promise<void> {
    try {
      const item: CacheItem<T> = {
        data,
        timestamp: Date.now(),
        version: CACHE_VERSION,
      };
      await AsyncStorage.setItem(key, JSON.stringify(item));
    } catch (error) {
      console.error(`Erreur lors de la sauvegarde du cache ${key}:`, error);
    }
  }

  async get<T>(key: string): Promise<T | null> {
    const item = await this.getItem<T>(key);
    return item ? item.data : null;
  }

  async set<T>(key: string, data: T): Promise<void> {
    await this.setItem(key, data);
  }

  async remove(key: string): Promise<void> {
    try {
      await AsyncStorage.removeItem(key);
    } catch (error) {
      console.error(`Erreur lors de la suppression du cache ${key}:`, error);
    }
  }

  async clear(): Promise<void> {
    try {
      const keys = Object.values(CACHE_KEYS);
      await AsyncStorage.multiRemove(keys);
    } catch (error) {
      console.error('Erreur lors du nettoyage du cache:', error);
    }
  }

  async preloadEssentialData(services: {
    productService?: { fetchProducts: () => Promise<any> };
    categoryService?: { fetchCategories: () => Promise<any> };
    customerService?: { fetchProfile: () => Promise<any> };
    cartService?: { fetchCart: () => Promise<any> };
  }): Promise<void> {
    try {
      const promises: Promise<any>[] = [];

      if (services.productService) {
        promises.push(
          services.productService.fetchProducts().then((data) => {
            return this.set(CACHE_KEYS.PRODUCTS, data);
          })
        );
      }

      if (services.categoryService) {
        promises.push(
          services.categoryService.fetchCategories().then((data) => {
            return this.set(CACHE_KEYS.CATEGORIES, data);
          })
        );
      }

      if (services.customerService) {
        promises.push(
          services.customerService.fetchProfile().then((data) => {
            return this.set(CACHE_KEYS.USER_PROFILE, data);
          })
        );
      }

      if (services.cartService) {
        promises.push(
          services.cartService.fetchCart().then((data) => {
            return this.set(CACHE_KEYS.CART, data);
          })
        );
      }

      await Promise.allSettled(promises);
    } catch (error) {
      console.error('Erreur lors du préchargement des données:', error);
    }
  }

  async invalidate(key: string): Promise<void> {
    await this.remove(key);
  }

  async invalidateAll(): Promise<void> {
    await this.clear();
  }
}

export const offlineCacheService = new OfflineCacheService();

