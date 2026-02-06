import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, Platform, Modal, TouchableOpacity, Linking } from 'react-native';
import { NavigationContainer, useNavigationContainerRef } from '@react-navigation/native';
import * as WebBrowser from 'expo-web-browser';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { loadUserAsync } from '../store/slices/authSlice';
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
import PriceCheckScreen from '../screens/PriceCheckScreen';
import AddressesScreen from '../screens/AddressesScreen';
import AddAddressScreen from '../screens/AddAddressScreen';
import OrdersScreen from '../screens/OrdersScreen';
import OrderDetailScreen from '../screens/OrderDetailScreen';
import SettingsScreen from '../screens/SettingsScreen';
import LoyaltyScreen from '../screens/LoyaltyScreen';

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
        size={24} 
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
          height: Platform.OS === 'ios' ? 60 + insets.bottom : 60 + insets.bottom,
          paddingBottom: insets.bottom > 0 ? insets.bottom : Platform.OS === 'ios' ? 10 : 8,
          paddingTop: 8,
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
          fontSize: 12,
          fontWeight: '600',
          marginTop: 4,
        },
        tabBarIconStyle: {
          marginTop: 4,
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

  useEffect(() => {
    if (isAuthenticated) {
      setHasDismissedAuthModal(false);
    }
  }, [isAuthenticated]);

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
    
    const handleDeepLink = async (event: { url: string }) => {
      const { url } = event;
      console.log('[AppNavigator] ========== URL INTERCEPTÉE VIA LINKING ==========');
      console.log('[AppNavigator] OUI - L\'app a reçu une URL via Linking.getInitialURL() ou addEventListener(\'url\')');
      console.log('[AppNavigator] URL complète:', url);
      console.log('[AppNavigator] Type:', typeof url);
      console.log('[AppNavigator] Contient payment-success:', url.includes('payment-success'));
      console.log('[AppNavigator] Contient payment_success:', url.includes('payment_success'));
      console.log('[AppNavigator] Contient payment-callback:', url.includes('payment-callback'));
      console.log('[AppNavigator] Contient /api/cart/payment-callback/:', url.includes('/api/cart/payment-callback/'));
      
      // Si c'est un retour de paiement (deep link bolibana:// ou URL HTTPS payment-callback)
      if (url.includes('payment-success') || url.includes('payment_success') || url.includes('/api/cart/payment-callback/')) {
        console.log('[AppNavigator] ✅ Retour de paiement détecté, fermeture du WebBrowser');
        
        // Fermer le WebBrowser si ouvert
        try {
          await WebBrowser.dismissBrowser();
          console.log('[AppNavigator] WebBrowser fermé après deep link');
        } catch (e) {
          console.log('[AppNavigator] WebBrowser déjà fermé ou non ouvert:', e);
        }
        
        // Extraire les paramètres de l'URL si disponibles
        let orderId: string | undefined;
        let orderNumber: string | undefined;
        
        try {
          const parsed = Linking.parse(url);
          orderId = parsed.queryParams?.order_id as string | undefined;
          orderNumber = parsed.queryParams?.order_number as string | undefined;
          console.log('[AppNavigator] Paramètres extraits - orderId:', orderId, 'orderNumber:', orderNumber);
        } catch (e) {
          console.log('[AppNavigator] Erreur lors de l\'extraction des paramètres:', e);
        }
        
        // Naviguer vers les commandes
        const nav = navigationRef.current;
        if (nav) {
          nav.navigate('Profile', { 
            screen: 'Orders',
            params: orderId ? { orderId, orderNumber } : undefined
          });
          console.log('[AppNavigator] Navigation vers Profile > Orders');
        }
      }
    };

    // Écouter les deep links au démarrage
    console.log('[AppNavigator] Vérification de l\'URL initiale (getInitialURL)...');
    Linking.getInitialURL()
      .then((url) => {
        if (url) {
          console.log('[AppNavigator] URL initiale trouvée (app lancée via lien):', url);
          handleDeepLink({ url });
        } else {
          console.log('[AppNavigator] Aucune URL initiale (app non lancée via lien)');
        }
      })
      .catch((error) => {
        console.error('[AppNavigator] Erreur getInitialURL:', error);
      });

    // Écouter les deep links pendant l'exécution (URL ouverte pendant que l'app est au premier plan)
    console.log('[AppNavigator] Listener addEventListener(\'url\') actif - en attente d\'URL...');
    const subscription = Linking.addEventListener('url', (event) => {
      console.log('[AppNavigator] >>> Événement "url" déclenché - Linking a reçu une URL:', event.url);
      handleDeepLink(event);
    });

    return () => {
      console.log('[AppNavigator] Nettoyage du listener de deep links');
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
            <Text style={styles.authModalTitle}>Rejoignez</Text>
            <View style={styles.authLogoContainer}>
              <Logo size="medium" dimension={120} showText={false} />
              <Text style={styles.authAppTitle}>Sugu</Text>
            </View>
            <Text style={styles.authModalSubtitle}>
              Connectez-vous ou créez un compte pour profiter de toutes les fonctionnalités.
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
    top: -6,
    right: -10,
    backgroundColor: '#EF4444', // Rouge
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    paddingHorizontal: 6,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  badgeText: {
    color: '#FFFFFF',
    fontSize: 10,
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
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'center',
    gap: 8,
    marginBottom: 4,
  },
  authAppTitle: {
    fontSize: 26,
    fontWeight: '700',
    color: COLORS.PRIMARY,
    letterSpacing: 0.5,
  },
  authModalTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: COLORS.TEXT,
    marginTop: 0,
    marginBottom: 6,
    textAlign: 'center',
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
