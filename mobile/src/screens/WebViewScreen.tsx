import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { WebView } from 'react-native-webview';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { COLORS, API_ENDPOINTS } from '../utils/constants';
import apiClient from '../services/api';

interface WebViewScreenParams {
  slug?: string;
  title: string;
  url?: string;
}

const WebViewScreen: React.FC = () => {
  const route = useRoute();
  const navigation = useNavigation();
  const insets = useSafeAreaInsets();
  const { slug, title, url } = (route.params as WebViewScreenParams) || { title: '' };

  const [htmlContent, setHtmlContent] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (slug) {
      fetchStaticPage(slug);
    } else {
      setIsLoading(false);
    }
  }, [slug]);

  const fetchStaticPage = async (pageSlug: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiClient.get(API_ENDPOINTS.STATIC_PAGES(pageSlug));
      const { content } = response.data;
      if (content) {
        setHtmlContent(wrapHtml(content));
      } else {
        setError('Contenu non disponible');
      }
    } catch (err: any) {
      console.error('[WebViewScreen] Erreur chargement page:', err);
      if (err.response?.status === 404) {
        setError('Page non trouvée');
      } else {
        setError('Impossible de charger la page. Vérifiez votre connexion.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const wrapHtml = (content: string): string => {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; }
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 16px;
            line-height: 1.6;
            color: ${COLORS.TEXT};
            padding: 16px;
            background-color: #FFFFFF;
          }
          h1 { font-size: 22px; font-weight: 700; margin-bottom: 16px; color: ${COLORS.TEXT}; }
          h2 { font-size: 19px; font-weight: 600; margin-top: 24px; margin-bottom: 12px; color: ${COLORS.TEXT}; }
          h3 { font-size: 17px; font-weight: 600; margin-top: 20px; margin-bottom: 8px; color: ${COLORS.TEXT}; }
          p { margin-bottom: 12px; color: ${COLORS.TEXT}; }
          ul, ol { margin-bottom: 12px; padding-left: 24px; }
          li { margin-bottom: 6px; }
          a { color: ${COLORS.PRIMARY}; text-decoration: none; }
          img { max-width: 100%; height: auto; border-radius: 8px; margin: 8px 0; }
          table { width: 100%; border-collapse: collapse; margin: 12px 0; }
          th, td { border: 1px solid #E5E7EB; padding: 8px 12px; text-align: left; }
          th { background-color: #F9FAFB; font-weight: 600; }
          blockquote {
            border-left: 3px solid ${COLORS.PRIMARY};
            padding-left: 12px;
            margin: 12px 0;
            color: ${COLORS.TEXT_SECONDARY};
          }
          strong { font-weight: 600; }
        </style>
      </head>
      <body>${content}</body>
      </html>
    `;
  };

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Ionicons name="arrow-back" size={24} color={COLORS.TEXT} />
        </TouchableOpacity>
        <Text style={styles.headerTitle} numberOfLines={1}>{title}</Text>
        <View style={styles.placeholder} />
      </View>

      {isLoading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={COLORS.PRIMARY} />
          <Text style={styles.loadingText}>Chargement...</Text>
        </View>
      )}

      {error && (
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle-outline" size={48} color={COLORS.TEXT_SECONDARY} />
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity
            style={styles.retryButton}
            onPress={() => slug && fetchStaticPage(slug)}
          >
            <Text style={styles.retryButtonText}>Réessayer</Text>
          </TouchableOpacity>
        </View>
      )}

      {!isLoading && !error && htmlContent && (
        <WebView
          source={{ html: htmlContent }}
          style={styles.webView}
          originWhitelist={['*']}
          scrollEnabled={true}
          showsVerticalScrollIndicator={false}
          javaScriptEnabled={false}
        />
      )}

      {!isLoading && !error && url && !slug && (
        <WebView
          source={{ uri: url }}
          style={styles.webView}
          startInLoadingState={true}
          renderLoading={() => (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color={COLORS.PRIMARY} />
            </View>
          )}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
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
  webView: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 15,
    color: COLORS.TEXT_SECONDARY,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  errorText: {
    marginTop: 12,
    fontSize: 16,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
  },
  retryButton: {
    marginTop: 20,
    backgroundColor: COLORS.PRIMARY,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '600',
  },
});

export default WebViewScreen;
