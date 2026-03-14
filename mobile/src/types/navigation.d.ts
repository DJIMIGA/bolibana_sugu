import { ParamListBase, RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { CompositeNavigationProp } from '@react-navigation/native';
import { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';

// Définition des paramètres pour chaque écran de la pile des produits
export type ProductStackParamList = {
  ProductList: { categoryId?: number; promo?: boolean } | undefined;
  ProductDetail: { slug: string };
};

// Définition des paramètres pour chaque écran du navigateur de tabulation principal
export type MainTabParamList = {
  Home: undefined;
  Categories: undefined;
  Products: { screen: keyof ProductStackParamList; params?: ProductStackParamList[keyof ProductStackParamList]; } | undefined;
  PriceCheck: undefined;
  Profile: undefined;
};

// Définition des paramètres pour la pile d'authentification (si nécessaire)
export type AuthStackParamList = {
  Login: undefined;
};

// Type pour la navigation globale (Root Stack Navigator)
// Contient les tabs principales et le panier
export type RootStackParamList = {
  MainTabs: undefined;
  Cart: undefined;
};

// Type composite pour `useNavigation` lorsqu'il navigue dans des piles imbriquées
// Par exemple, pour naviguer de HomeScreen (dans MainTabs) vers ProductDetail (dans ProductStack)
export type ProductListScreenNavigationProp = CompositeNavigationProp<
  BottomTabNavigationProp<MainTabParamList, 'Products'>,
  StackNavigationProp<ProductStackParamList, 'ProductList'>
>;

export type ProductDetailScreenNavigationProp = CompositeNavigationProp<
  BottomTabNavigationProp<MainTabParamList, 'Products'>,
  StackNavigationProp<ProductStackParamList, 'ProductDetail'>
>;

export type HomeScreenNavigationProp = CompositeNavigationProp<
  BottomTabNavigationProp<MainTabParamList, 'Home'>,
  StackNavigationProp<RootStackParamList>
>;

declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}

