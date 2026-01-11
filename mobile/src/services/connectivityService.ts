import NetInfo, { NetInfoState } from '@react-native-community/netinfo';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ConnectivityState } from '../types';

export { ConnectivityState };

type ConnectivityCallback = (state: ConnectivityState) => void;

const FORCE_OFFLINE_KEY = 'force_offline_mode';
const FORCE_OFFLINE_VERSION_KEY = 'force_offline_mode_version';
const CURRENT_VERSION = '1.0.1'; // Version de la fonctionnalité (incrémentée pour forcer la réinitialisation)

class ConnectivityService {
  private listeners: Map<string, ConnectivityCallback> = new Map();
  private currentState: ConnectivityState = {
    isOnline: false,
    isInternetReachable: false,
  };
  private forceOffline: boolean = false;
  private initialized: boolean = false;
  private initPromise: Promise<void> | null = null;

  constructor() {
    this.initPromise = this.initializeAsync();
    this.initialize();
  }

  private async initializeAsync(): Promise<void> {
    await this.loadForceOfflineMode();
    this.initialized = true;
  }

  async waitForInitialization(): Promise<void> {
    if (this.initPromise) {
      await this.initPromise;
    }
  }

  isInitialized(): boolean {
    return this.initialized;
  }

  private async loadForceOfflineMode(): Promise<void> {
    try {
      const [saved, savedVersion] = await Promise.all([
        AsyncStorage.getItem(FORCE_OFFLINE_KEY),
        AsyncStorage.getItem(FORCE_OFFLINE_VERSION_KEY)
      ]);
      
      // Si c'est une nouvelle version ou première utilisation, réinitialiser à EN LIGNE par défaut
      if (savedVersion !== CURRENT_VERSION) {
        this.forceOffline = false;
        await Promise.all([
          AsyncStorage.setItem(FORCE_OFFLINE_KEY, 'false'),
          AsyncStorage.setItem(FORCE_OFFLINE_VERSION_KEY, CURRENT_VERSION)
        ]);
        return;
      }
      
      // Par défaut, on est en ligne (forceOffline = false)
      // Seulement si explicitement sauvegardé comme 'true', on force le mode hors ligne
      this.forceOffline = saved === 'true';
      
      // Si rien n'est sauvegardé, s'assurer qu'on est en ligne
      if (saved === null) {
        this.forceOffline = false;
        await Promise.all([
          AsyncStorage.setItem(FORCE_OFFLINE_KEY, 'false'),
          AsyncStorage.setItem(FORCE_OFFLINE_VERSION_KEY, CURRENT_VERSION)
        ]);
      } else {
        // Si la valeur sauvegardée est 'true' mais qu'on veut forcer EN LIGNE par défaut
        // (pour cette version, on réinitialise toujours à EN LIGNE)
        if (saved === 'true') {
          this.forceOffline = false;
          await Promise.all([
            AsyncStorage.setItem(FORCE_OFFLINE_KEY, 'false'),
            AsyncStorage.setItem(FORCE_OFFLINE_VERSION_KEY, CURRENT_VERSION)
          ]);
        }
      }
    } catch (error) {
      console.error('[ConnectivityService] ❌ Erreur lors du chargement du mode hors ligne:', error);
      // En cas d'erreur, par défaut on est en ligne
      this.forceOffline = false;
    }
  }

  async setForceOfflineMode(enabled: boolean): Promise<void> {
    this.forceOffline = enabled;
    try {
      await Promise.all([
        AsyncStorage.setItem(FORCE_OFFLINE_KEY, enabled.toString()),
        AsyncStorage.setItem(FORCE_OFFLINE_VERSION_KEY, CURRENT_VERSION)
      ]);
      this.notifyListeners();
    } catch (error) {
      console.error('[ConnectivityService] ❌ Erreur lors de la sauvegarde du mode:', error);
    }
  }

  isForceOffline(): boolean {
    return this.forceOffline;
  }

  private initialize(): void {
    // Vérifier l'état initial
    NetInfo.fetch().then((state: NetInfoState) => {
      this.updateState(state);
    });

    // Écouter les changements de connectivité
    NetInfo.addEventListener((state: NetInfoState) => {
      this.updateState(state);
      this.notifyListeners();
    });
  }

  private updateState(state: NetInfoState): void {
    this.currentState = {
      isOnline: state.isConnected ?? false,
      isInternetReachable: state.isInternetReachable ?? false,
      type: state.type,
    };
  }

  private notifyListeners(): void {
    this.listeners.forEach((callback) => {
      callback(this.currentState);
    });
  }

  getIsOnline(): boolean {
    // Si le mode hors ligne est forcé, retourner false
    if (this.forceOffline) {
      return false;
    }
    return this.currentState.isOnline && this.currentState.isInternetReachable !== false;
  }

  // Vérifier la vraie connexion (ignorant le mode forcé)
  getRealConnectionStatus(): boolean {
    return this.currentState.isOnline && this.currentState.isInternetReachable !== false;
  }

  getState(): ConnectivityState {
    return { ...this.currentState };
  }

  on(event: 'connectivityChange', callback: ConnectivityCallback): string {
    const id = `listener_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.listeners.set(id, callback);
    
    // Notifier immédiatement avec l'état actuel
    callback(this.currentState);
    
    return id;
  }

  off(listenerId: string): void {
    this.listeners.delete(listenerId);
  }

  async checkConnectivity(): Promise<ConnectivityState> {
    const state = await NetInfo.fetch();
    this.updateState(state);
    return this.currentState;
  }
}

export const connectivityService = new ConnectivityService();

