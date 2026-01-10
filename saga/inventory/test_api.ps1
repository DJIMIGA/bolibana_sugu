# Script PowerShell pour tester l'API B2B
# Usage: .\test_api.ps1 VOTRE_CLE_API

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiKey
)

$uri = "https://www.bolibanastock.com/api/v1/b2c/categories/"

Write-Host "Test de l'API B2B..." -ForegroundColor Cyan
Write-Host "URL: $uri" -ForegroundColor Gray
Write-Host "Header X-API-Key: $($ApiKey.Substring(0, [Math]::Min(10, $ApiKey.Length)))..." -ForegroundColor Gray

try {
    $headers = @{
        "X-API-Key" = $ApiKey
        "Content-Type" = "application/json"
        "Accept" = "application/json"
    
        
    
    $response = Invoke-WebRequest -Uri $uri -Headers $headers -Method GET
    
    Write-Host "`n✅ SUCCÈS!" -ForegroundColor Green
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "`nRéponse:" -ForegroundColor Yellow
    $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
}
catch {
    Write-Host "`n❌ ERREUR!" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host "Message: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "`nRéponse du serveur:" -ForegroundColor Yellow
        Write-Host $responseBody
    }
}

