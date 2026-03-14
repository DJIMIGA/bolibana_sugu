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

## Configuration par Fichier

### 1. settings.py
```python
# Applications requises
INSTALLED_APPS = [
    # ...
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
]

# Middleware
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

# Configuration du logging pour OTP
LOGGING = {
    'handlers': {
        'otp_file': {
            'class': 'logging.FileHandler',
            'filename': 'otp_debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'accounts.admin': {
            'handlers': ['console', 'otp_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### 2. urls.py
```python
from django_otp.admin import OTPAdminSite
from django.contrib import admin

# Configuration de l'admin sécurisé
admin.site.__class__ = OTPAdminSite

urlpatterns = [
    path(f'{settings.ADMIN_URL}', admin.site.urls),
    # ... autres URLs
]
```

### 3. admin.py
```python
from django.contrib import admin
from django_otp.admin import OTPAdminSite
from .models import Shopper

class MyOTPAdminSite(OTPAdminSite):
    def has_permission(self, request):
        if not super().has_permission(request):
            return False
        return request.user.is_verified()

# Enregistrement des modèles
admin.site.register(Shopper)
```

### 4. models.py
```python
from django.contrib.auth.models import AbstractUser
from django_otp.models import Device

class Shopper(AbstractUser):
    # Champs personnalisés
    pass

class SagaDevice(Device):
    # Configuration du device OTP
    pass
```

### 5. middleware.py
```python
from django.conf import settings
from django.http import HttpResponseForbidden
from ipaddress import ip_address, ip_network

class AdminIPRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(f'/{settings.ADMIN_URL}'):
            client_ip = self.get_client_ip(request)
            if not self.is_ip_allowed(client_ip):
                return HttpResponseForbidden('Accès non autorisé')
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def is_ip_allowed(self, client_ip):
        try:
            client_ip = ip_address(client_ip)
            return any(
                client_ip in ip_network(allowed_ip)
                for allowed_ip in settings.ADMIN_ALLOWED_IPS
            )
        except ValueError:
            return False
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

## Sécurité

### Protection de l'Admin
- URL personnalisée : `s3cur3d4dm1n-p4n3l-2024/`
- Vérification OTP obligatoire
- Protection contre les accès non autorisés
- Restriction des IPs autorisées

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