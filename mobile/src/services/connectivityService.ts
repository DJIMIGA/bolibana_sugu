import NetInfo, { NetInfoState } from '@react-native-community/netinfo';
import { ConnectivityState } from '../types';

export { ConnectivityState };

type ConnectivityCallback = (state: ConnectivityState) => void;

class ConnectivityService {
  private listeners: Map<string, ConnectivityCallback> = new Map();
  private currentState: ConnectivityState = {
    isOnline: false,
    isInternetReachable: false,
  };

  constructor() {
    this.initialize();
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

