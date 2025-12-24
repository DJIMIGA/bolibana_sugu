# Guide de Désinstallation des Programmes Windows

## 📋 Méthodes pour Lister les Programmes

### Méthode 1 : Script PowerShell (Recommandé)
```powershell
.\list_programs.ps1
```
Ce script génère :
- Une liste complète des programmes installés
- Un fichier CSV avec tous les détails
- Une liste des programmes potentiellement inutilisés (installés il y a plus de 6 mois)

### Méthode 2 : Interface Windows
1. Ouvrir **Paramètres** (Windows + I)
2. Aller dans **Applications** > **Applications et fonctionnalités**
3. Utiliser la barre de recherche pour filtrer

### Méthode 3 : Panneau de configuration classique
```powershell
appwiz.cpl
```
Ou via Exécuter (Windows + R) : `appwiz.cpl`

## 🗑️ Méthodes pour Supprimer les Programmes

### Méthode 1 : Script PowerShell (Pour un programme spécifique)
```powershell
.\uninstall_program.ps1 -ProgramName "Nom du programme"
```
Exemple :
```powershell
.\uninstall_program.ps1 -ProgramName "Python 3.9"
```

### Méthode 2 : Interface Windows (Recommandé)
1. **Paramètres** > **Applications** > **Applications et fonctionnalités**
2. Rechercher le programme
3. Cliquer sur **Désinstaller**

### Méthode 3 : Via PowerShell (Commande directe)
```powershell
# Lister les programmes avec leur nom exact
Get-AppxPackage | Select-Object Name, PackageFullName

# Désinstaller un package Windows Store
Remove-AppxPackage -Package "NomDuPackage"
```

### Méthode 4 : Via le registre (Avancé)
```powershell
# Trouver la clé de désinstallation
Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*" | 
    Where-Object {$_.DisplayName -like "*NomDuProgramme*"} | 
    Select-Object DisplayName, UninstallString
```

## ⚠️ Programmes à NE PAS Supprimer

- **Microsoft Visual C++ Redistributables** : Nécessaires pour de nombreux programmes
- **Microsoft Edge WebView2** : Utilisé par de nombreuses applications modernes
- **Windows Subsystem for Linux** : Si vous utilisez WSL
- **Drivers système** : Acer Jumpstart, etc.

## 🔍 Identification des Programmes Inutilisés

### Critères d'identification :
1. **Date d'installation** : Plus de 6 mois sans utilisation
2. **Taille** : Programmes volumineux non utilisés
3. **Fréquence d'utilisation** : Vérifier dans le Gestionnaire des tâches

### Programmes souvent inutilisés :
- **Anciennes versions de Python** : Garder uniquement la version active
- **Programmes d'essai** : Soda PDF si vous ne l'utilisez plus
- **Outils de développement obsolètes** : Anciennes versions d'IDE
- **Plugins OBS** : Si vous n'utilisez plus OBS

## 📊 Analyse Recommandée

1. **Exécuter le script de liste** pour obtenir un aperçu complet
2. **Examiner le fichier CSV** généré
3. **Identifier les doublons** (ex: plusieurs versions de Python)
4. **Vérifier l'utilisation** avant de supprimer
5. **Sauvegarder** avant de supprimer des programmes système

## 🛠️ Nettoyage Recommandé pour Votre Système

Basé sur votre liste actuelle :

### À considérer pour suppression :
- **Python 3.9.4** et **Python 3.10.5** : Si vous utilisez uniquement Python 3.12.4
- **Soda PDF Desktop 14** : Si vous ne l'utilisez plus
- **Acer Jumpstart** : Bloatware souvent inutile
- **ExpressVPN** : Si vous ne l'utilisez plus

### À garder absolument :
- **Node.js** : Pour votre projet React Native
- **Python 3.12.4** : Version active
- **Git** : Essentiel pour le développement
- **Docker Desktop** : Pour la containerisation
- **PostgreSQL 15** : Base de données de votre projet
- **Android Studio** : Pour le développement mobile

## 🔒 Sécurité

- Toujours vérifier avant de supprimer
- Ne pas supprimer les programmes Microsoft essentiels
- Faire une sauvegarde système avant un nettoyage massif
- Utiliser la restauration système si nécessaire


