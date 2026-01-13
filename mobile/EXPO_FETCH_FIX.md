# Solutions pour l'erreur "TypeError: fetch failed" avec Expo CLI

## Problème
L'erreur `TypeError: fetch failed` se produit lorsque Expo CLI essaie de récupérer les versions des modules natifs depuis l'API Expo.

## Solutions

### Solution 1 : Mode Offline (Recommandé pour développement local)
```powershell
cd mobile
npx expo start --offline
```

**Avantages :**
- Évite complètement les appels réseau vers l'API Expo
- Fonctionne même sans connexion internet
- Plus rapide au démarrage

**Inconvénients :**
- Ne vérifie pas les versions des modules natifs
- Peut utiliser des versions obsolètes

### Solution 2 : Ignorer la vérification des dépendances
```powershell
cd mobile
$env:EXPO_NO_DOTENV=1
npx expo start --no-dev --minify
```

### Solution 3 : Utiliser un port spécifique (évite la confirmation)
```powershell
cd mobile
npx expo start --port 8082 --offline
```

### Solution 4 : Configurer les variables d'environnement
Créer un fichier `.env` dans le dossier `mobile/` :
```env
EXPO_NO_DOTENV=1
EXPO_OFFLINE=1
```

### Solution 5 : Vérifier la connectivité réseau
```powershell
# Tester la connexion à l'API Expo
curl https://exp.host/--/api/v2/versions/native-modules
```

### Solution 6 : Désactiver temporairement la vérification
Modifier temporairement le comportement en utilisant :
```powershell
cd mobile
$env:EXPO_NO_UPDATE_CHECK=1
npx expo start
```

## Solution Permanente (Recommandée)

Pour éviter ce problème à chaque démarrage, ajoutez dans `package.json` :

```json
{
  "scripts": {
    "start": "expo start --offline",
    "start:online": "expo start"
  }
}
```

Ensuite, utilisez simplement :
```powershell
npm start
```

## Notes
- Le mode offline est généralement suffisant pour le développement local
- Pour les builds EAS, la vérification des versions est importante
- Si vous êtes derrière un proxy d'entreprise, configurez-le dans `.npmrc`
