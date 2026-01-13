# Script pour lancer un build preview avec les credentials locaux
# Usage: .\scripts\build-preview.ps1

Write-Host "[INFO] Configuration des credentials pour le profil PREVIEW..." -ForegroundColor Cyan

# Lire le keystore en base64
$keystoreBase64 = Get-Content "credentials\keystore-preview.base64" -Raw
$keystoreBase64 = $keystoreBase64.Trim()

# Lire le mot de passe
$passwordLine = Get-Content "credentials\passwords-preview.txt" | Select-String -Pattern 'PREVIEW_PASSWORD='
$password = $passwordLine -replace 'PREVIEW_PASSWORD=', ''

# Configurer les variables d'environnement
$env:ANDROID_KEYSTORE_BASE64 = $keystoreBase64
$env:ANDROID_KEYSTORE_PASSWORD = $password
$env:ANDROID_KEY_ALIAS = "bolibana_sugu_preview"
$env:ANDROID_KEY_PASSWORD = $password

Write-Host "[OK] Credentials configures" -ForegroundColor Green
Write-Host "[INFO] Alias: $env:ANDROID_KEY_ALIAS" -ForegroundColor Cyan

# Lancer le build
Write-Host "[INFO] Lancement du build preview..." -ForegroundColor Cyan
npx eas build --profile preview --platform android
