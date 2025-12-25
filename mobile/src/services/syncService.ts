import AsyncStorage from '@react-native-async-storage/async-storage';
import { STORAGE_KEYS, SYNC_BATCH_SIZE } from '../utils/constants';
import { SyncQueueItem } from '../types';
import { connectivityService } from './connectivityService';
import apiClient from './api';
import { generateId, sleep, retryWithBackoff } from '../utils/helpers';

class SyncService {
  private isSyncing = false;
  private syncListeners: Map<string, (count: number) => void> = new Map();

  async addToQueue(
    action: 'CREATE' | 'UPDATE' | 'DELETE',
    endpoint: string,
    method: 'POST' | 'PUT' | 'PATCH' | 'DELETE',
    data: any
  ): Promise<string> {
    const queueItem: SyncQueueItem = {
      id: generateId(),
      action,
      endpoint,
      method,
      data,
      status: 'PENDING',
      retryCount: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    const queue = await this.getQueue();
    queue.push(queueItem);
    await this.saveQueue(queue);

    // Notifier les listeners
    this.notifyListeners(queue.length);

    // Si en ligne, synchroniser immédiatement
    if (connectivityService.getIsOnline()) {
      this.syncQueue();
    }

    return queueItem.id;
  }

  async getQueue(): Promise<SyncQueueItem[]> {
    try {
      const queueJson = await AsyncStorage.getItem(STORAGE_KEYS.SYNC_QUEUE);
      return queueJson ? JSON.parse(queueJson) : [];
    } catch (error) {
      console.error('Erreur lors de la récupération de la file:', error);
      return [];
    }
  }

  private async saveQueue(queue: SyncQueueItem[]): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.SYNC_QUEUE, JSON.stringify(queue));
    } catch (error) {
      console.error('Erreur lors de la sauvegarde de la file:', error);
    }
  }

  async getPendingCount(): Promise<number> {
    const queue = await this.getQueue();
    return queue.filter((item) => item.status === 'PENDING' || item.status === 'FAILED').length;
  }

  async syncQueue(): Promise<void> {
    if (this.isSyncing) return;
    if (!connectivityService.getIsOnline()) return;

    console.log(`[SyncService] 🔄 Starting sync for ${await this.getPendingCount()} items...`);
    this.isSyncing = true;

    try {
      const queue = await this.getQueue();
      const pendingItems = queue.filter(
        (item) => item.status === 'PENDING' || item.status === 'FAILED'
      );

      if (pendingItems.length === 0) {
        this.isSyncing = false;
        return;
      }

      // Traiter par batch
      const batches = [];
      for (let i = 0; i < pendingItems.length; i += SYNC_BATCH_SIZE) {
        batches.push(pendingItems.slice(i, i + SYNC_BATCH_SIZE));
      }

      for (const batch of batches) {
        await Promise.allSettled(
          batch.map((item) => this.syncItem(item))
        );
        
        // Petit délai entre les batches
        await sleep(100);
      }

      // Nettoyer les items réussis
      const updatedQueue = await this.getQueue();
      const cleanedQueue = updatedQueue.filter((item) => item.status !== 'SUCCESS');
      await this.saveQueue(cleanedQueue);

      this.notifyListeners(cleanedQueue.length);
    } catch (error) {
      console.error('Erreur lors de la synchronisation:', error);
    } finally {
      this.isSyncing = false;
    }
  }

  private async syncItem(item: SyncQueueItem): Promise<void> {
    const queue = await this.getQueue();
    const index = queue.findIndex((q) => q.id === item.id);
    
    if (index === -1) return;

    // Marquer comme en cours de synchronisation
    queue[index].status = 'SYNCING';
    queue[index].updatedAt = new Date().toISOString();
    await this.saveQueue(queue);

    try {
      await retryWithBackoff(async () => {
        let response;
        
        switch (item.method) {
          case 'POST':
            response = await apiClient.post(item.endpoint, item.data);
            break;
          case 'PUT':
            response = await apiClient.put(item.endpoint, item.data);
            break;
          case 'PATCH':
            response = await apiClient.patch(item.endpoint, item.data);
            break;
          case 'DELETE':
            response = await apiClient.delete(item.endpoint);
            break;
        }

        return response;
      });

      // Succès
      queue[index].status = 'SUCCESS';
      queue[index].updatedAt = new Date().toISOString();
    } catch (error) {
      // Échec
      queue[index].status = 'FAILED';
      queue[index].retryCount += 1;
      queue[index].updatedAt = new Date().toISOString();
    }

    await this.saveQueue(queue);
  }

  onQueueChange(callback: (count: number) => void): string {
    const id = `listener_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.syncListeners.set(id, callback);
    return id;
  }

  offQueueChange(listenerId: string): void {
    this.syncListeners.delete(listenerId);
  }

  private notifyListeners(count: number): void {
    this.syncListeners.forEach((callback) => {
      callback(count);
    });
  }

  async clearQueue(): Promise<void> {
    await AsyncStorage.removeItem(STORAGE_KEYS.SYNC_QUEUE);
    this.notifyListeners(0);
  }
}

export const syncService = new SyncService();

// Écouter les changements de connectivité pour synchroniser automatiquement
connectivityService.on('connectivityChange', (state) => {
  if (state.isOnline) {
    syncService.syncQueue();
  }
});

