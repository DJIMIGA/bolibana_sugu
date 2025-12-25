# Script PowerShell pour lister les programmes installés sur Windows
# et identifier ceux potentiellement inutilisés

Write-Host "=== LISTE DES PROGRAMMES INSTALLÉS ===" -ForegroundColor Green
Write-Host ""

# Lister les programmes depuis le registre (32 bits et 64 bits)
$programs32 = Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*" | 
    Where-Object { $_.DisplayName -ne $null } | 
    Select-Object DisplayName, DisplayVersion, Publisher, InstallDate, @{Name="Size";Expression={$_.EstimatedSize}}

$programs64 = Get-ItemProperty "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" | 
    Where-Object { $_.DisplayName -ne $null } | 
    Select-Object DisplayName, DisplayVersion, Publisher, InstallDate, @{Name="Size";Expression={$_.EstimatedSize}}

# Combiner et trier par nom
$allPrograms = ($programs32 + $programs64) | Sort-Object DisplayName -Unique

Write-Host "Nombre total de programmes: $($allPrograms.Count)" -ForegroundColor Cyan
Write-Host ""

# Afficher la liste
$allPrograms | Format-Table DisplayName, DisplayVersion, Publisher, InstallDate, @{Name="Taille (KB)";Expression={if($_.Size){[math]::Round($_.Size/1KB,2)}else{"N/A"}}} -AutoSize

# Exporter vers un fichier CSV
$csvPath = "programmes_installes_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
$allPrograms | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "Liste exportée vers: $csvPath" -ForegroundColor Yellow
Write-Host ""

# Identifier les programmes potentiellement inutilisés (critères simples)
Write-Host "=== PROGRAMMES POTENTIELLEMENT INUTILISÉS ===" -ForegroundColor Yellow
Write-Host "(Programmes installés il y a plus de 6 mois sans date de modification récente)" -ForegroundColor Gray
Write-Host ""

$oldPrograms = $allPrograms | Where-Object {
    if ($_.InstallDate) {
        try {
            $installDate = [DateTime]::ParseExact($_.InstallDate, "yyyyMMdd", $null)
            $monthsOld = (New-TimeSpan -Start $installDate -End (Get-Date)).Days / 30
            return $monthsOld -gt 6
        } catch {
            return $false
        }
    }
    return $false
}

if ($oldPrograms.Count -gt 0) {
    $oldPrograms | Format-Table DisplayName, DisplayVersion, Publisher, InstallDate -AutoSize
    Write-Host "Total: $($oldPrograms.Count) programmes anciens" -ForegroundColor Yellow
} else {
    Write-Host "Aucun programme ancien identifié selon les critères." -ForegroundColor Green
}

Write-Host ""
Write-Host "=== INSTRUCTIONS ===" -ForegroundColor Cyan
Write-Host "1. Ouvrez 'Paramètres' > 'Applications' pour désinstaller manuellement" -ForegroundColor White
Write-Host "2. Ou utilisez: appwiz.cpl pour le panneau de désinstallation classique" -ForegroundColor White
Write-Host "3. Vérifiez le fichier CSV pour une liste complète" -ForegroundColor White



