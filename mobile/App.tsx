import 'react-native-get-random-values'; // DOIT être le premier import pour crypto-js
import React, { useEffect, useState, useCallback } from 'react';
import * as SplashScreen from 'expo-splash-screen';

// Garder le splash screen visible pendant que l'app charge
SplashScreen.preventAutoHideAsync().catch(() => {
  /* ignore error */
});

import { StatusBar } from 'expo-status-bar';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { store, persistor } from './src/store/store';
import AppNavigator from './src/navigation/AppNavigator';
import { ErrorBoundary } from './src/components/ErrorBoundary';
import { LoadingScreen } from './src/components/LoadingScreen';
import { setSessionExpiredCallback } from './src/services/api';
import { setSessionExpired } from './src/store/slices/authSlice';

export default function App() {
  const [appIsReady, setAppIsReady] = useState(false);

  useEffect(() => {
    async function prepare() {
      try {
        // Configurer le callback de session expirée
        setSessionExpiredCallback(() => {
          store.dispatch(setSessionExpired(true));
        });
        
        // Simuler un petit délai pour laisser les polices/assets se charger si nécessaire
        await new Promise(resolve => setTimeout(resolve, 500));
      } catch (e) {
        console.warn(e);
      } finally {
        setAppIsReady(true);
      }
    }

    prepare();
  }, []);

  const onLayoutRootView = useCallback(async () => {
    if (appIsReady) {
      // Masquer le splash screen natif une fois que le RootView est prêt
      await SplashScreen.hideAsync();
    }
  }, [appIsReady]);

  if (!appIsReady) {
    return null;
  }

  return (
    <SafeAreaProvider onLayout={onLayoutRootView}>
      <ErrorBoundary>
        <Provider store={store}>
          <PersistGate loading={<LoadingScreen />} persistor={persistor}>
            <AppNavigator />
            <StatusBar style="dark" />
          </PersistGate>
        </Provider>
      </ErrorBoundary>
    </SafeAreaProvider>
  );
}

