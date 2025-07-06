# Configuration des Webhooks Stripe - SagaKore

## 📋 Vue d'ensemble

Ce document détaille la configuration et l'utilisation des webhooks Stripe pour gérer les paiements en temps réel dans SagaKore.

**⚠️ IMPORTANT :** Le système de commandes mixtes a été fusionné avec le système unifié. Toutes les commandes (Salam, Classiques, Mixtes) utilisent maintenant la même fonction `create_checkout_session` et les mêmes endpoints de paiement.

## 🎯 Cas d'usage des webhooks

### ✅ Quand utiliser la vue webhook

1. **Environnement de production**
   - Application déployée sur serveur public (VPS, Heroku, AWS)
   - Stripe peut joindre directement l'endpoint via HTTPS
   - URL : `https://sagakore.com/cart/stripe/webhook/`

2. **Développement local avec Stripe CLI**
   - Développement en local avec `stripe listen`
   - Stripe CLI fait le pont entre Stripe et localhost
   - URL : `http://localhost:8000/cart/stripe/webhook/`

3. **Tests avec ngrok (alternative)**
   - Alternative à Stripe CLI pour exposer localhost
   - URL : `https://ton-tunnel.ngrok.io/cart/stripe/webhook/`

### ❌ Quand NE PAS utiliser la vue webhook

1. **Tests unitaires** - Utiliser des mocks Stripe
2. **Développement sans Stripe CLI** - Utiliser `payment_success` en fallback
3. **Environnements sans HTTPS** - Stripe CLI requis pour localhost
   - URL : `https://abc123.ngrok.io/stripe/webhook/`

### ❌ Quand NE PAS utiliser la vue webhook

1. **Développement local sans tunnel**
   - Stripe ne peut pas joindre `localhost:8000`
   - Résultat : Aucun webhook reçu

2. **Tests unitaires**
   - Utiliser `stripe trigger` ou des mocks
   - Pas besoin d'un vrai serveur web

## 🛠️ Installation et configuration

### 1. Installation de Stripe CLI

```bash
# Windows (avec Chocolatey)
choco install stripe-cli

# Ou téléchargement direct
# https://stripe.com/docs/stripe-cli
```

### 2. Authentification Stripe CLI

```bash
stripe login
```

**En cas d'erreur d'authentification :**
```bash
# Déconnecter la session expirée
stripe logout

# Se reconnecter
stripe login

# Vérifier la configuration
stripe config --list
```

**Si la clé API a expiré :**
1. Aller sur [dashboard.stripe.com](https://dashboard.stripe.com)
2. Naviguer vers **Developers > API keys**
3. Vérifier que les clés de test sont actives
4. Régénérer une nouvelle clé si nécessaire

### 3. Configuration des variables d'environnement

```python
# settings.py
if DEBUG:
    # Développement local
    STRIPE_WEBHOOK_SECRET = 'whsec_xxx'  # Clé Stripe CLI
    WEBHOOK_URL = 'http://localhost:8000/cart/stripe/webhook/'
else:
    # Production
    STRIPE_WEBHOOK_SECRET = 'whsec_yyy'  # Clé production
    WEBHOOK_URL = 'https://sagakore.com/stripe/webhook/'
```

## 🚀 Workflow de développement

### Phase 1 : Développement local

1. **Lancer le serveur Django**
   ```bash
   python manage.py runserver
   ```

2. **Lancer Stripe CLI**
   ```bash
   stripe listen --forward-to localhost:8000/cart/stripe/webhook/
   ```

3. **Noter la clé de signature**
   ```
   Ready! Your webhook signing secret is whsec_1234567890abcdef...
   ```

4. **Configurer la clé dans Django**
   ```python
   STRIPE_WEBHOOK_SECRET = 'whsec_1234567890abcdef...'
   ```

5. **Tester les paiements**
   - Effectuer un paiement depuis l'application
   - Observer les événements dans la console Stripe CLI

### Phase 2 : Tests en staging

1. Déployer sur serveur de test
2. Configurer l'URL de staging dans le dashboard Stripe
3. Tester les webhooks en conditions réelles

### Phase 3 : Production

1. Déployer en production
2. Configurer l'URL de production dans le dashboard Stripe
3. Activer les webhooks pour les événements critiques

## 📊 Événements webhook

### Événements obligatoires (e-commerce)

```python
WEBHOOK_EVENTS_CRITICAL = [
    'checkout.session.completed',    # Paiement réussi
    'payment_intent.succeeded',      # Paiement confirmé
    'payment_intent.payment_failed', # Paiement échoué
    'invoice.payment_succeeded',     # Facture payée
    'customer.subscription.created', # Abonnement créé
]
```

### Événements optionnels

```python
WEBHOOK_EVENTS_OPTIONAL = [
    'customer.created',              # Nouveau client
    'customer.updated',              # Client modifié
    'charge.refunded',               # Remboursement
    'dispute.created',               # Contestation
    'account.updated',               # Compte mis à jour
]
```

## 🔧 Commandes Stripe CLI utiles

### Écouter les événements
```bash
# Écouter tous les événements
stripe listen --forward-to localhost:8000/cart/stripe/webhook/

# Écouter des événements spécifiques
stripe listen --forward-to localhost:8000/cart/stripe/webhook/ --events checkout.session.completed,payment_intent.succeeded

# Afficher les détails complets
stripe listen --forward-to localhost:8000/cart/stripe/webhook/ --print-secret

# Sauvegarder les événements
stripe listen --forward-to localhost:8000/cart/stripe/webhook/ --save-events
```

### Tester les événements
```bash
# Simuler un événement
stripe trigger checkout.session.completed

# Voir l'historique des événements
stripe events list

# Voir les détails d'un événement
stripe events retrieve evt_1234567890
```

## 🐛 Débogage

### 1. Vérifier la réception des webhooks

```python
def stripe_webhook(request):
    print(f"Webhook reçu: {request.method} {request.path}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Body: {request.body[:200]}...")  # Premiers 200 caractères
    # ... suite du code
```

### 2. Exemple de sortie Stripe CLI

```bash
> Ready! Your webhook signing secret is whsec_1234567890abcdef...

2024-01-15 10:30:45   --> checkout.session.completed [evt_1ABC123...]
2024-01-15 10:30:45  <--  [200] POST http://localhost:8000/cart/stripe/webhook/ [evt_1ABC123...]
2024-01-15 10:30:46   --> payment_intent.succeeded [evt_1DEF456...]
2024-01-15 10:30:46  <--  [200] POST http://localhost:8000/cart/stripe/webhook/ [evt_1DEF456...]
```

### 3. Codes de statut HTTP

- **200** : Webhook traité avec succès
- **400** : Erreur de validation (signature, format)
- **500** : Erreur interne du serveur

## 🔒 Sécurité

### 1. Validation de signature

```python
import stripe
from django.conf import settings

def verify_webhook_signature(payload, sig_header, secret):
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, secret
        )
        return event
    except ValueError as e:
        # Payload invalide
        raise ValueError('Invalid payload')
    except stripe.error.SignatureVerificationError as e:
        # Signature invalide
        raise ValueError('Invalid signature')
```

### 2. Variables d'environnement

```bash
# .env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## 🏪 Logique métier : Produits Salam vs Classiques

### **Produits Salam** 🧕
- **Gestion de stock** : ❌ Aucune gestion de stock
- **Quantités** : Illimitées
- **Traitement** : Immédiat, sans vérification
- **Comportement webhook** : Supprime seulement les Salam du panier
- **Logique** : Commande spéciale, livraison selon méthode configurée

### **Produits Classiques** 📱
- **Gestion de stock** : ✅ Gestion complète du stock
- **Quantités** : Limitées selon `product.stock`
- **Traitement** : Vérification et réservation du stock
- **Comportement webhook** : Supprime tous les produits traités
- **Logique** : Stock réservé lors de la commande, déduit du stock disponible

### **Commandes Mixtes** 🔄
- **Détection automatique** : Le système détecte automatiquement les paniers mixtes
- **Traitement unifié** : Une seule fonction `create_checkout_session` gère tous les types
- **Logique hybride** : Salam (pas de stock) + Classiques (avec stock)
- **Avantages** : Code DRY, maintenance simplifiée, cohérence

### **Différence dans le webhook**
```python
# Salam : Pas de gestion de stock
cart.cart_items.filter(product__is_salam=True).delete()

# Classiques : Gestion de stock complète
if item.product.can_order(item.quantity):
    item.product.reserve_stock(item.quantity)
    # Créer l'item de commande
cart.cart_items.all().delete()
```

### **Pourquoi cette distinction ?**
- **Salam** : Produits commandés sur mesure, pas de stock physique
- **Classiques** : Produits en stock, gestion d'inventaire nécessaire
- **Flexibilité** : Permet de traiter les Salam séparément des autres produits

## 📝 Logs et monitoring

### 1. Configuration des logs

```python
import logging

logger = logging.getLogger(__name__)

def stripe_webhook(request):
    logger.info("Webhook Stripe reçu")
    try:
        # Traitement du webhook
        logger.info("Webhook traité avec succès")
    except Exception as e:
        logger.error(f"Erreur webhook: {e}")
        return HttpResponse(status=500)
```

### 2. Fichier de log dédié

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'stripe_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/stripe_webhooks.log',
        },
    },
    'loggers': {
        'stripe_webhooks': {
            'handlers': ['stripe_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🚨 Problèmes courants

### 1. Aucun webhook reçu

**Causes possibles :**
- Pas de tunnel (Stripe CLI ou ngrok)
- URL incorrecte dans le dashboard Stripe
- Firewall ou problème réseau
- Code webhook ne logge rien

**Solutions :**
- Vérifier que Stripe CLI est lancé
- Tester avec `stripe trigger`
- Vérifier les logs Django

### 2. Erreur de signature

**Causes possibles :**
- Mauvaise clé webhook
- Payload modifié
- Headers manquants

**Solutions :**
- Vérifier la clé dans les variables d'environnement
- Utiliser la bonne clé (CLI vs production)

### 3. Timeout du webhook

**Causes possibles :**
- Traitement trop long
- Base de données lente
- Requêtes externes

**Solutions :**
- Traitement asynchrone
- Optimisation des requêtes
- Timeout approprié

## 📚 Ressources

- [Documentation Stripe Webhooks](https://stripe.com/docs/webhooks)
- [Stripe CLI Documentation](https://stripe.com/docs/stripe-cli)
- [Django Stripe Integration](https://stripe.com/docs/checkout/django)

## 🔄 Mise à jour

Ce document doit être mis à jour à chaque modification de la configuration webhook ou ajout de nouveaux événements.

---

**Note :** Ce README est spécifique au projet SagaKore et doit être adapté selon les besoins spécifiques de l'application. 