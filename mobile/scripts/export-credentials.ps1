# Script PowerShell pour exporter les variables d'environnement des credentials selon le profil
# Usage: .\scripts\export-credentials.ps1 [development|preview|production]

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("development", "preview", "production")]
    [string]$Profile = "development"
)

# Verifier si le fichier .env existe
if (-not (Test-Path ".env")) {
    Write-Host '[WARNING] Fichier .env non trouve. Creez-le a partir de .env.example' -ForegroundColor Yellow
    exit 1
}

# Charger les variables depuis .env
Get-Content .env | Where-Object { $_ -notmatch '^#' -and $_ -match '=' } | ForEach-Object {
    $key, $value = $_ -split '=', 2
    if ($key -and $value) {
        [Environment]::SetEnvironmentVariable($key.Trim(), $value.Trim(), "Process")
    }
}

# Selectionner les variables selon le profil
switch ($Profile) {
    "development" {
        $env:ANDROID_KEYSTORE_BASE64 = $env:ANDROID_KEYSTORE_BASE64_DEV
        $env:ANDROID_KEYSTORE_PASSWORD = $env:ANDROID_KEYSTORE_PASSWORD_DEV
        $env:ANDROID_KEY_ALIAS = $env:ANDROID_KEY_ALIAS_DEV
        $env:ANDROID_KEY_PASSWORD = $env:ANDROID_KEY_PASSWORD_DEV
        $env:EAS_BUILD_PROFILE = "development"
        Write-Host '[OK] Variables exportees pour le profil DEVELOPMENT' -ForegroundColor Green
    }
    "preview" {
        $env:ANDROID_KEYSTORE_BASE64 = $env:ANDROID_KEYSTORE_BASE64_PREVIEW
        $env:ANDROID_KEYSTORE_PASSWORD = $env:ANDROID_KEYSTORE_PASSWORD_PREVIEW
        $env:ANDROID_KEY_ALIAS = $env:ANDROID_KEY_ALIAS_PREVIEW
        $env:ANDROID_KEY_PASSWORD = $env:ANDROID_KEY_PASSWORD_PREVIEW
        $env:EAS_BUILD_PROFILE = "preview"
        Write-Host '[OK] Variables exportees pour le profil PREVIEW' -ForegroundColor Green
    }
    "production" {
        $env:ANDROID_KEYSTORE_BASE64 = $env:ANDROID_KEYSTORE_BASE64_PROD
        $env:ANDROID_KEYSTORE_PASSWORD = $env:ANDROID_KEYSTORE_PASSWORD_PROD
        $env:ANDROID_KEY_ALIAS = $env:ANDROID_KEY_ALIAS_PROD
        $env:ANDROID_KEY_PASSWORD = $env:ANDROID_KEY_PASSWORD_PROD
        $env:EAS_BUILD_PROFILE = "production"
        Write-Host '[OK] Variables exportees pour le profil PRODUCTION' -ForegroundColor Green
    }
}

Write-Host "[INFO] Profil actif: $env:EAS_BUILD_PROFILE" -ForegroundColor Cyan
if ($env:ANDROID_KEYSTORE_BASE64) {
    $preview = $env:ANDROID_KEYSTORE_BASE64.Substring(0, [Math]::Min(20, $env:ANDROID_KEYSTORE_BASE64.Length))
    Write-Host "[INFO] Keystore Android: ${preview}..." -ForegroundColor Cyan
}
if ($env:ANDROID_KEY_ALIAS) {
    Write-Host "[INFO] Alias: $env:ANDROID_KEY_ALIAS" -ForegroundColor Cyan
}
