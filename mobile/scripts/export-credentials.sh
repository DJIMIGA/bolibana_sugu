#!/bin/bash
# Script pour exporter les variables d'environnement des credentials selon le profil
# Usage: source scripts/export-credentials.sh [development|preview|production]

PROFILE=${1:-development}

if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env non trouvé. Créez-le à partir de .env.example"
    exit 1
fi

# Charger les variables depuis .env
export $(cat .env | grep -v '^#' | xargs)

# Sélectionner les variables selon le profil
case $PROFILE in
    development)
        export ANDROID_KEYSTORE_BASE64="$ANDROID_KEYSTORE_BASE64_DEV"
        export ANDROID_KEYSTORE_PASSWORD="$ANDROID_KEYSTORE_PASSWORD_DEV"
        export ANDROID_KEY_ALIAS="$ANDROID_KEY_ALIAS_DEV"
        export ANDROID_KEY_PASSWORD="$ANDROID_KEY_PASSWORD_DEV"
        export EAS_BUILD_PROFILE=development
        echo "✅ Variables exportées pour le profil DEVELOPMENT"
        ;;
    preview)
        export ANDROID_KEYSTORE_BASE64="$ANDROID_KEYSTORE_BASE64_PREVIEW"
        export ANDROID_KEYSTORE_PASSWORD="$ANDROID_KEYSTORE_PASSWORD_PREVIEW"
        export ANDROID_KEY_ALIAS="$ANDROID_KEY_ALIAS_PREVIEW"
        export ANDROID_KEY_PASSWORD="$ANDROID_KEY_PASSWORD_PREVIEW"
        export EAS_BUILD_PROFILE=preview
        echo "✅ Variables exportées pour le profil PREVIEW"
        ;;
    production)
        export ANDROID_KEYSTORE_BASE64="$ANDROID_KEYSTORE_BASE64_PROD"
        export ANDROID_KEYSTORE_PASSWORD="$ANDROID_KEYSTORE_PASSWORD_PROD"
        export ANDROID_KEY_ALIAS="$ANDROID_KEY_ALIAS_PROD"
        export ANDROID_KEY_PASSWORD="$ANDROID_KEY_PASSWORD_PROD"
        export EAS_BUILD_PROFILE=production
        echo "✅ Variables exportées pour le profil PRODUCTION"
        ;;
    *)
        echo "❌ Profil invalide: $PROFILE"
        echo "Usage: source scripts/export-credentials.sh [development|preview|production]"
        exit 1
        ;;
esac

echo "📦 Profil actif: $EAS_BUILD_PROFILE"
echo "🔑 Keystore Android: ${ANDROID_KEYSTORE_BASE64:0:20}..."
echo "🔐 Alias: $ANDROID_KEY_ALIAS"

