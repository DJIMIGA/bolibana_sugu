# Script PowerShell pour désinstaller un programme
# Usage: .\uninstall_program.ps1 -ProgramName "Nom du programme"

param(
    [Parameter(Mandatory=$true)]
    [string]$ProgramName
)

Write-Host "Recherche du programme: $ProgramName" -ForegroundColor Cyan

# Rechercher dans le registre
$program32 = Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*" | 
    Where-Object { $_.DisplayName -like "*$ProgramName*" } | 
    Select-Object DisplayName, UninstallString, PSChildName

$program64 = Get-ItemProperty "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" | 
    Where-Object { $_.DisplayName -like "*$ProgramName*" } | 
    Select-Object DisplayName, UninstallString, PSChildName

$programs = ($program32 + $program64) | Sort-Object DisplayName -Unique

if ($programs.Count -eq 0) {
    Write-Host "Aucun programme trouvé avec le nom: $ProgramName" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Programmes trouvés:" -ForegroundColor Yellow
$index = 1
foreach ($prog in $programs) {
    Write-Host "$index. $($prog.DisplayName)" -ForegroundColor White
    $index++
}

if ($programs.Count -eq 1) {
    $selected = $programs[0]
    Write-Host ""
    Write-Host "Désinstallation de: $($selected.DisplayName)" -ForegroundColor Yellow
    Write-Host "Commande: $($selected.UninstallString)" -ForegroundColor Gray
    
    $confirm = Read-Host "Confirmer la désinstallation? (O/N)"
    if ($confirm -eq "O" -or $confirm -eq "o") {
        $uninstallString = $selected.UninstallString
        if ($uninstallString -match '^"(.+)"') {
            $exe = $matches[1]
            $args = $uninstallString.Substring($matches[0].Length).Trim()
            Start-Process -FilePath $exe -ArgumentList $args -Wait
        } else {
            $parts = $uninstallString -split ' ', 2
            Start-Process -FilePath $parts[0] -ArgumentList $parts[1] -Wait
        }
        Write-Host "Désinstallation terminée." -ForegroundColor Green
    } else {
        Write-Host "Désinstallation annulée." -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    $choice = Read-Host "Sélectionnez le numéro du programme à désinstaller (1-$($programs.Count))"
    $selectedIndex = [int]$choice - 1
    if ($selectedIndex -ge 0 -and $selectedIndex -lt $programs.Count) {
        $selected = $programs[$selectedIndex]
        Write-Host ""
        Write-Host "Désinstallation de: $($selected.DisplayName)" -ForegroundColor Yellow
        
        $confirm = Read-Host "Confirmer la désinstallation? (O/N)"
        if ($confirm -eq "O" -or $confirm -eq "o") {
            $uninstallString = $selected.UninstallString
            if ($uninstallString -match '^"(.+)"') {
                $exe = $matches[1]
                $args = $uninstallString.Substring($matches[0].Length).Trim()
                Start-Process -FilePath $exe -ArgumentList $args -Wait
            } else {
                $parts = $uninstallString -split ' ', 2
                Start-Process -FilePath $parts[0] -ArgumentList $parts[1] -Wait
            }
            Write-Host "Désinstallation terminée." -ForegroundColor Green
        } else {
            Write-Host "Désinstallation annulée." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Choix invalide." -ForegroundColor Red
    }
}



