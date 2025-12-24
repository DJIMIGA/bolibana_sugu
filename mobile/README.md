# SagaKore Mobile

Application mobile React Native avec Expo pour SagaKore.

## Architecture

- **Framework**: React Native avec Expo (~54.0.25)
- **Langage**: TypeScript
- **État global**: Redux Toolkit avec slices modulaires
- **Navigation**: React Navigation (Stack + Bottom Tabs)
- **HTTP Client**: Axios avec intercepteurs
- **Stockage local**: AsyncStorage
- **Gestion réseau**: @react-native-community/netinfo

## Structure

```
mobile/
├── src/
│   ├── components/          # Composants réutilisables
│   ├── screens/            # Écrans de l'application
│   ├── services/           # Services API et utilitaires
│   ├── store/              # Redux store
│   ├── hooks/              # Hooks personnalisés
│   ├── types/              # Types TypeScript
│   ├── utils/              # Fonctions utilitaires
│   └── navigation/         # Configuration de navigation
```

## Installation

```bash
cd mobile
npm install
```

## Développement

```bash
npm start
```

Pour Android:
```bash
npm run android
```

Pour iOS:
```bash
npm run ios
```

## Build

### Development
```bash
npm run build:dev
```

### Preview
```bash
npm run build:preview
```

### Production
```bash
npm run build:prod
```

## Soumission

### Android
```bash
npm run submit:android
```

### iOS
```bash
npm run submit:ios
```

## Configuration

Les variables d'environnement sont configurées dans `eas.json` pour chaque profil de build.

## Fonctionnalités

- Authentification JWT
- Mode hors ligne avec cache et synchronisation
- Gestion des produits et catégories
- Panier avec synchronisation
- Profil utilisateur
- Gestion d'erreurs globale

