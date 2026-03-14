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

### Configuration des Keystores et Credentials

Avant de lancer un build, vous devez configurer les keystores Android et les certificats iOS pour chaque profil (development, preview, production).

**📖 Guides disponibles** :
- [`docs/keystore-setup.md`](docs/keystore-setup.md) - Documentation technique complète
- [`docs/keystore-guide-pas-a-pas.md`](docs/keystore-guide-pas-a-pas.md) - **Guide pas à pas pratique** ⭐

**⚠️ Important** : Les fichiers de credentials (`.jks`, `.p12`, `.mobileprovision`) ne doivent **JAMAIS** être commités dans Git. Utilisez un gestionnaire de secrets pour stocker les valeurs base64.

**🚀 Pour commencer rapidement** : Suivez le [guide pas à pas](docs/keystore-guide-pas-a-pas.md) qui vous accompagne étape par étape.

## Fonctionnalités

- Authentification JWT
- Mode hors ligne avec cache et synchronisation
- Gestion des produits et catégories
- Panier avec synchronisation
- Profil utilisateur
- Gestion d'erreurs globale

## Dépannage

### Erreurs Metro sur Windows

Si vous rencontrez les erreurs suivantes sur Windows :
- `Failed to start watch mode`
- `TypeError: Body is unusable`

#### Solutions

1. **Nettoyer le cache Metro** :
   ```bash
   npm run reset
   ```
   ou
   ```bash
   npx expo start --clear --reset-cache
   ```

2. **Vérifier la configuration Metro** :
   La configuration Metro (`metro.config.js`) a été optimisée pour Windows avec :
   - Désactivation de la vérification des versions en ligne
   - Configuration du watcher pour Windows
   - Optimisation du resolver

3. **Si les problèmes persistent** :
   - Fermer tous les processus Node.js et Expo
   - Supprimer le dossier `node_modules` et réinstaller :
     ```bash
     rm -rf node_modules
     npm install
     ```
   - Redémarrer l'application :
     ```bash
     npm run start:clear
     ```

4. **Problèmes de réseau/proxy** :
   Si vous êtes derrière un proxy, configurez les variables d'environnement :
   ```bash
   set HTTP_PROXY=http://proxy:port
   set HTTPS_PROXY=http://proxy:port
   ```

### Autres problèmes courants

- **Port déjà utilisé** : Changer le port avec `expo start --port 8082`
- **Cache corrompu** : Utiliser `npm run reset` pour tout nettoyer
- **Problèmes de dépendances** : Vérifier la compatibilité des versions dans `package.json`

