# Script pour configurer les credentials preview sur EAS
# Ce script prépare les informations nécessaires pour configurer les credentials
# Usage: .\scripts\setup-credentials-preview.ps1

Write-Host "[INFO] Preparation des credentials pour le profil PREVIEW..." -ForegroundColor Cyan

# Lire le mot de passe
$passwordLine = Get-Content "credentials\passwords-preview.txt" | Select-String -Pattern 'PREVIEW_PASSWORD='
$password = $passwordLine -replace 'PREVIEW_PASSWORD=', ''

Write-Host ""
Write-Host "===========================================" -ForegroundColor Yellow
Write-Host "INFORMATIONS POUR CONFIGURER LES CREDENTIALS" -ForegroundColor Yellow
Write-Host "===========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Fichier keystore: credentials\keystore-preview.jks" -ForegroundColor Cyan
Write-Host "Alias: bolibana_sugu_preview" -ForegroundColor Cyan
Write-Host "Mot de passe: $password" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour configurer les credentials, executez:" -ForegroundColor Green
Write-Host "  npx eas credentials --platform android" -ForegroundColor White
Write-Host ""
Write-Host "Puis:" -ForegroundColor Green
Write-Host "  1. Selectionnez le profil 'preview'" -ForegroundColor White
Write-Host "  2. Choisissez 'Set up a new Android Keystore'" -ForegroundColor White
Write-Host "  3. Selectionnez 'Upload a keystore file'" -ForegroundColor White
Write-Host "  4. Entrez le chemin: credentials\keystore-preview.jks" -ForegroundColor White
Write-Host "  5. Entrez l'alias: bolibana_sugu_preview" -ForegroundColor White
Write-Host "  6. Entrez le mot de passe: $password" -ForegroundColor White
Write-Host ""
Write-Host "OU utilisez directement le fichier .jks avec:" -ForegroundColor Green
Write-Host "  npx eas credentials --platform android --profile preview" -ForegroundColor White
Write-Host ""
