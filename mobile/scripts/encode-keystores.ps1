# Script PowerShell pour encoder les keystores en base64
# Usage: .\scripts\encode-keystores.ps1

Write-Host '📦 Encodage des keystores en base64...' -ForegroundColor Cyan

# Obtenir le chemin absolu du script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
# Le script est dans mobile/scripts/, donc le dossier mobile est le parent
$mobilePath = Split-Path -Parent $scriptPath

# Construire les chemins absolus
$credentialsPath = Join-Path $mobilePath "credentials"

$profiles = @('dev', 'preview', 'prod')

foreach ($profile in $profiles) {
    $keystorePath = Join-Path $credentialsPath "keystore-$profile.jks"
    $base64Path = Join-Path $credentialsPath "keystore-$profile.base64"
    
    if (Test-Path $keystorePath) {
        Write-Host "   Encodage de keystore-$profile.jks..." -ForegroundColor Yellow
        try {
            $content = [Convert]::ToBase64String([IO.File]::ReadAllBytes($keystorePath))
            $content | Out-File -FilePath $base64Path -Encoding ASCII -NoNewline
            Write-Host "   ✅ Fichier cree: $base64Path" -ForegroundColor Green
        } catch {
            Write-Host "   ❌ Erreur lors de l'encodage: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "   ⚠️  Fichier non trouve: $keystorePath" -ForegroundColor Yellow
    }
}

Write-Host ''
Write-Host '✅ Encodage termine!' -ForegroundColor Green
Write-Host '📝 Les fichiers base64 sont dans credentials/keystore-*.base64' -ForegroundColor Cyan

