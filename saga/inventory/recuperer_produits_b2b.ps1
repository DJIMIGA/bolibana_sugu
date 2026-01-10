# Script PowerShell pour récupérer les produits B2B
# Usage: .\recuperer_produits_b2b.ps1 [-ApiKey VOTRE_CLE_API] [-PageSize 100] [-SaveJson]

param(
    [Parameter(Mandatory=$false)]
    [string]$ApiKey = "",
    
    [Parameter(Mandatory=$false)]
    [int]$PageSize = 100,
    
    [Parameter(Mandatory=$false)]
    [switch]$SaveJson = $false,
    
    [Parameter(Mandatory=$false)]
    [string]$JsonFile = "produits_b2b.json"
)

# URL de l'API B2B
$baseUrl = "https://www.bolibanastock.com/api/v1"
$productsEndpoint = "$baseUrl/b2c/products/"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RÉCUPÉRATION DES PRODUITS B2B" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si la clé API est fournie
if ([string]::IsNullOrEmpty($ApiKey)) {
    Write-Host "⚠️  Aucune clé API fournie" -ForegroundColor Yellow
    Write-Host "   Utilisez: .\recuperer_produits_b2b.ps1 -ApiKey VOTRE_CLE_API" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Ou récupérez les produits depuis la base de données locale avec:" -ForegroundColor Gray
    Write-Host "   python saga\inventory\recuperer_produits_b2b.py --source bdd" -ForegroundColor Gray
    exit 1
}

Write-Host "URL: $productsEndpoint" -ForegroundColor Gray
Write-Host "Page Size: $PageSize" -ForegroundColor Gray
Write-Host "Header X-API-Key: $($ApiKey.Substring(0, [Math]::Min(10, $ApiKey.Length)))..." -ForegroundColor Gray
Write-Host ""

$headers = @{
    "X-API-Key" = $ApiKey
    "Content-Type" = "application/json"
    "Accept" = "application/json"
}

$allProducts = @()
$page = 1
$hasNext = $true
$totalCount = 0

try {
    while ($hasNext) {
        Write-Host "📡 Récupération de la page $page..." -ForegroundColor Cyan
        
        $uri = "$productsEndpoint?page=$page&page_size=$PageSize"
        
        $response = Invoke-WebRequest -Uri $uri -Headers $headers -Method GET -ErrorAction Stop
        
        Write-Host "✅ Succès (Status: $($response.StatusCode))" -ForegroundColor Green
        
        $data = $response.Content | ConvertFrom-Json
        
        # Gérer différents formats de réponse
        $products = @()
        if ($data.results) {
            $products = $data.results
            $totalCount = $data.count
            $hasNext = $null -ne $data.next
        }
        elseif ($data.products) {
            $products = $data.products
            $hasNext = $false
        }
        elseif ($data -is [Array]) {
            $products = $data
            $hasNext = $false
        }
        else {
            $products = @($data)
            $hasNext = $false
        }
        
        Write-Host "   Produits récupérés: $($products.Count)" -ForegroundColor Gray
        if ($totalCount -gt 0) {
            Write-Host "   Total disponible: $totalCount" -ForegroundColor Gray
        }
        
        $allProducts += $products
        
        if (-not $hasNext) {
            break
        }
        
        $page++
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ RÉCUPÉRATION TERMINÉE" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Total de produits récupérés: $($allProducts.Count)" -ForegroundColor Green
    Write-Host ""
    
    # Afficher les 10 premiers produits
    Write-Host "PREMIERS PRODUITS (10 premiers):" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Gray
    $displayCount = [Math]::Min(10, $allProducts.Count)
    for ($i = 0; $i -lt $displayCount; $i++) {
        $product = $allProducts[$i]
        Write-Host ""
        Write-Host "$($i + 1). [$($product.id)] $($product.name -or $product.title)" -ForegroundColor White
        Write-Host "   SKU: $($product.sku -or 'N/A')" -ForegroundColor Gray
        Write-Host "   Prix: $($product.price) FCFA" -ForegroundColor Gray
        Write-Host "   Stock: $($product.stock -or 0)" -ForegroundColor Gray
        if ($product.category) {
            $categoryName = if ($product.category.name) { $product.category.name } else { $product.category }
            Write-Host "   Catégorie: $categoryName" -ForegroundColor Gray
        }
    }
    
    # Sauvegarder en JSON si demandé
    if ($SaveJson) {
        Write-Host ""
        Write-Host "💾 Sauvegarde dans $JsonFile..." -ForegroundColor Cyan
        
        $outputPath = Join-Path $PSScriptRoot $JsonFile
        $allProducts | ConvertTo-Json -Depth 10 | Out-File -FilePath $outputPath -Encoding UTF8
        
        Write-Host "✅ Fichier sauvegardé: $outputPath" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "RÉSUMÉ" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Total de produits: $($allProducts.Count)" -ForegroundColor White
    Write-Host "Pages récupérées: $($page - 1)" -ForegroundColor White
    if ($SaveJson) {
        Write-Host "Fichier JSON: $JsonFile" -ForegroundColor White
    }
    Write-Host "========================================" -ForegroundColor Cyan
    
}
catch {
    Write-Host ""
    Write-Host "❌ ERREUR!" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host "Message: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host ""
        Write-Host "Réponse du serveur:" -ForegroundColor Yellow
        Write-Host $responseBody
    }
    
    exit 1
}

