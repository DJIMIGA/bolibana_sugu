import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, Platform, Modal, TouchableOpacity, Linking } from 'react-native';
import { NavigationContainer, useNavigationContainerRef } from '@react-navigation/native';
import * as WebBrowser from 'expo-web-browser';
import * as SplashScreen from 'expo-splash-screen';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { loadUserAsync } from '../store/slices/authSlice';
import { fetchFavorites } from '../store/slices/favoritesSlice';
import { LoadingScreen } from '../components/LoadingScreen';
import { COLORS } from '../utils/constants';
import Logo from '../components/Logo';

// Screens
import LoginScreen from '../screens/LoginScreen';
import SignupScreen from '../screens/SignupScreen';
import HomeScreen from '../screens/HomeScreen';
import ProductListScreen from '../screens/ProductListScreen';
import ProductDetailScreen from '../screens/ProductDetailScreen';
import CartScreen from '../screens/CartScreen';
import CheckoutScreen from '../screens/CheckoutScreen';
import ProfileScreen from '../screens/ProfileScreen';
import CategoryScreen from '../screens/CategoryScreen';
import SubCategoryScreen from '../screens/SubCategoryScreen';
import WebViewScreen from '../screens/WebViewScreen';
import PaymentWebViewScreen from '../screens/PaymentWebViewScreen';
import PriceCheckScreen from '../screens/PriceCheckScreen';
import AddressesScreen from '../screens/AddressesScreen';
import AddAddressScreen from '../screens/AddAddressScreen';
import OrdersScreen from '../screens/OrdersScreen';
import OrderDetailScreen from '../screens/OrderDetailScreen';
import SettingsScreen from '../screens/SettingsScreen';
import LoyaltyScreen from '../screens/LoyaltyScreen';
import FavoritesScreen from '../screens/FavoritesScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Stack pour l'authentification
const AuthStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="Login" component={LoginScreen} />
  </Stack.Navigator>
);

// Stack pour les catégories
const CategoryStack = () => (
  <Stack.Navigator>
    <Stack.Screen 
      name="CategoryMain" 
      component={CategoryScreen}
      options={{ headerShown: false }}
    />
    <Stack.Screen 
      name="SubCategory" 
      component={SubCategoryScreen}
      options={{ headerShown: false }}
    />
  </Stack.Navigator>
);

// Stack pour les produits
const ProductStack = () => (
  <Stack.Navigator>
    <Stack.Screen 
      name="ProductList" 
      component={ProductListScreen}
      options={{ headerShown: false }}
    />
    <Stack.Screen 
      name="ProductDetail" 
      component={ProductDetailScreen}
      options={{ headerShown: false }}
    />
  </Stack.Navigator>
);

// Stack pour le panier
const CartStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="CartMain" component={CartScreen} />
    <Stack.Screen name="Checkout" component={CheckoutScreen} />
    <Stack.Screen name="PaymentWebView" component={PaymentWebViewScreen} />
  </Stack.Navigator>
);

// Stack pour le profil (inclut Login, Signup, WebView, Addresses, Orders, Settings)
const ProfileStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="ProfileMain" component={ProfileScreen} />
    <Stack.Screen name="Login" component={LoginScreen} />
    <Stack.Screen name="Signup" component={SignupScreen} />
    <Stack.Screen name="WebView" component={WebViewScreen} />
    <Stack.Screen name="Addresses" component={AddressesScreen} />
    <Stack.Screen name="AddAddress" component={AddAddressScreen} />
    <Stack.Screen name="Orders" component={OrdersScreen} />
    <Stack.Screen name="OrderDetail" component={OrderDetailScreen} />
    <Stack.Screen name="Settings" component={SettingsScreen} />
    <Stack.Screen name="Loyalty" component={LoyaltyScreen} />
    <Stack.Screen name="Favorites" component={FavoritesScreen} />
  </Stack.Navigator>
);

// Composant pour les icônes avec badge
const TabBarIcon: React.FC<{ 
  name: keyof typeof Ionicons.glyphMap; 
  color: string; 
  focused: boolean;
  badge?: number;
}> = ({ name, color, focused, badge }) => {
  return (
    <View style={styles.iconContainer}>
      <Ionicons
        name={focused ? name : (`${name}-outline` as keyof typeof Ionicons.glyphMap)}
        size={22}
        color={color}
      />
      {badge !== undefined && badge > 0 && (
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{badge > 99 ? '99+' : badge}</Text>
        </View>
      )}
    </View>
  );
};

// Tabs principales de l'application
const MainTabs = () => {
  const insets = useSafeAreaInsets();
  const cart = useAppSelector((state) => state.cart);
  const itemsCount = cart?.itemsCount || 0;

  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#10B981', // Vert
        tabBarInactiveTintColor: '#9CA3AF',
        tabBarStyle: {
          height: 50 + insets.bottom,
          paddingBottom: insets.bottom > 0 ? insets.bottom : 2,
          paddingTop: 4,
          backgroundColor: '#FFFFFF',
          borderTopWidth: 1,
          borderTopColor: '#E5E7EB',
          elevation: 8,
          shadowColor: '#000',
          shadowOffset: {
            width: 0,
            height: -2,
          },
          shadowOpacity: 0.1,
          shadowRadius: 8,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
          marginTop: 0,
        },
        tabBarIconStyle: {
          marginTop: 0,
        },
        tabBarHideOnKeyboard: true,
      }}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{ 
          tabBarLabel: 'Accueil',
          tabBarIcon: ({ color, focused }) => (
            <TabBarIcon name="home" color={color} focused={focused} />
          ),
        }}
      />
      <Tab.Screen 
        name="Categories" 
        component={CategoryStack}
        options={{ 
          tabBarLabel: 'Catégories',
          unmountOnBlur: true,
          tabBarIcon: ({ color, focused }) => (
            <TabBarIcon name="grid" color={color} focused={focused} />
          ),
        }}
      />
      <Tab.Screen 
        name="Products" 
        component={ProductStack}
        options={{ 
          tabBarLabel: 'Produits',
          unmountOnBlur: true,
          tabBarIcon: ({ color, focused }) => (
            <TabBarIcon name="bag" color={color} focused={focused} />
          ),
        }}
      />
      <Tab.Screen 
        name="CartTab" 
        component={CartStack}
        options={{ 
          tabBarLabel: 'Panier',
          tabBarBadge: itemsCount > 0 ? itemsCount : undefined,
          tabBarIcon: ({ color, focused }) => (
            <TabBarIcon 
              name="cart" 
              color={color} 
              focused={focused} 
            />
          ),
        }}
      />
      <Tab.Screen 
        name="PriceCheck" 
        component={PriceCheckScreen}
        options={{ 
          tabBarLabel: 'Comparer',
          tabBarIcon: ({ color, focused }) => (
            <TabBarIcon name="scan" color={color} focused={focused} />
          ),
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileStack}
        options={{ 
          tabBarLabel: 'Profil',
          unmountOnBlur: true,
          tabBarIcon: ({ color, focused }) => (
            <TabBarIcon name="person" color={color} focused={focused} />
          ),
        }}
      />
    </Tab.Navigator>
  );
};

// Stack racine qui contient les tabs et le panier
const RootStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="MainTabs" component={MainTabs} />
    <Stack.Screen name="Cart" component={CartStack} />
  </Stack.Navigator>
);

// Navigation principale
const AppNavigator: React.FC = () => {
  const dispatch = useAppDispatch();
  const auth = useAppSelector((state) => state.auth);
  const isLoading = auth?.isLoading;
  const isAuthenticated = auth?.isAuthenticated;
  const isLoggingIn = auth?.isLoggingIn;
  const navigationRef = useNavigationContainerRef();
  const [currentRouteName, setCurrentRouteName] = useState<string | undefined>(undefined);
  const [isAuthModalVisible, setIsAuthModalVisible] = useState(false);
  const [hasDismissedAuthModal, setHasDismissedAuthModal] = useState(false);
  const authModalTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const excludedRoutes = ['Profile', 'ProfileMain', 'Login', 'Signup'];

  useEffect(() => {
    // Charger l'utilisateur au démarrage
    dispatch(loadUserAsync());
  }, [dispatch]);

  // Masquer le splash screen natif une fois que l'auth est chargée
  useEffect(() => {
    if (isLoading === false) {
      SplashScreen.hideAsync().catch(() => {});
    }
  }, [isLoading]);

  useEffect(() => {
    if (isAuthenticated) {
      setHasDismissedAuthModal(false);
      // Charger les favoris seulement après que loadUserAsync a fini (isLoading === false)
      // pour éviter un appel sans token valide au rehydrate de l'état persisté
      if (isLoading === false) {
        dispatch(fetchFavorites());
      }
    }
  }, [isAuthenticated, isLoading]);

  useEffect(() => {
    if (authModalTimerRef.current) {
      clearTimeout(authModalTimerRef.current);
      authModalTimerRef.current = null;
    }

    const shouldShowModal =
      !isLoading &&
      !isLoggingIn &&
      !isAuthenticated &&
      !hasDismissedAuthModal &&
      currentRouteName &&
      !excludedRoutes.includes(currentRouteName);

    if (shouldShowModal) {
      authModalTimerRef.current = setTimeout(() => {
        setIsAuthModalVisible(true);
      }, 800);
    } else {
      setIsAuthModalVisible(false);
    }

    return () => {
      if (authModalTimerRef.current) {
        clearTimeout(authModalTimerRef.current);
        authModalTimerRef.current = null;
      }
    };
  }, [isLoading, isLoggingIn, isAuthenticated, hasDismissedAuthModal, currentRouteName]);

  // Configuration des deep links
  const linking = {
    prefixes: ['bolibana://', 'https://www.bolibana.com', 'https://bolibana.com'],
    config: {
      screens: {
        Profile: {
          screens: {
            Orders: 'orders',
          },
        },
      },
    },
  };

  // Gérer les deep links pour les retours de paiement
  useEffect(() => {
    console.log('[AppNavigator] ========== LISTENER DEEP LINKS ==========');
    console.log('[AppNavigator] Initialisation du listener de deep links');
    console.log('[AppNavigator] Prefixes configurés:', ['bolibana://', 'https://www.bolibana.com', 'https://bolibana.com']);
    console.log('[AppNavigator] Pour payment-callback: Linking reçoit l\'URL seulement si elle est ouverte DEPUIS L\'EXTÉRIEUR de l\'app (pas depuis le WebBrowser in-app)');
    
    // Domaines autorisés pour les deep links de paiement
    const TRUSTED_HOSTS = ['www.bolibana.com', 'bolibana.com'];

    const isPaymentCallback = (url: string): boolean => {
      // Accepter le scheme bolibana:// natif
      if (url.startsWith('bolibana://')) {
        return url.includes('payment-success') || url.includes('payment_success');
      }
      // Pour les URLs HTTPS, vérifier le domaine avant tout
      try {
        const parsed = new URL(url);
        if (!TRUSTED_HOSTS.includes(parsed.hostname)) return false;
        return parsed.pathname.includes('/api/cart/payment-callback/');
      } catch {
        return false;
      }
    };

    const handleDeepLink = async (event: { url: string }) => {
      const { url } = event;
      if (__DEV__) console.log('[AppNavigator] Deep link reçu:', url);

      if (!isPaymentCallback(url)) return;

      try {
        await WebBrowser.dismissBrowser();
      } catch {
        // déjà fermé
      }

      let orderId: string | undefined;
      let orderNumber: string | undefined;

      try {
        const parsed = Linking.parse(url);
        orderId = parsed.queryParams?.order_id as string | undefined;
        orderNumber = parsed.queryParams?.order_number as string | undefined;
      } catch {
        // paramètres non disponibles
      }

      const nav = navigationRef.current;
      if (nav) {
        nav.navigate('Profile', {
          screen: 'Orders',
          params: orderId ? { orderId, orderNumber } : undefined
        });
      }
    };

    Linking.getInitialURL()
      .then((url) => { if (url) handleDeepLink({ url }); })
      .catch(() => {});

    const subscription = Linking.addEventListener('url', handleDeepLink);

    return () => {
      subscription.remove();
    };
  }, []);

  // N'afficher l'écran de chargement QUE lors du chargement initial de l'application
  // pour éviter de démonter toute la navigation lors d'un login ou d'une mise à jour de profil
  if (isLoading !== false) {
    return <LoadingScreen />;
  }

  return (
    <>
      <NavigationContainer
        ref={navigationRef}
        linking={linking}
        fallback={<LoadingScreen />}
        onReady={() => {
          const route = navigationRef.getCurrentRoute();
          setCurrentRouteName(route?.name);
          console.log('[AppNavigator] NavigationContainer prêt, route actuelle:', route?.name);
        }}
        onStateChange={() => {
          const route = navigationRef.getCurrentRoute();
          setCurrentRouteName(route?.name);
          console.log('[AppNavigator] État de navigation changé, route actuelle:', route?.name);
        }}
        onUnhandledAction={(action) => {
          console.log('[AppNavigator] Action non gérée:', action);
        }}
      >
        <RootStack />
      </NavigationContainer>
      <Modal
        visible={isAuthModalVisible}
        animationType="fade"
        transparent={true}
        onRequestClose={() => setIsAuthModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.authModalContent}>
            <View style={styles.authLogoContainer}>
              <Logo variant="full" dimension={52} showText={false} />
            </View>
            <Text style={styles.authModalSubtitle}>
              Connectez-vous ou créez un compte gratuit pour profiter de toutes les fonctionnalités.
            </Text>
            <View style={styles.authModalButtons}>
              <TouchableOpacity
                style={[styles.authModalButton, styles.authSecondaryButton]}
                onPress={() => {
                  setIsAuthModalVisible(false);
                  setHasDismissedAuthModal(true);
                  if (navigationRef.isReady()) {
                    navigationRef.navigate('Profile' as never, { screen: 'Signup' } as never);
                  }
                }}
              >
                <Text style={styles.authSecondaryText}>Créer un compte</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.authModalButton, styles.authPrimaryButton]}
                onPress={() => {
                  setIsAuthModalVisible(false);
                  setHasDismissedAuthModal(true);
                  if (navigationRef.isReady()) {
                    navigationRef.navigate('Profile' as never, { screen: 'Login' } as never);
                  }
                }}
              >
                <Text style={styles.authPrimaryText}>Se connecter</Text>
              </TouchableOpacity>
            </View>
            <TouchableOpacity
              style={styles.authCloseButton}
              onPress={() => {
                setIsAuthModalVisible(false);
                setHasDismissedAuthModal(true);
              }}
            >
              <Text style={styles.authCloseText}>Plus tard</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  iconContainer: {
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
  },
  badge: {
    position: 'absolute',
    top: -4,
    right: -8,
    backgroundColor: '#EF4444',
    borderRadius: 8,
    minWidth: 16,
    height: 16,
    paddingHorizontal: 4,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: '#FFFFFF',
  },
  badgeText: {
    color: '#FFFFFF',
    fontSize: 9,
    fontWeight: '700',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  authModalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: 20,
    paddingTop: 8,
    paddingBottom: 28,
    width: '90%',
    maxWidth: 400,
    alignItems: 'center',
  },
  authLogoContainer: {
    alignItems: 'center',
    alignSelf: 'center',
    marginTop: 8,
    marginBottom: 12,
  },
  authModalSubtitle: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 20,
  },
  authModalButtons: {
    flexDirection: 'row',
    gap: 8,
    width: '100%',
    marginBottom: 12,
  },
  authModalButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  authPrimaryButton: {
    backgroundColor: COLORS.PRIMARY,
  },
  authSecondaryButton: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: COLORS.PRIMARY,
  },
  authPrimaryText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '600',
  },
  authSecondaryText: {
    color: COLORS.PRIMARY,
    fontSize: 15,
    fontWeight: '600',
  },
  authCloseButton: {
    marginTop: 4,
  },
  authCloseText: {
    color: COLORS.TEXT_SECONDARY,
    fontSize: 14,
    fontWeight: '500',
  },
});

export default AppNavigator;
