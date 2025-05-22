# Configuration 2FA pour SagaKore

## Vue d'ensemble
Ce document décrit l'implémentation de l'authentification à deux facteurs (2FA) dans le projet SagaKore, utilisant `django-otp` et le plugin `otp_totp`.

## Prérequis
- Python 3.8+
- Django 5.1+
- django-otp
- django-otp-totp

## Installation

1. **Installation des dépendances**
```bash
pip install django-otp django-otp-totp
```

2. **Configuration dans settings.py**
```python
INSTALLED_APPS = [
    # ...
    'django_otp',
    'django_otp.plugins.otp_totp',
]

MIDDLEWARE = [
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',  # Doit être après AuthenticationMiddleware
]

# Configuration OTP
OTP_TOTP_ISSUER = 'SagaKore'
OTP_LOGIN_URL = f'/{ADMIN_URL}login/'
OTP_ADMIN_ENABLED = True
OTP_ENFORCE_ADMIN = True
OTP_ENFORCE_GLOBAL = True
OTP_REQUIRED = True
OTP_ADMIN_REQUIRED = True
```

## Structure du Projet

### Modèles
- `Shopper` : Modèle utilisateur personnalisé
- `SagaDevice` : Modèle abstrait pour les devices OTP
- `TOTPDevice` : Modèle pour l'authentification TOTP

### Administration
```python
class MyOTPAdminSite(OTPAdminSite):
    def has_permission(self, request):
        if not super().has_permission(request):
            return False
        return request.user.is_verified()
```

## Utilisation

### 1. Configuration Initiale
1. Se connecter à l'interface d'administration
2. Accéder à la section "TOTP Devices"
3. Ajouter un nouveau device TOTP
4. Scanner le QR code avec Google Authenticator

### 2. Processus d'Authentification
1. Connexion avec identifiants habituels
2. Saisie du code TOTP généré par l'application
3. Accès à l'interface d'administration si le code est valide

### 3. Gestion des Devices
- Ajout de nouveaux devices
- Désactivation de devices existants
- Réinitialisation en cas de perte

## Sécurité

### Protection de l'Admin
- URL personnalisée : `s3cur3d4dm1n-p4n3l-2024/`
- Vérification OTP obligatoire
- Protection contre les accès non autorisés

### Bonnes Pratiques
1. **Pour les Administrateurs**
   - Utiliser des mots de passe forts
   - Activer la 2FA immédiatement
   - Conserver les codes de secours
   - Ne pas partager les appareils d'authentification

2. **Pour les Développeurs**
   - Vérifier la configuration du middleware
   - Tester la 2FA en mode développement
   - Maintenir les logs de sécurité

## Dépannage

### Problèmes Courants
1. **Code TOTP non accepté**
   - Vérifier la synchronisation de l'horloge
   - S'assurer que le code est entré dans le délai de 30 secondes
   - Vérifier que le device est actif

2. **Accès Admin refusé**
   - Vérifier que l'utilisateur est vérifié OTP
   - Confirmer les permissions utilisateur
   - Vérifier les logs de sécurité

### Logs
Les logs de vérification OTP sont disponibles dans :
- `otp_debug.log` pour les informations détaillées
- Configuration du logging dans `settings.py`

## Maintenance

### Mise à Jour
1. Vérifier les mises à jour de django-otp
2. Tester la configuration après mise à jour
3. Sauvegarder les données des devices

### Surveillance
1. Vérifier régulièrement les logs
2. Surveiller les tentatives d'accès
3. Maintenir la liste des devices actifs

## Ressources

### Documentation
- [Documentation django-otp](https://django-otp.readthedocs.io/)
- [Guide TOTP](https://django-otp.readthedocs.io/en/stable/ref/plugins/otp_totp.html)

### Sécurité
- [OWASP 2FA](https://www.owasp.org/index.php/Multifactor_Authentication_Cheat_Sheet)
- [Meilleures pratiques Django](https://docs.djangoproject.com/fr/5.1/topics/security/)

## Support

Pour toute question ou problème :
1. Consulter les logs dans `otp_debug.log`
2. Vérifier la documentation officielle
3. Contacter l'équipe de développement

## Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails. 