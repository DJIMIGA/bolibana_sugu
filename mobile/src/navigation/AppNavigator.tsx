import React, { useEffect } from 'react';
import { View, Text, StyleSheet, Platform } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { loadUserAsync } from '../store/slices/authSlice';
import { LoadingScreen } from '../components/LoadingScreen';

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
import WebViewScreen from '../screens/WebViewScreen';
import PriceCheckScreen from '../screens/PriceCheckScreen';
import AddressesScreen from '../screens/AddressesScreen';
import AddAddressScreen from '../screens/AddAddressScreen';
import OrdersScreen from '../screens/OrdersScreen';
import SettingsScreen from '../screens/SettingsScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Stack pour l'authentification
const AuthStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="Login" component={LoginScreen} />
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
    <Stack.Screen name="Settings" component={SettingsScreen} />
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
        component={CategoryScreen}
        options={{ 
          tabBarLabel: 'Catégories',
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

  useEffect(() => {
    // Charger l'utilisateur au démarrage
    dispatch(loadUserAsync());
  }, [dispatch]);

  // N'afficher l'écran de chargement QUE lors du chargement initial de l'application
  // pour éviter de démonter toute la navigation lors d'un login ou d'une mise à jour de profil
  if (isLoading !== false) {
    return <LoadingScreen />;
  }

  return (
    <NavigationContainer fallback={<LoadingScreen />}>
        <RootStack />
    </NavigationContainer>
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
});

export default AppNavigator;
