#!/bin/bash
# Script pour générer automatiquement les mots de passe pour les keystores
# Usage: ./scripts/generate-passwords.sh

echo "🔐 Génération des mots de passe sécurisés pour les keystores..."

# Créer le dossier credentials s'il n'existe pas
mkdir -p credentials

# Générer le mot de passe pour Development
DEV_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
echo "DEV_PASSWORD=$DEV_PASSWORD" > credentials/passwords-dev.txt
echo "✅ Mot de passe DEV généré et sauvegardé dans credentials/passwords-dev.txt"

# Générer le mot de passe pour Preview
PREVIEW_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
echo "PREVIEW_PASSWORD=$PREVIEW_PASSWORD" > credentials/passwords-preview.txt
echo "✅ Mot de passe PREVIEW généré et sauvegardé dans credentials/passwords-preview.txt"

# Générer le mot de passe pour Production
PROD_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
echo "PROD_PASSWORD=$PROD_PASSWORD" > credentials/passwords-prod.txt
echo "✅ Mot de passe PROD généré et sauvegardé dans credentials/passwords-prod.txt"

echo ""
echo "📋 Résumé des mots de passe générés :"
echo "   DEV:     $DEV_PASSWORD"
echo "   PREVIEW: $PREVIEW_PASSWORD"
echo "   PROD:    $PROD_PASSWORD"
echo ""
echo "⚠️  IMPORTANT :"
echo "   1. Les mots de passe sont sauvegardés dans credentials/passwords-*.txt"
echo "   2. Ces fichiers sont dans .gitignore et ne seront PAS commités"
echo "   3. Copiez ces mots de passe dans votre fichier .env"
echo "   4. Stockez-les également dans un gestionnaire de secrets sécurisé"
echo ""
echo "📝 Prochaines étapes :"
echo "   1. Copiez les mots de passe dans mobile/.env"
echo "   2. Utilisez-les lors de la génération des keystores"
echo "   3. Consultez mobile/docs/keystore-guide-pas-a-pas.md pour la suite"

