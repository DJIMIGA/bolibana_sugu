import { useState, useEffect, useCallback } from 'react';
import { connectivityService } from '../services/connectivityService';
import { ConnectivityState as ConnectivityStateType } from '../types';

export const useConnectivity = (): ConnectivityStateType & { isOnline: boolean } => {
  const [state, setState] = useState<ConnectivityStateType>(connectivityService.getState());
  const [isOnline, setIsOnline] = useState<boolean>(connectivityService.getIsOnline());

  const updateState = useCallback(() => {
    setState(connectivityService.getState());
    setIsOnline(connectivityService.getIsOnline());
  }, []);

  useEffect(() => {
    const listenerId = connectivityService.on('connectivityChange', (newState) => {
      updateState();
    });

    // Vérifier périodiquement l'état (pour détecter les changements de mode forcé)
    const interval = setInterval(() => {
      updateState();
    }, 300);

    return () => {
      connectivityService.off(listenerId);
      clearInterval(interval);
    };
  }, [updateState]);

  return {
    ...state,
    isOnline, // Utiliser getIsOnline() qui prend en compte le mode forcé
  };
};
