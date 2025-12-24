import { useState, useEffect } from 'react';
import { connectivityService } from '../services/connectivityService';
import { ConnectivityState as ConnectivityStateType } from '../types';

export const useConnectivity = (): ConnectivityStateType => {
  const [state, setState] = useState<ConnectivityStateType>(connectivityService.getState());

  useEffect(() => {
    const listenerId = connectivityService.on('connectivityChange', (newState) => {
      setState(newState);
    });

    return () => {
      connectivityService.off(listenerId);
    };
  }, []);

  return state;
};
