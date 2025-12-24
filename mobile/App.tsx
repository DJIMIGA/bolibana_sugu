import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { Provider } from 'react-redux';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { store } from './src/store/store';
import AppNavigator from './src/navigation/AppNavigator';
import { ErrorBoundary } from './src/components/ErrorBoundary';
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
          <AppNavigator />
          <StatusBar style="auto" />
        </Provider>
      </ErrorBoundary>
    </SafeAreaProvider>
  );
}

