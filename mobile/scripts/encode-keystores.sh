#!/bin/bash
# Script pour encoder les keystores en base64
# Usage: ./scripts/encode-keystores.sh

echo "📦 Encodage des keystores en base64..."

profiles=("dev" "preview" "prod")

for profile in "${profiles[@]}"; do
    keystore_path="credentials/keystore-${profile}.jks"
    base64_path="credentials/keystore-${profile}.base64"
    
    if [ -f "$keystore_path" ]; then
        echo "   Encodage de keystore-${profile}.jks..."
        base64 "$keystore_path" | tr -d '\n' > "$base64_path"
        echo "   ✅ Fichier créé: $base64_path"
    else
        echo "   ⚠️  Fichier non trouvé: $keystore_path"
    fi
done

echo ""
echo "✅ Encodage terminé!"
echo "📝 Les fichiers base64 sont dans credentials/keystore-*.base64"







