# JavaScript pour l'application Accounts

Ce dossier contient tous les fichiers JavaScript nécessaires au fonctionnement de l'application `accounts`.

## Structure des fichiers

- `auth.js` : Gestion de l'authentification (connexion, inscription, mot de passe oublié)
- `user-profile.js` : Gestion du profil utilisateur et des préférences
- `notifications.js` : Gestion des notifications et messages
- `main.js` : Fichier principal qui initialise tous les modules

## Organisation

Les fichiers sont organisés de manière modulaire pour une meilleure maintenance :

```
accounts/
└── static/
    └── accounts/
        └── js/
            ├── auth.js
            ├── user-profile.js
            ├── notifications.js
            ├── main.js
            └── README.md
```

## Utilisation

1. Tous les fichiers JavaScript sont compilés avec Webpack
2. Le fichier `main.js` importe tous les autres modules
3. Les fichiers sont minifiés en production

## Bonnes pratiques

- Utiliser des fonctions nommées pour une meilleure lisibilité
- Documenter le code avec des commentaires
- Gérer les erreurs de manière appropriée
- Utiliser les promesses pour les opérations asynchrones
- Respecter les conventions de nommage 