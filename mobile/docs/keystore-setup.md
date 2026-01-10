# Configuration des keystores et credentials EAS

Ce document explique comment préparer les clés Android et les certificats iOS pour les trois profils `development`, `preview` et `production`. Chaque profil doit disposer de ses propres credentials, car :

- `development` doit rester isolé et utiliser une clé de test (build interne).
- `preview` peut correspondre à une release de pré-production.
- `production` doit utiliser les clés finales (App Store et Play Store).

> **Important** : les keystores/identifiants réels ne doivent jamais être committés. Stockez-les dans un gestionnaire de secrets (GitHub Secrets, 1Password, etc.) et référencez-les via des variables d’environnement ou `eas credentials`.

## 1. Android : keystore par profil

### Génération
```bash
keytool -genkeypair \
  -alias bolibana_sugu \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -keystore credentials/keystore-{profil}.jks \
  -storepass changeit \
  -keypass changeit \
  -dname "CN=BoliBana,S=...</..."
```

Remplace `credentials/keystore-{profil}.jks` par `keystore-dev.jks`, `keystore-preview.jks` et `keystore-prod.jks`, et ajuste les mots de passe si nécessaire.

### Préparation pour EAS
Encode chaque fichier en base64 (utile pour CI) :
```bash
base64 credentials/keystore-dev.jks | tr -d '\n' > credentials/keystore-dev.base64
```

Déclare les variables d’environnement qui contiennent les blobs base64 et les métadonnées :

| Nom | Description |
| --- | --- |
| `ANDROID_KEYSTORE_BASE64_DEV` | contenu base64 du keystore dev |
| `ANDROID_KEYSTORE_BASE64_PREVIEW` | contenu base64 du keystore preview |
| `ANDROID_KEYSTORE_BASE64_PROD` | contenu base64 du keystore production |
| `ANDROID_KEYSTORE_PASSWORD` | mot de passe du keystore (identique pour tous ou spécifique) |
| `ANDROID_KEY_ALIAS` | alias utilisé lors de la génération (`bolibana_sugu`) |
| `ANDROID_KEY_PASSWORD` | mot de passe de la clé (souvent identique au storepass) |

### Utilisation
Avant de lancer un `eas build --profile ...`, exporte les variables voulues :
```bash
export ANDROID_KEYSTORE_BASE64="$ANDROID_KEYSTORE_BASE64_DEV"
export ANDROID_KEYSTORE_PASSWORD=changeit
export ANDROID_KEY_ALIAS=bolibana_sugu
export ANDROID_KEY_PASSWORD=changeit
EAS_BUILD_PROFILE=development eas build --profile development
```

Change simplement la variable `ANDROID_KEYSTORE_BASE64` selon le profil (`PREVIEW` ou `PROD`). Sur CI, définis les secrets correspondants et fais varier `EAS_BUILD_PROFILE`.

## 2. iOS : certificats et provisioning

1. Crée un certificat de distribution (Apple Developer) et exporte-le en `.p12`.
2. Génère un provisioning profile App Store.
3. Encode les fichiers en base64 :
   ```bash
   base64 ios/certificates/dist-cert.p12 > ios/certificates/dist-cert.base64
   base64 ios/certificates/provisioning-profile.mobileprovision > ios/certificates/provisioning.base64
   ```
4. Stocke les blobs dans les variables :
   - `EXPO_APPLE_DIST_CERT_BASE64`
   - `EXPO_APPLE_PROV_PROFILE_BASE64`
   - `EXPO_APPLE_APP_SPECIFIC_PASSWORD` (pour les opérations lors de `eas credentials` ou `expo upload`)
   - `EXPO_APPLE_ID` et `EXPO_APPLE_TEAM_ID` (facultatifs si tu utilises `eas credentials` interactif)

> Astuce : utilise `eas credentials` pour lier les fichiers à chaque profil (`EAS_BUILD_PROFILE=production eas credentials`). Tu peux aussi importer les fichiers manuellement via l’interface `eas`.

## 3. Intégration dans `eas.json`

Pour éviter les valeurs en dur, on repose sur les variables d’environnement copiées avant `eas build`. `eas.json` contient déjà les profils `development`, `preview` et `production`. Lors de chaque build :

1. Charge les variables correspondantes (via un script `source scripts/export-android.sh` ou CI).
2. Lance `EAS_BUILD_PROFILE` approprié (`development`, `preview`, `production`).
3. `eas` utilise automatiquement les variables `ANDROID_KEYSTORE_BASE64` et `EXPO_APPLE_*` fournies.

## 4. Scripts d'aide

Des scripts sont disponibles pour faciliter l'export des variables d'environnement selon le profil :

### Linux/macOS
```bash
source scripts/export-credentials.sh development
npm run build:dev
```

### Windows PowerShell
```powershell
.\scripts\export-credentials.ps1 development
npm run build:dev
```

Ces scripts chargent automatiquement les variables depuis `.env` et sélectionnent les credentials appropriés selon le profil.

## 5. Fichier .env.example

Un fichier `env.example` est fourni dans le dossier `mobile/` avec toutes les variables nécessaires. 

**Étapes** :
1. Copiez `env.example` en `.env` : `cp env.example .env`
2. Remplissez les valeurs base64 des keystores et certificats
3. Le fichier `.env` est déjà dans `.gitignore` et ne sera pas commité

## 6. Bonnes pratiques

- Crée un dossier `mobile/credentials/` (hors VCS) pour stocker les fichiers bruts et ajoute-le à `.gitignore`.
- Utilise `expo-cli`/`eas-cli` pour vérifier les credentials : `eas credentials --profile production`.
- Documente la procédure (comme ce fichier) et mets à jour ton README principal avec un lien vers ce guide.
- Ne jamais exposer les fichiers `.jks` ou `.p12` dans Git ; partage-les via un canal sécurisé (Slack privé, coffre-fort MDM, etc.).
- Utilisez les scripts fournis (`export-credentials.sh` ou `.ps1`) pour éviter les erreurs de configuration.

