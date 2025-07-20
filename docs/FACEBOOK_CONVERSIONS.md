# Configuration Facebook Conversions API pour BoliBana

## Vue d'ensemble
Ce document explique comment configurer et utiliser l'API Conversions Facebook pour tracker les conversions sur BoliBana.

## Configuration

### 1. Configuration via l'interface d'administration
L'API Facebook Conversions utilise la configuration existante de `SiteConfiguration` :

1. **Accédez à l'administration Django** : `http://127.0.0.1:8000/bismillah/`
2. **Allez dans "Configuration du site"**
3. **Remplissez les champs Facebook :**
   - **Facebook Pixel ID** : ID de votre pixel Facebook
   - **Facebook Access Token** : Token d'accès pour l'API Conversions

### 2. Obtention des credentials

#### Facebook Pixel ID
1. Allez sur [Facebook Business Manager](https://business.facebook.com)
2. Créez un nouveau Pixel ou utilisez un existant
3. Copiez l'ID du Pixel

#### Facebook Access Token
1. Allez sur [Facebook Developers](https://developers.facebook.com)
2. Créez une nouvelle app ou utilisez une existante
3. Générez un token d'accès avec les permissions nécessaires :
   - `ads_management`
   - `ads_read`
   - `business_management`

## Utilisation

### 1. Événements disponibles

#### Purchase (Achat)
```python
from core.facebook_conversions import facebook_conversions

facebook_conversions.send_purchase_event(
    user_data={
        "email": "client@email.com",
        "phone": "+22312345678"
    },
    amount=50000,  # Montant en FCFA
    currency="XOF",
    content_name="Service Salam BoliBana"
)
```

#### Lead (Demande)
```python
facebook_conversions.send_lead_event(
    user_data={
        "email": "client@email.com",
        "phone": "+22312345678"
    },
    content_name="Comparateur de Prix Salam"
)
```

### 2. Intégration dans les vues

#### Succès de paiement
```python
def payment_success(request):
    # Traitement du paiement
    # ...
    
    # Tracking Facebook
    if request.user.is_authenticated:
        user_data = {
            "email": request.user.email,
            "phone": getattr(request.user, 'phone', '')
        }
        
        facebook_conversions.send_purchase_event(
            user_data=user_data,
            amount=cart_total,
            currency="XOF",
            content_name="Service Salam BoliBana"
        )
```

#### Comparateur de prix
```python
def check_price(request):
    if request.method == 'POST':
        # Traitement de la demande
        # ...
        
        # Tracking Facebook
        if request.user.is_authenticated:
            user_data = {
                "email": request.user.email,
                "phone": getattr(request.user, 'phone', '')
            }
            
            facebook_conversions.send_lead_event(
                user_data=user_data,
                content_name="Comparateur de Prix Salam"
            )
```

## Événements recommandés pour BoliBana

### Conversions principales
- **Purchase** : Client paie vos services d'intermédiation
- **Lead** : Demande de comparaison de prix
- **InitiateCheckout** : Début du processus de commande

### Événements d'engagement
- **ViewContent** : Consultation de produits
- **Search** : Recherche de prix
- **Contact** : Contact client

## Sécurité

### Hachage des données
Les données utilisateur sont automatiquement hachées :
- Email → SHA256
- Téléphone → SHA256 (nettoyé)

### Gestion des erreurs
- Logs automatiques des erreurs
- Pas d'interruption du flux utilisateur
- Fallback gracieux si l'API n'est pas configurée

## Test

### Mode développement
```python
# Les événements sont loggés mais pas envoyés si non configuré
facebook_conversions.send_purchase_event(...)
```

### Mode production
```python
# Vérifiez les logs pour confirmer l'envoi
# Les événements apparaissent dans Facebook Events Manager
```

## Dépannage

### Problèmes courants
1. **Token invalide** : Vérifiez le Facebook Access Token dans l'admin
2. **Pixel ID incorrect** : Vérifiez le Facebook Pixel ID dans l'admin
3. **Permissions manquantes** : Vérifiez les permissions de l'app Facebook

### Logs
Consultez les logs Django pour les erreurs :
```bash
tail -f logs/django.log | grep Facebook
```

## Avantages de cette approche

### ✅ **Intégration avec l'existant**
- Utilise la configuration `SiteConfiguration` existante
- Pas de variables d'environnement supplémentaires
- Configuration centralisée dans l'admin

### ✅ **Facilité de gestion**
- Modification via l'interface d'administration
- Pas besoin de redéployer pour changer les credentials
- Configuration visible et modifiable

### ✅ **Sécurité**
- Données stockées en base de données
- Accès contrôlé via l'admin
- Logs de configuration

## Ressources
- [Facebook Conversions API Documentation](https://developers.facebook.com/docs/marketing-api/conversions-api)
- [Facebook Business Manager](https://business.facebook.com)
- [Facebook Developers](https://developers.facebook.com) 