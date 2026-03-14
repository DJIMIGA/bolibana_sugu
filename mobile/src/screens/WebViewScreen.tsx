import React, { useEffect } from 'react';
import { View, StyleSheet, ActivityIndicator, Text, TouchableOpacity } from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import * as WebBrowser from 'expo-web-browser';
import { COLORS } from '../utils/constants';
import LoadingSpinner from '../components/LoadingSpinner';

interface WebViewScreenParams {
  url: string;
  title: string;
}

const ALLOWED_DOMAINS = ['bolibana.com', 'www.bolibana.com'];

const isTrustedUrl = (rawUrl: string): boolean => {
  if (!rawUrl) return false;
  try {
    const parsed = new URL(rawUrl);
    return parsed.protocol === 'https:' && ALLOWED_DOMAINS.includes(parsed.hostname);
  } catch {
    return false;
  }
};

const WebViewScreen: React.FC = () => {
  const route = useRoute();
  const navigation = useNavigation();
  const { url, title } = (route.params as WebViewScreenParams) || { url: '', title: '' };

  useEffect(() => {
    if (url && isTrustedUrl(url)) {
      WebBrowser.openBrowserAsync(url, {
        presentationStyle: WebBrowser.WebBrowserPresentationStyle.FULL_SCREEN,
        controlsColor: COLORS.PRIMARY,
      });
    } else if (url) {
      if (__DEV__) console.warn('[WebViewScreen] URL refusée (domaine non autorisé):', url);
    }
  }, [url]);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Ionicons name="arrow-back" size={24} color={COLORS.TEXT} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{title}</Text>
        <View style={styles.placeholder} />
      </View>
      <View style={styles.content}>
        <LoadingSpinner />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.BACKGROUND,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.TEXT,
    flex: 1,
    textAlign: 'center',
  },
  placeholder: {
    width: 40,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
  },
});

export default WebViewScreen;

