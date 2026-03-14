import 'react-native-get-random-values'; // DOIT être le premier import pour crypto-js
import React, { useEffect, useState, useCallback } from 'react';
import * as SplashScreen from 'expo-splash-screen';

// Masquer immédiatement le splash screen natif pour utiliser notre composant personnalisé avec logo réduit
SplashScreen.hideAsync().catch(() => {
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
  const [persistBootstrapped, setPersistBootstrapped] = useState(
    () => persistor.getState().bootstrapped
  );

  useEffect(() => {
    // Écouter la réhydratation Redux
    const unsubscribe = persistor.subscribe(() => {
      if (persistor.getState().bootstrapped) {
        setPersistBootstrapped(true);
        unsubscribe();
      }
    });
    return unsubscribe;
  }, []);

  useEffect(() => {
    async function prepare() {
      try {
        setSessionExpiredCallback(() => {
          store.dispatch(setSessionExpired(true));
        });
      } catch (e) {
        console.warn(e);
      } finally {
        setAppIsReady(true);
      }
    }
    prepare();
  }, []);

  const isReady = appIsReady && persistBootstrapped;

  const onLayoutRootView = useCallback(async () => {
    if (isReady) {
      await SplashScreen.hideAsync();
    }
  }, [isReady]);

  if (!isReady) {
    return <LoadingScreen />;
  }

  return (
    <SafeAreaProvider onLayout={onLayoutRootView}>
      <ErrorBoundary>
        <Provider store={store}>
          <PersistGate loading={null} persistor={persistor}>
            <AppNavigator />
            <StatusBar style="dark" />
          </PersistGate>
        </Provider>
      </ErrorBoundary>
    </SafeAreaProvider>
  );
}

