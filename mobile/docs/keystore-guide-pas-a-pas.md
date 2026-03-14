# Guide Pas à Pas - Configuration des Keystores EAS

Ce guide vous accompagne étape par étape pour configurer les keystores et credentials nécessaires aux builds EAS.

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir :
- ✅ Java JDK installé (pour `keytool`)
- ✅ EAS CLI installé : `npm install -g eas-cli` ou `npx eas-cli`
- ✅ Un compte Expo/EAS configuré
- ✅ Pour iOS : Un compte Apple Developer (pour production)

---

## 🚀 Étape 1 : Créer le dossier credentials

Créez un dossier pour stocker vos fichiers de credentials (ce dossier ne sera pas commité) :

```bash
cd mobile
mkdir credentials
```

**Windows PowerShell :**
```powershell
cd mobile
New-Item -ItemType Directory -Path credentials
```

---

## 🔐 Étape 2 : Générer les mots de passe automatiquement

Avant de générer les keystores, générons des mots de passe sécurisés automatiquement avec le script fourni :

### 2.1 Générer tous les mots de passe en une commande

**Linux/macOS :**
```bash
chmod +x scripts/generate-passwords.sh
./scripts/generate-passwords.sh
```

**Windows PowerShell :**
```powershell
.\scripts\generate-passwords.ps1
```

Le script va :
- ✅ Générer 3 mots de passe sécurisés (un par profil)
- ✅ Les sauvegarder dans `credentials/passwords-*.txt`
- ✅ Afficher un résumé avec les mots de passe générés

**⚠️ Important** : 
- Les fichiers `passwords-*.txt` contiennent vos mots de passe. **NE LES COMMITTEZ JAMAIS** ! Ils sont déjà dans `.gitignore`.
- Notez ces mots de passe dans un gestionnaire de secrets sécurisé (1Password, Bitwarden, etc.)
- Vous en aurez besoin pour remplir le fichier `.env` et pour les builds EAS

---

## 🔐 Étape 3 : Générer les keystores Android

### 3.1 Keystore pour Development

**Linux/macOS :**
```bash
source credentials/passwords-dev.txt
keytool -genkeypair \
  -alias bolibana_sugu_dev \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -keystore credentials/keystore-dev.jks \
  -storepass "$DEV_PASSWORD" \
  -keypass "$DEV_PASSWORD" \
  -dname "CN=BoliBana Sugu Dev, OU=Development, O=BoliBana, L=Bamako, ST=Bamako, C=ML"
```

**Windows PowerShell :**
```powershell
$DEV_PASSWORD = (Get-Content "credentials/passwords-dev.txt" | Select-String "DEV_PASSWORD=").ToString().Split('=')[1]
keytool -genkeypair `
  -alias bolibana_sugu_dev `
  -keyalg RSA `
  -keysize 2048 `
  -validity 10000 `
  -keystore credentials/keystore-dev.jks `
  -storepass "$DEV_PASSWORD" `
  -keypass "$DEV_PASSWORD" `
  -dname "CN=BoliBana Sugu Dev, OU=Development, O=BoliBana, L=Bamako, ST=Bamako, C=ML"
```

### 3.2 Keystore pour Preview

**Linux/macOS :**
```bash
source credentials/passwords-preview.txt
keytool -genkeypair \
  -alias bolibana_sugu_preview \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -keystore credentials/keystore-preview.jks \
  -storepass "$PREVIEW_PASSWORD" \
  -keypass "$PREVIEW_PASSWORD" \
  -dname "CN=BoliBana Sugu Preview, OU=Preview, O=BoliBana, L=Bamako, ST=Bamako, C=ML"
```

**Windows PowerShell :**
```powershell
$PREVIEW_PASSWORD = (Get-Content "credentials/passwords-preview.txt" | Select-String "PREVIEW_PASSWORD=").ToString().Split('=')[1]
keytool -genkeypair `
  -alias bolibana_sugu_preview `
  -keyalg RSA `
  -keysize 2048 `
  -validity 10000 `
  -keystore credentials/keystore-preview.jks `
  -storepass "$PREVIEW_PASSWORD" `
  -keypass "$PREVIEW_PASSWORD" `
  -dname "CN=BoliBana Sugu Preview, OU=Preview, O=BoliBana, L=Bamako, ST=Bamako, C=ML"
```

### 3.3 Keystore pour Production

**Linux/macOS :**
```bash
source credentials/passwords-prod.txt
keytool -genkeypair \
  -alias bolibana_sugu_prod \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -keystore credentials/keystore-prod.jks \
  -storepass "$PROD_PASSWORD" \
  -keypass "$PROD_PASSWORD" \
  -dname "CN=BoliBana Sugu, OU=Production, O=BoliBana, L=Bamako, ST=Bamako, C=ML"
```

**Windows PowerShell :**
```powershell
$PROD_PASSWORD = (Get-Content "credentials/passwords-prod.txt" | Select-String "PROD_PASSWORD=").ToString().Split('=')[1]
keytool -genkeypair `
  -alias bolibana_sugu_prod `
  -keyalg RSA `
  -keysize 2048 `
  -validity 10000 `
  -keystore credentials/keystore-prod.jks `
  -storepass "$PROD_PASSWORD" `
  -keypass "$PROD_PASSWORD" `
  -dname "CN=BoliBana Sugu, OU=Production, O=BoliBana, L=Bamako, ST=Bamako, C=ML"
```

**🔒 Les mots de passe sont générés automatiquement et stockés dans `credentials/passwords-*.txt`**

---

## 📦 Étape 4 : Encoder les keystores en base64

### 4.1 Encoder tous les keystores automatiquement (recommandé)

**Linux/macOS :**
```bash
chmod +x scripts/encode-keystores.sh
./scripts/encode-keystores.sh
```

**Windows PowerShell :**
```powershell
.\scripts\encode-keystores.ps1
```

Le script va automatiquement encoder tous les keystores présents dans `credentials/` et créer les fichiers `.base64` correspondants.

### 4.2 Encoder manuellement (optionnel)

Si vous préférez encoder manuellement chaque keystore :

**Linux/macOS :**
```bash
base64 credentials/keystore-dev.jks | tr -d '\n' > credentials/keystore-dev.base64
base64 credentials/keystore-preview.jks | tr -d '\n' > credentials/keystore-preview.base64
base64 credentials/keystore-prod.jks | tr -d '\n' > credentials/keystore-prod.base64
```

**Windows PowerShell :**
```powershell
# S'assurer d'être dans le dossier mobile
cd mobile

# Encoder le keystore Development
$content = [Convert]::ToBase64String([IO.File]::ReadAllBytes("credentials\keystore-dev.jks"))
$content | Out-File -FilePath "credentials\keystore-dev.base64" -Encoding ASCII -NoNewline

# Encoder le keystore Preview
$content = [Convert]::ToBase64String([IO.File]::ReadAllBytes("credentials\keystore-preview.jks"))
$content | Out-File -FilePath "credentials\keystore-preview.base64" -Encoding ASCII -NoNewline

# Encoder le keystore Production
$content = [Convert]::ToBase64String([IO.File]::ReadAllBytes("credentials\keystore-prod.jks"))
$content | Out-File -FilePath "credentials\keystore-prod.base64" -Encoding ASCII -NoNewline
```

---

## 📝 Étape 5 : Configurer le fichier .env

### 5.1 Copier le fichier exemple

```bash
cp env.example .env
```

**Windows PowerShell :**
```powershell
Copy-Item env.example .env
```

### 5.2 Remplir les valeurs base64 et mots de passe

Ouvrez le fichier `mobile/.env` et remplissez les valeurs :

1. **Lisez les mots de passe générés** :

**Linux/macOS :**
```bash
cat credentials/passwords-dev.txt
cat credentials/passwords-preview.txt
cat credentials/passwords-prod.txt
```

**Windows PowerShell :**
```powershell
Get-Content credentials/passwords-dev.txt
Get-Content credentials/passwords-preview.txt
Get-Content credentials/passwords-prod.txt
```

2. **Lisez le contenu des fichiers base64** :

**Linux/macOS :**
```bash
cat credentials/keystore-dev.base64
cat credentials/keystore-preview.base64
cat credentials/keystore-prod.base64
```

**Windows PowerShell :**
```powershell
Get-Content credentials/keystore-dev.base64
Get-Content credentials/keystore-preview.base64
Get-Content credentials/keystore-prod.base64
```

3. **Copiez chaque valeur** et collez-la dans `.env` :

```env
# Keystores base64
ANDROID_KEYSTORE_BASE64_DEV=<collez le contenu de keystore-dev.base64 ici>
ANDROID_KEYSTORE_BASE64_PREVIEW=<collez le contenu de keystore-preview.base64 ici>
ANDROID_KEYSTORE_BASE64_PROD=<collez le contenu de keystore-prod.base64 ici>

# Mots de passe (utilisez ceux générés dans passwords-*.txt)
# Pour development
ANDROID_KEYSTORE_PASSWORD_DEV=<collez le mot de passe DEV généré>
ANDROID_KEY_ALIAS_DEV=bolibana_sugu_dev
ANDROID_KEY_PASSWORD_DEV=<même mot de passe que DEV_PASSWORD>

# Pour preview
ANDROID_KEYSTORE_PASSWORD_PREVIEW=<collez le mot de passe PREVIEW généré>
ANDROID_KEY_ALIAS_PREVIEW=bolibana_sugu_preview
ANDROID_KEY_PASSWORD_PREVIEW=<même mot de passe que PREVIEW_PASSWORD>

# Pour production
ANDROID_KEYSTORE_PASSWORD_PROD=<collez le mot de passe PROD généré>
ANDROID_KEY_ALIAS_PROD=bolibana_sugu_prod
ANDROID_KEY_PASSWORD_PROD=<même mot de passe que PROD_PASSWORD>
```

**⚠️ Important** : 
- Utilisez les mots de passe générés automatiquement (pas `changeit`)
- Chaque profil a son propre alias et mot de passe
- Les fichiers `passwords-*.txt` contiennent les mots de passe originaux

---

## 🍎 Étape 6 : Configuration iOS (optionnel pour le moment)

Si vous ne build pas encore pour iOS, vous pouvez ignorer cette étape pour l'instant.

### 6.1 Obtenir les certificats iOS

1. Connectez-vous à [Apple Developer](https://developer.apple.com)
2. Créez un certificat de distribution
3. Téléchargez le fichier `.cer` et convertissez-le en `.p12`
4. Téléchargez le provisioning profile `.mobileprovision`

### 6.2 Encoder les fichiers iOS

**Linux/macOS :**
```bash
base64 ios/certificates/dist-cert.p12 | tr -d '\n' > ios/certificates/dist-cert.base64
base64 ios/certificates/provisioning-profile.mobileprovision | tr -d '\n' > ios/certificates/provisioning.base64
```

**Windows PowerShell :**
```powershell
$cert = [Convert]::ToBase64String([IO.File]::ReadAllBytes("ios/certificates/dist-cert.p12"))
$cert | Out-File -FilePath "ios/certificates/dist-cert.base64" -Encoding ASCII -NoNewline

$prov = [Convert]::ToBase64String([IO.File]::ReadAllBytes("ios/certificates/provisioning-profile.mobileprovision"))
$prov | Out-File -FilePath "ios/certificates/provisioning.base64" -Encoding ASCII -NoNewline
```

### 6.3 Ajouter les valeurs dans .env

```env
EXPO_APPLE_DIST_CERT_BASE64=<contenu base64 du .p12>
EXPO_APPLE_PROV_PROFILE_BASE64=<contenu base64 du .mobileprovision>
EXPO_APPLE_DIST_CERT_PASSWORD=<mot de passe du .p12>
EXPO_APPLE_ID=<votre Apple ID>
EXPO_APPLE_TEAM_ID=<votre Team ID>
```

---

## ✅ Étape 7 : Vérifier la configuration

### 7.1 Vérifier que les fichiers sont bien ignorés

Vérifiez que `.gitignore` contient bien :
```
mobile/credentials/
mobile/**/*.jks
mobile/**/*.keystore
```

### 7.2 Tester l'export des variables

**Linux/macOS :**
```bash
source scripts/export-credentials.sh development
echo $ANDROID_KEYSTORE_BASE64
```

**Windows PowerShell :**
```powershell
.\scripts\export-credentials.ps1 development
echo $env:ANDROID_KEYSTORE_BASE64
```

Si vous voyez une longue chaîne base64, c'est bon ! ✅

---

## 🏗️ Étape 8 : Premier build de test

### 8.1 Build Development

**Linux/macOS :**
```bash
source scripts/export-credentials.sh development
npm run build:dev
```

**Windows PowerShell :**
```powershell
.\scripts\export-credentials.ps1 development
npm run build:dev
```

### 8.2 Vérifier avec EAS CLI

```bash
eas credentials --profile development
```

Cela vous permettra de voir et gérer les credentials via l'interface EAS.

---

## 🔄 Étape 9 : Configuration pour CI/CD (optionnel)

Si vous utilisez GitHub Actions ou un autre CI :

1. **Ajoutez les secrets dans votre CI** :
   - `ANDROID_KEYSTORE_BASE64_DEV`
   - `ANDROID_KEYSTORE_BASE64_PREVIEW`
   - `ANDROID_KEYSTORE_BASE64_PROD`
   - `ANDROID_KEYSTORE_PASSWORD`
   - `ANDROID_KEY_ALIAS`
   - `ANDROID_KEY_PASSWORD`

2. **Dans votre workflow CI**, exportez les variables avant le build :
   ```yaml
   - name: Export credentials
     run: |
       export ANDROID_KEYSTORE_BASE64="${{ secrets.ANDROID_KEYSTORE_BASE64_DEV }}"
       export ANDROID_KEYSTORE_PASSWORD="${{ secrets.ANDROID_KEYSTORE_PASSWORD }}"
   ```

---

## 📚 Résumé des commandes importantes

### Générer un keystore
```bash
keytool -genkeypair -alias <alias> -keystore credentials/keystore-<profil>.jks ...
```

### Encoder en base64
```bash
base64 credentials/keystore-<profil>.jks | tr -d '\n' > credentials/keystore-<profil>.base64
```

### Exporter les variables
```bash
source scripts/export-credentials.sh <profil>
```

### Lancer un build
```bash
npm run build:dev    # ou build:preview ou build:prod
```

### Vérifier les credentials
```bash
eas credentials --profile <profil>
```

---

## 🆘 Dépannage

### Erreur : "keytool: command not found"
**Solution** : Installez Java JDK et ajoutez-le au PATH.

### Erreur : "Keystore was tampered with, or password was incorrect"
**Solution** : Vérifiez que le mot de passe dans `.env` correspond à celui utilisé lors de la génération.

### Erreur : "Alias does not exist"
**Solution** : Vérifiez que `ANDROID_KEY_ALIAS` dans `.env` correspond à l'alias utilisé lors de la génération.

### Les builds fonctionnent mais les credentials ne sont pas utilisés
**Solution** : Assurez-vous d'exporter les variables AVANT de lancer le build avec le script d'export.

---

## ✨ Prochaines étapes

Une fois la configuration terminée :

1. ✅ Testez un build development
2. ✅ Testez un build preview
3. ✅ Configurez les credentials iOS si nécessaire
4. ✅ Configurez votre CI/CD pour utiliser ces credentials
5. ✅ Documentez les mots de passe dans un gestionnaire de secrets sécurisé

**🎉 Félicitations ! Votre configuration est prête pour les builds EAS.**

