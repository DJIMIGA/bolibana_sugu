# Script PowerShell pour generer automatiquement les mots de passe pour les keystores
# Usage: .\scripts\generate-passwords.ps1

Write-Host '🔐 Generation des mots de passe securises pour les keystores...' -ForegroundColor Cyan

# Creer le dossier credentials s'il n'existe pas
if (-not (Test-Path 'credentials')) {
    New-Item -ItemType Directory -Path 'credentials' | Out-Null
}

# Fonction pour generer un mot de passe aleatoire
function Generate-Password {
    $chars = (48..57) + (65..90) + (97..122)  # Chiffres, majuscules, minuscules
    return -join ($chars | Get-Random -Count 25 | ForEach-Object {[char]$_})
}

# Generer le mot de passe pour Development
$DEV_PASSWORD = Generate-Password
"DEV_PASSWORD=$DEV_PASSWORD" | Out-File -FilePath 'credentials/passwords-dev.txt' -Encoding ASCII
Write-Host '✅ Mot de passe DEV genere et sauvegarde dans credentials/passwords-dev.txt' -ForegroundColor Green

# Generer le mot de passe pour Preview
$PREVIEW_PASSWORD = Generate-Password
"PREVIEW_PASSWORD=$PREVIEW_PASSWORD" | Out-File -FilePath 'credentials/passwords-preview.txt' -Encoding ASCII
Write-Host '✅ Mot de passe PREVIEW genere et sauvegarde dans credentials/passwords-preview.txt' -ForegroundColor Green

# Generer le mot de passe pour Production
$PROD_PASSWORD = Generate-Password
"PROD_PASSWORD=$PROD_PASSWORD" | Out-File -FilePath 'credentials/passwords-prod.txt' -Encoding ASCII
Write-Host '✅ Mot de passe PROD genere et sauvegarde dans credentials/passwords-prod.txt' -ForegroundColor Green

Write-Host ''
Write-Host '📋 Resume des mots de passe generes :' -ForegroundColor Yellow
Write-Host "   DEV:     $DEV_PASSWORD" -ForegroundColor White
Write-Host "   PREVIEW: $PREVIEW_PASSWORD" -ForegroundColor White
Write-Host "   PROD:    $PROD_PASSWORD" -ForegroundColor White
Write-Host ''
Write-Host '⚠️  IMPORTANT :' -ForegroundColor Red
Write-Host '   1. Les mots de passe sont sauvegardes dans credentials/passwords-*.txt' -ForegroundColor Yellow
Write-Host '   2. Ces fichiers sont dans .gitignore et ne seront PAS commites' -ForegroundColor Yellow
Write-Host '   3. Copiez ces mots de passe dans votre fichier .env' -ForegroundColor Yellow
Write-Host '   4. Stockez-les egalement dans un gestionnaire de secrets securise' -ForegroundColor Yellow
Write-Host ''
Write-Host '📝 Prochaines etapes :' -ForegroundColor Cyan
Write-Host '   1. Copiez les mots de passe dans mobile/.env' -ForegroundColor White
Write-Host '   2. Utilisez-les lors de la generation des keystores' -ForegroundColor White
Write-Host '   3. Consultez mobile/docs/keystore-guide-pas-a-pas.md pour la suite' -ForegroundColor White
