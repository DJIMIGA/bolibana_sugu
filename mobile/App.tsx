import React, { useEffect } from 'react';
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
  useEffect(() => {
    // Configurer le callback de session expirée
    setSessionExpiredCallback(() => {
      store.dispatch(setSessionExpired(true));
    });
  }, []);

  return (
    <SafeAreaProvider>
      <ErrorBoundary>
        <Provider store={store}>
          <PersistGate loading={<LoadingScreen />} persistor={persistor}>
            <AppNavigator />
            <StatusBar style="auto" />
          </PersistGate>
        </Provider>
      </ErrorBoundary>
    </SafeAreaProvider>
  );
}

