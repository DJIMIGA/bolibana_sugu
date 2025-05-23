# Configuration de l'Administration avec 2FA

## Vue d'ensemble
Ce document décrit la configuration de l'interface d'administration Django avec authentification à deux facteurs (2FA) pour SagaKore.

## Structure de l'Administration

### 1. Configuration de Base (accounts/admin.py)
```python
# Configuration de l'admin avec 2FA
class MyOTPAdminSite(OTPAdminSite):
    """
    Site d'administration personnalisé avec authentification à deux facteurs.
    """
    def has_permission(self, request):
        """
        Vérifie si l'utilisateur a la permission d'accéder à l'interface d'administration.
        """
        return super().has_permission(request) and request.user.is_verified()

# Création de l'instance du site d'administration 2FA
admin_site = MyOTPAdminSite(name='OTPAdmin')
```

### 2. Organisation des Modèles
Chaque application gère ses propres modèles dans son fichier `admin.py` :

#### accounts/admin.py
- Gère les modèles liés aux utilisateurs et à l'authentification
- Définit la configuration 2FA
- Enregistre les modèles : `Shopper`, `AllowedIP`, `TOTPDevice`

#### product/admin.py
- Gère les modèles liés aux produits
- Utilise l'instance `admin_site` pour l'enregistrement
- Enregistre les modèles : `Product`, `Category`, `Phone`, etc.

## Important : Différence entre admin.site.register et admin_site.register

### 1. Problème de Visibilité
```python
# ❌ Ne fonctionne PAS avec notre configuration 2FA
admin.site.register(MonModele)  # Enregistrement standard Django

# ✅ Fonctionne correctement avec notre configuration 2FA
admin_site.register(MonModele)  # Enregistrement dans notre interface sécurisée
```

### 2. Pourquoi cette Différence ?
- `admin.site.register` enregistre les modèles dans l'interface d'administration standard de Django
- `admin_site.register` enregistre les modèles dans notre interface personnalisée avec 2FA
- Comme nous utilisons notre propre instance `admin_site`, les enregistrements via `admin.site.register` ne sont pas visibles

### 3. Bonnes Pratiques
- Toujours utiliser `admin_site.register` pour l'enregistrement des modèles
- Éviter les enregistrements redondants via `admin.site.register`
- Centraliser les enregistrements dans la fonction `register_admin_models`

### 4. Exemple de Configuration Correcte
```python
# Dans le fichier admin.py de l'application
from accounts.admin import admin_site

# Configuration de la classe d'administration
class MonModeleAdmin(admin.ModelAdmin):
    # Configuration spécifique
    pass

# Enregistrement correct avec admin_site
admin_site.register(MonModele, MonModeleAdmin)
```

## Configuration des Modèles

### 1. Modèles Utilisateurs
```python
class ShopperAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        # Logging des informations de vérification OTP
        logger.debug(f"=== OTP DEBUG INFO ===")
        logger.debug(f"User: {request.user.email}")
        logger.debug(f"OTP verified: {request.user.is_verified()}")
        return super().has_module_permission(request)
```

### 2. Modèles Produits
```python
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_name', 'get_full_path', 'image_preview')
    list_filter = (CategoryLevelFilter, 'parent',)
    search_fields = ('name',)
    # ... autres configurations
```

## Sécurité

### 1. Vérification 2FA
- Tous les accès à l'administration nécessitent une vérification 2FA
- La vérification est gérée par le middleware OTP
- Les utilisateurs non vérifiés sont redirigés vers la page de vérification

### 2. Restrictions IP
- Les accès sont limités aux IPs autorisées
- La vérification IP est effectuée avant la vérification 2FA
- Les tentatives d'accès non autorisées sont journalisées

## Utilisation

### 1. Accès à l'Administration
1. Se connecter avec ses identifiants
2. Vérifier son identité via 2FA
3. Accéder à l'interface d'administration

### 2. Gestion des Modèles
- Chaque application gère ses propres modèles
- Les configurations sont centralisées dans les fichiers `admin.py` respectifs
- L'interface est sécurisée par 2FA

## Bonnes Pratiques

### 1. Organisation du Code
- Séparer les configurations par application
- Utiliser des classes d'administration personnalisées
- Documenter les configurations complexes

### 2. Sécurité
- Toujours vérifier les permissions
- Journaliser les accès et les modifications
- Maintenir à jour les listes d'IPs autorisées

### 3. Maintenance
- Vérifier régulièrement les logs
- Mettre à jour les configurations de sécurité
- Tester les accès après les modifications

## Dépannage

### 1. Problèmes d'Accès
- Vérifier la configuration 2FA
- Confirmer que l'IP est autorisée
- Consulter les logs pour plus de détails

### 2. Problèmes d'Affichage
- Vérifier les enregistrements des modèles
- Confirmer les permissions des utilisateurs
- Vérifier les configurations des classes d'administration

## Exemples de Configuration

### 1. Enregistrement d'un Modèle
```python
# Dans le fichier admin.py de l'application
from accounts.admin import admin_site

class MonModeleAdmin(admin.ModelAdmin):
    # Configuration spécifique
    pass

admin_site.register(MonModele, MonModeleAdmin)
```

### 2. Configuration des Permissions
```python
class MonModeleAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        # Vérifications personnalisées
        return super().has_module_permission(request)
```

## Ressources

### Documentation
- [Django Admin](https://docs.djangoproject.com/fr/5.1/ref/contrib/admin/)
- [Django OTP](https://django-otp.readthedocs.io/)
- [Django Security](https://docs.djangoproject.com/fr/5.1/topics/security/)

### Sécurité
- [OWASP Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Django_Security_Cheat_Sheet.html)
- [Best Practices for 2FA](https://www.owasp.org/index.php/Multifactor_Authentication_Cheat_Sheet) 