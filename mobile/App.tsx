import 'react-native-get-random-values'; // DOIT être le premier import pour crypto-js
import * as Sentry from '@sentry/react-native';
import React, { useEffect, useState } from 'react';
import * as SplashScreen from 'expo-splash-screen';

// Initialiser Sentry le plus tôt possible
Sentry.init({
  // TODO: Remplacez par votre DSN Sentry (https://sentry.io → Projet → Settings → Client Keys)
  dsn: process.env.EXPO_PUBLIC_SENTRY_DSN || '',
  enabled: !__DEV__, // Désactivé en développement
  tracesSampleRate: 0.2, // 20% des transactions pour le monitoring de performance
  attachScreenshot: true, // Capture d'écran lors des crashes
  enableAutoSessionTracking: true, // Suivi automatique des sessions
  sessionTrackingIntervalMillis: 30000, // Intervalle de suivi des sessions
  environment: __DEV__ ? 'development' : 'production',
});

// Garder le splash screen natif visible jusqu'à ce que l'app soit prête
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

function App() {
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

  if (!isReady) {
    return <LoadingScreen />;
  }

  return (
    <SafeAreaProvider>
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

export default Sentry.wrap(App);

