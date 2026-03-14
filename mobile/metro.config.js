// Désactiver la vérification des versions en ligne pour éviter l'erreur "Body is unusable"
// Ces variables doivent être définies avant l'import de la config
process.env.EXPO_NO_DOTENV = '1';
process.env.EXPO_NO_TELEMETRY = '1';
// Désactiver la vérification des versions des modules natifs
process.env.EXPO_NO_VERSION_CHECK = '1';

const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Configuration pour améliorer la compatibilité Windows
config.watchFolders = [__dirname];

// Configuration du resolver pour éviter les problèmes de watch mode
config.resolver = {
  ...config.resolver,
  // Ignorer les patterns de fichiers problématiques sur Windows
  blockList: [
    /.*\/node_modules\/.*\/node_modules\/react-native\/.*/,
  ],
};

// Configuration du serveur Metro pour Windows
config.server = {
  ...config.server,
  // Augmenter le timeout pour Windows
  enhanceMiddleware: (middleware) => {
    return middleware;
  },
};

module.exports = config;









