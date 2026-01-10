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
    console.log('[ConnectivityService] 🚀 Initialisation du service de connectivité...');
    this.initPromise = this.initializeAsync();
    this.initialize();
  }

  private async initializeAsync(): Promise<void> {
    await this.loadForceOfflineMode();
    this.initialized = true;
    console.log('[ConnectivityService] ✅ Service initialisé');
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
      
      console.log('[ConnectivityService] 📱 Chargement du mode hors ligne:', saved, 'version:', savedVersion);
      
      // Si c'est une nouvelle version ou première utilisation, réinitialiser à EN LIGNE par défaut
      if (savedVersion !== CURRENT_VERSION) {
        console.log('[ConnectivityService] 🔄 Nouvelle version détectée, réinitialisation à EN LIGNE par défaut');
        this.forceOffline = false;
        await Promise.all([
          AsyncStorage.setItem(FORCE_OFFLINE_KEY, 'false'),
          AsyncStorage.setItem(FORCE_OFFLINE_VERSION_KEY, CURRENT_VERSION)
        ]);
        console.log('[ConnectivityService] ✅ Mode EN LIGNE par défaut (nouvelle version)');
        return;
      }
      
      // Par défaut, on est en ligne (forceOffline = false)
      // Seulement si explicitement sauvegardé comme 'true', on force le mode hors ligne
      this.forceOffline = saved === 'true';
      
      // Si rien n'est sauvegardé, s'assurer qu'on est en ligne
      if (saved === null) {
        console.log('[ConnectivityService] ✅ Aucune préférence trouvée, mode EN LIGNE par défaut');
        this.forceOffline = false;
        await Promise.all([
          AsyncStorage.setItem(FORCE_OFFLINE_KEY, 'false'),
          AsyncStorage.setItem(FORCE_OFFLINE_VERSION_KEY, CURRENT_VERSION)
        ]);
      } else {
        // Si la valeur sauvegardée est 'true' mais qu'on veut forcer EN LIGNE par défaut
        // (pour cette version, on réinitialise toujours à EN LIGNE)
        if (saved === 'true') {
          console.log('[ConnectivityService] 🔄 Réinitialisation de HORS LIGNE vers EN LIGNE (nouvelle logique)');
          this.forceOffline = false;
          await Promise.all([
            AsyncStorage.setItem(FORCE_OFFLINE_KEY, 'false'),
            AsyncStorage.setItem(FORCE_OFFLINE_VERSION_KEY, CURRENT_VERSION)
          ]);
          console.log('[ConnectivityService] ✅ Mode EN LIGNE par défaut restauré');
        } else {
          console.log(`[ConnectivityService] ${this.forceOffline ? '🔴 Mode HORS LIGNE' : '🟢 Mode EN LIGNE'} (sauvegardé: ${saved})`);
        }
      }
    } catch (error) {
      console.error('[ConnectivityService] ❌ Erreur lors du chargement du mode hors ligne:', error);
      // En cas d'erreur, par défaut on est en ligne
      this.forceOffline = false;
    }
  }

  async setForceOfflineMode(enabled: boolean): Promise<void> {
    console.log(`[ConnectivityService] 🔄 Changement de mode: ${enabled ? 'HORS LIGNE' : 'EN LIGNE'}`);
    this.forceOffline = enabled;
    try {
      await Promise.all([
        AsyncStorage.setItem(FORCE_OFFLINE_KEY, enabled.toString()),
        AsyncStorage.setItem(FORCE_OFFLINE_VERSION_KEY, CURRENT_VERSION)
      ]);
      console.log(`[ConnectivityService] 💾 Mode sauvegardé: ${enabled} (version: ${CURRENT_VERSION})`);
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

