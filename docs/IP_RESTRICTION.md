# Restriction des IPs pour SagaKore

## Vue d'ensemble
Ce document décrit la configuration de la restriction des IPs pour l'accès à l'interface d'administration de SagaKore.

## Configuration par Fichier

### 1. settings.py
```python
# Liste des IPs autorisées pour l'accès admin
ADMIN_ALLOWED_IPS = os.getenv('ADMIN_ALLOWED_IPS', '127.0.0.1').split(',')

# Middleware pour la restriction IP
MIDDLEWARE = [
    # ...
    'saga.middleware.AdminIPRestrictionMiddleware',
]
```

### 2. middleware.py
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

### 1. Configuration des IPs
- Ajoutez les IPs autorisées dans la variable d'environnement `ADMIN_ALLOWED_IPS`
- Utilisez la notation CIDR pour les plages d'IPs
- Exemple : `192.168.1.0/24` pour tout le réseau 192.168.1.x

### 2. Vérification des IPs
- Le middleware vérifie automatiquement l'IP du client
- Les requêtes provenant d'IPs non autorisées sont rejetées
- Les logs de tentatives d'accès sont enregistrés

## Sécurité

### Bonnes Pratiques
1. **Configuration**
   - Utilisez toujours HTTPS en production
   - Mettez à jour régulièrement la liste des IPs autorisées
   - Surveillez les logs pour détecter les tentatives d'accès non autorisées

2. **Gestion des IPs**
   - Limitez le nombre d'IPs autorisées
   - Utilisez des plages d'IPs spécifiques plutôt que des plages larges
   - Documentez chaque IP autorisée et sa raison d'être

## Dépannage

### 1. Problèmes d'Accès
- Vérifier que l'IP est correctement listée dans `ADMIN_ALLOWED_IPS`
- Confirmer que le middleware est correctement configuré
- Vérifier les logs pour les erreurs de restriction IP

### 2. Problèmes de Proxy
- Si vous utilisez un proxy, assurez-vous que `X-Forwarded-For` est correctement configuré
- Vérifiez que l'IP réelle du client est bien transmise

### 3. Logs
- Les tentatives d'accès non autorisées sont enregistrées dans les logs
- Surveillez régulièrement les logs pour détecter les tentatives d'intrusion

## Exemples de Configuration

### 1. IP Unique
```bash
ADMIN_ALLOWED_IPS=192.168.1.100
```

### 2. Plage d'IPs
```bash
ADMIN_ALLOWED_IPS=192.168.1.0/24
```

### 3. Multiples IPs
```bash
ADMIN_ALLOWED_IPS=192.168.1.100,10.0.0.50,172.16.0.0/24
```

## Maintenance

### 1. Mise à Jour des IPs
- Réviser régulièrement la liste des IPs autorisées
- Supprimer les IPs qui ne sont plus nécessaires
- Documenter les changements dans les logs

### 2. Surveillance
- Surveiller les tentatives d'accès non autorisées
- Mettre en place des alertes pour les tentatives suspectes
- Maintenir un journal des modifications d'IPs

## Ressources

### Documentation
- [Django Security](https://docs.djangoproject.com/fr/5.1/topics/security/)
- [IP Address Module Python](https://docs.python.org/3/library/ipaddress.html)

### Sécurité
- [OWASP Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Django_Security_Cheat_Sheet.html)
- [Best Practices for IP Restriction](https://www.owasp.org/index.php/Restrict_IP_Access)

## Support

Pour toute question ou problème :
1. Consulter les logs de sécurité
2. Vérifier la configuration du middleware
3. Contacter l'équipe de développement 

## Gestion des IPs Dynamiques en Production

### 1. Utilisation d'un Service DNS Dynamique
```python
# settings.py
import socket
import requests

def get_current_ip():
    try:
        # Utiliser un service externe pour obtenir l'IP publique
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except:
        return None

# Mise à jour automatique des IPs autorisées
CURRENT_IP = get_current_ip()
if CURRENT_IP:
    ADMIN_ALLOWED_IPS = [CURRENT_IP] + os.getenv('ADMIN_ALLOWED_IPS', '127.0.0.1').split(',')
```

### 2. Script de Mise à Jour Automatique
```python
# scripts/update_allowed_ips.py
import os
import requests
import django
from django.conf import settings

def update_allowed_ips():
    try:
        # Obtenir l'IP actuelle
        response = requests.get('https://api.ipify.org?format=json')
        current_ip = response.json()['ip']
        
        # Mettre à jour la variable d'environnement
        os.environ['ADMIN_ALLOWED_IPS'] = current_ip
        
        # Recharger la configuration Django
        django.setup()
        
        print(f"IP mise à jour : {current_ip}")
    except Exception as e:
        print(f"Erreur lors de la mise à jour : {str(e)}")

if __name__ == "__main__":
    update_allowed_ips()
```

### 3. Configuration avec Cron
```bash
# /etc/cron.d/update-allowed-ips
# Mise à jour toutes les heures
0 * * * * /usr/bin/python3 /chemin/vers/scripts/update_allowed_ips.py >> /var/log/ip-updates.log 2>&1
```

### 4. Utilisation d'un Service de Proxy
```python
# settings.py
PROXY_HEADERS = {
    'HTTP_X_FORWARDED_FOR': True,
    'HTTP_X_REAL_IP': True,
}

# middleware.py
class AdminIPRestrictionMiddleware:
    def get_client_ip(self, request):
        for header in settings.PROXY_HEADERS:
            if header in request.META:
                return request.META[header].split(',')[0]
        return request.META.get('REMOTE_ADDR')
```

### 5. Gestion des IPs via l'Interface d'Administration
```python
# models.py
from django.db import models

class AllowedIP(models.Model):
    ip_address = models.GenericIPAddressField()
    description = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "IP Autorisée"
        verbose_name_plural = "IPs Autorisées"

# admin.py
from django.contrib import admin
from .models import AllowedIP

@admin.register(AllowedIP)
class AllowedIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'description', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('ip_address', 'description')
```

### 6. Bonnes Pratiques pour les IPs Dynamiques

1. **Surveillance**
   - Mettre en place des alertes pour les changements d'IP
   - Conserver un historique des IPs utilisées
   - Vérifier régulièrement les logs d'accès

2. **Sécurité**
   - Limiter la durée de validité des IPs dynamiques
   - Implémenter un système de validation par email lors des changements d'IP
   - Utiliser des services de géolocalisation pour vérifier la légitimité des IPs

3. **Backup**
   - Maintenir une liste d'IPs de secours
   - Avoir un accès alternatif en cas de problème
   - Documenter la procédure de récupération d'accès

### 7. Exemple de Configuration Heroku
```bash
# Procfile
web: python manage.py runserver 0.0.0.0:$PORT
worker: python scripts/update_allowed_ips.py

# Config Vars Heroku
ADMIN_ALLOWED_IPS=current_ip,backup_ip1,backup_ip2
```

### 8. Script de Vérification
```python
# scripts/verify_ip_access.py
import requests
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_admin_access():
    try:
        response = requests.get('https://votre-site.com/admin/')
        if response.status_code == 200:
            logger.info("Accès admin OK")
            return True
        else:
            logger.error(f"Erreur d'accès: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Erreur de vérification: {str(e)}")
        return False

if __name__ == "__main__":
    if not verify_admin_access():
        sys.exit(1)
```

## Dépannage des IPs Dynamiques

### 1. Problèmes Courants
- IP non mise à jour automatiquement
- Accès refusé après changement d'IP
- Problèmes de proxy ou de VPN

### 2. Solutions
1. **Vérification Manuelle**
   ```bash
   curl https://api.ipify.org?format=json
   ```

2. **Test d'Accès**
   ```bash
   curl -I https://votre-site.com/admin/
   ```

3. **Vérification des Logs**
   ```bash
   tail -f /var/log/ip-updates.log
   ```

### 3. Procédure de Récupération
1. Vérifier l'IP actuelle
2. Mettre à jour manuellement si nécessaire
3. Tester l'accès
4. Documenter l'incident 

## Gestion des IPs : Configuration vs Base de Données

### 1. Configuration dans settings.py
```python
# Liste des IPs autorisées pour l'accès admin
ADMIN_ALLOWED_IPS = [
    '127.0.0.1',  # Localhost
    '192.168.1.0/24',  # Réseau local
    # Autres IPs critiques
]
```

### 2. Gestion dans la Base de Données
```python
# models.py
class AllowedIP(models.Model):
    ip_address = models.GenericIPAddressField(verbose_name="Adresse IP")
    description = models.CharField(max_length=200, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")
    last_used = models.DateTimeField(null=True, blank=True, verbose_name="Dernière utilisation")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Expire le")
    added_by = models.ForeignKey('Shopper', on_delete=models.SET_NULL, null=True, verbose_name="Ajouté par")
```

### 3. Priorité et Vérification

Le système utilise une approche à deux niveaux pour la vérification des IPs :

1. **Vérification Primaires (settings.py)**
   - Les IPs définies dans `settings.py` sont vérifiées en premier
   - Ces IPs ont la priorité la plus haute
   - Idéal pour les IPs critiques et de secours

2. **Vérification Secondaire (Base de Données)**
   - Si l'IP n'est pas trouvée dans `settings.py`, la base de données est consultée
   - Permet une gestion dynamique des IPs
   - Supporte les dates d'expiration et le suivi d'utilisation

### 4. Logs et Surveillance

Le système enregistre des logs détaillés pour chaque vérification :
```python
# Exemple de logs
"IP 192.168.1.100 autorisée via configuration"
"IP 10.0.0.50 autorisée via base de données"
"Tentative d'accès non autorisé depuis l'IP: 172.16.0.100"
```

### 5. Gestion des Erreurs

Le système gère plusieurs scénarios d'erreur :

1. **Erreur de Base de Données**
   - Si la base de données est inaccessible, le système continue avec les IPs de configuration
   - Les erreurs sont enregistrées dans les logs

2. **IP Invalide**
   - Les IPs mal formatées sont rejetées
   - Les erreurs de validation sont enregistrées

3. **Expiration**
   - Les IPs expirées sont automatiquement ignorées
   - La dernière utilisation est mise à jour

### 6. Bonnes Pratiques

1. **Configuration**
   - Garder les IPs critiques dans `settings.py`
   - Utiliser la base de données pour les IPs temporaires
   - Documenter chaque IP et sa raison d'être

2. **Sécurité**
   - Limiter le nombre d'IPs dans `settings.py`
   - Mettre en place des dates d'expiration
   - Surveiller régulièrement les logs

3. **Maintenance**
   - Nettoyer régulièrement les IPs expirées
   - Vérifier les logs pour les tentatives suspectes
   - Mettre à jour la documentation

### 7. Exemple d'Utilisation

```python
# settings.py
ADMIN_ALLOWED_IPS = [
    '127.0.0.1',  # Développement local
    '192.168.1.0/24',  # Réseau interne
    '10.0.0.50',  # Serveur de production
]

# Interface d'administration
# - Ajouter une nouvelle IP temporaire
# - Définir une date d'expiration
# - Ajouter une description
```

### 8. Dépannage

1. **Vérification des IPs**
   ```bash
   # Vérifier l'IP actuelle
   curl https://api.ipify.org?format=json
   
   # Vérifier l'accès
   curl -I https://votre-site.com/admin/
   ```

2. **Vérification des Logs**
   ```bash
   # Voir les tentatives d'accès
   tail -f /var/log/admin_access.log
   ```

3. **Vérification de la Configuration**
   ```python
   # Vérifier les IPs autorisées
   from django.conf import settings
   print(settings.ADMIN_ALLOWED_IPS)
   ``` 