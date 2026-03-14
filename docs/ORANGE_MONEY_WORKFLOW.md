# Workflow Orange Money - SagaKore

## 📋 Vue d'ensemble du système

Le service Orange Money de SagaKore permet aux utilisateurs de payer leurs commandes via l'API Orange Money Web Payment. Voici le workflow complet et détaillé.

## 🔄 Workflow complet Orange Money

### 1. **Configuration et Initialisation**

#### Variables d'environnement requises :
```bash
ORANGE_MONEY_ENABLED=True
ORANGE_MONEY_ENV=dev  # ou 'prod'
ORANGE_MONEY_MERCHANT_KEY=your_merchant_key
ORANGE_MONEY_CLIENT_ID=your_client_id
ORANGE_MONEY_CLIENT_SECRET=your_client_secret
ORANGE_MONEY_CURRENCY=OUV  # OUV pour dev, XOF pour prod
ORANGE_MONEY_LANGUAGE=fr
ORANGE_MONEY_TIMEOUT=600
ORANGE_MONEY_MAX_RETRIES=3

# URLs de callback (obligatoires pour les webhooks)
ORANGE_MONEY_NOTIFICATION_URL=https://your-domain.com/cart/orange-money/webhook/
ORANGE_MONEY_RETURN_URL=https://your-domain.com/cart/orange-money/return/
ORANGE_MONEY_CANCEL_URL=https://your-domain.com/cart/orange-money/cancel/
```

#### URLs API selon l'environnement :
- **Développement** :
  - Base URL: `https://api.orange.com`
  - Payment URL: `https://webpayment-qualif.orange-money.com`
  - WebPayment API: `https://api.orange.com/orange-money-webpay/dev/v1/webpayment`
  - Status API: `https://api.orange.com/orange-money-webpay/dev/v1/transactionstatus`

- **Production** :
  - Base URL: `https://api.orange.com`
  - Payment URL: `https://webpayment.orange-money.com`
  - WebPayment API: `https://api.orange.com/orange-money-webpay/v1/webpayment`
  - Status API: `https://api.orange.com/orange-money-webpay/v1/transactionstatus`

### 2. **Processus de Paiement - Flux Détaillé**

#### **Étape 1 : Initiation du Paiement**
```
Utilisateur → SagaKore → Orange Money API
```

1. **Vérification de la configuration** :
   - `OrangeMoneyService.is_enabled()` vérifie que tous les credentials sont présents
   - Validation du panier et du stock
   - Création d'une commande temporaire avec statut `PENDING`

2. **Authentification OAuth2** :
   - Génération d'un token d'accès via `client_credentials`
   - Headers : `Authorization: Basic {base64(client_id:client_secret)}`
   - Endpoint : `POST /oauth/v3/token`
   - Le token est mis en cache pour éviter les appels répétés

#### **Étape 2 : Création de la Session de Paiement**
```python
# Données envoyées à Orange Money
order_data = {
    'merchant_key': config['merchant_key'],
    'currency': config['currency'],  # OUV ou XOF
    'order_id': order.order_number,
    'amount': amount_in_cents,  # Montant en centimes
    'return_url': 'https://your-domain.com/cart/orange-money/return/',
    'cancel_url': 'https://your-domain.com/cart/orange-money/cancel/',
    'notif_url': 'https://your-domain.com/cart/orange-money/webhook/',
    'lang': 'fr',
    'reference': f'SagaKore-{order.order_number}'
}
```

3. **Appel API de création de session** :
   - Endpoint : `POST /orange-money-webpay/dev/v1/webpayment`
   - Headers : `Authorization: Bearer {access_token}`
   - Réponse attendue :
   ```json
   {
     "pay_token": "abc123...",
     "notif_token": "xyz789...",
     "status": "PENDING"
   }
   ```

4. **Stockage des tokens** :
   - `pay_token` et `notif_token` stockés en session Django
   - `order_id` sauvegardé pour le suivi

#### **Étape 3 : Redirection vers Orange Money**
```
SagaKore → Orange Money Payment Page
```

5. **Construction de l'URL de paiement** :
   - URL : `{payment_url}/payment/pay_token/{pay_token}`
   - Redirection automatique de l'utilisateur

6. **Interface Orange Money** :
   - L'utilisateur saisit son numéro de téléphone
   - Réception et saisie du code OTP
   - Confirmation du paiement

### 3. **Gestion des Retours et Webhooks**

#### **Retour Utilisateur (Return URL)**
```
Orange Money → SagaKore Return View
```

1. **Vérification du statut** :
   - Appel à `check_transaction_status()` avec :
     - `order_id` : Numéro de commande
     - `amount` : Montant en centimes
     - `pay_token` : Token de paiement

2. **Traitement selon le statut** :
   - **SUCCESS** : Commande confirmée, panier vidé, redirection vers succès
   - **FAILED** : Commande annulée, message d'erreur
   - **PENDING** : Attente de la notification webhook

#### **Webhook de Notification (Notification URL)**
```
Orange Money → SagaKore Webhook Endpoint
```

1. **Réception de la notification** :
   ```json
   {
     "status": "SUCCESS|FAILED",
     "txnid": "transaction_id",
     "notif_token": "token_from_session",
     "amount": 10000,
     "currency": "OUV"
   }
   ```

2. **Validation de la notification** :
   - Vérification du `notif_token`
   - Validation du statut (`SUCCESS` ou `FAILED`)
   - Logging de la transaction

3. **Mise à jour de la commande** :
   - Recherche de la commande par `order_number`
   - Mise à jour du statut et du paiement
   - Nettoyage des données de session

### 4. **Gestion des Erreurs et Annulations**

#### **Annulation Utilisateur (Cancel URL)**
- Suppression de la commande temporaire
- Nettoyage de la session
- Redirection vers le panier avec message d'information

#### **Gestion des Timeouts**
- Timeout configuré à 600 secondes (10 minutes)
- Retry automatique jusqu'à 3 tentatives
- Logging détaillé des erreurs

### 5. **Sécurité et Validation**

#### **Protection CSRF**
- Toutes les vues protégées par `@csrf_protect`
- Webhook exempté avec `@csrf_exempt` mais validation manuelle

#### **Validation des Données**
- Vérification des montants (conversion centimes ↔ FCFA)
- Validation des tokens de notification
- Logging complet pour audit

#### **Gestion des Sessions**
- Tokens stockés en session Django
- Nettoyage automatique après traitement
- Protection contre les sessions orphelines

## 🔧 Architecture Technique

### **Classes et Services**

1. **OrangeMoneyService** (`saga/cart/orange_money_service.py`) :
   - Gestion de l'authentification OAuth2
   - Création des sessions de paiement
   - Vérification des statuts
   - Validation des webhooks

2. **Vues Django** (`saga/cart/views.py`) :
   - `orange_money_payment()` : Initiation du paiement
   - `orange_money_return()` : Traitement du retour
   - `orange_money_cancel()` : Gestion des annulations
   - `orange_money_webhook()` : Réception des notifications

3. **Configuration** (`saga/settings.py`) :
   - `ORANGE_MONEY_CONFIG` : Configuration principale
   - `ORANGE_MONEY_WEBHOOKS` : URLs de callback

### **URLs et Routage**

```python
# saga/cart/urls.py
path('orange-money/payment/', views.orange_money_payment, name='orange_money_payment'),
path('orange-money/return/', views.orange_money_return, name='orange_money_return'),
path('orange-money/cancel/', views.orange_money_cancel, name='orange_money_cancel'),
path('orange-money/webhook/', views.orange_money_webhook, name='orange_money_webhook'),
```

## 📊 États des Commandes

### **Statuts de Commande**
- `PENDING` : Commande créée, paiement en cours
- `CONFIRMED` : Paiement validé, commande confirmée
- `CANCELLED` : Paiement annulé ou échoué

### **Statuts de Paiement**
- `is_paid = False` : Paiement non effectué
- `is_paid = True` + `paid_at` : Paiement confirmé avec timestamp

## 🚀 Déploiement et Tests

### **Environnement de Développement**
- Utiliser ngrok pour exposer le serveur local
- Configurer les URLs de callback avec l'URL ngrok
- Tester avec le simulateur Orange Money

### **Environnement de Production**
- URLs de callback en HTTPS obligatoires
- Configuration des credentials de production
- Monitoring des logs et webhooks

## 📝 Logs et Debugging

### **Logging Détaillé**
- Tous les appels API sont loggés
- Erreurs et exceptions capturées
- Tokens et données sensibles masqués

### **Fichiers de Log**
- `orange_money_debug.log` : Logs spécifiques Orange Money
- `django.log` : Logs généraux Django
- `debug.log` : Logs de debug généraux

## ⚠️ Points d'Attention

1. **URLs de Callback** : Doivent être accessibles publiquement (pas localhost)
2. **HTTPS Obligatoire** : En production, toutes les URLs doivent être en HTTPS
3. **Gestion des Timeouts** : Orange Money a des timeouts stricts
4. **Validation des Webhooks** : Toujours valider les tokens de notification
5. **Gestion des Doublons** : Éviter les traitements multiples des mêmes notifications

## 🔄 Flux de Données Résumé

```
1. Utilisateur → Initie paiement → SagaKore
2. SagaKore → OAuth2 → Orange Money API
3. SagaKore → Crée session → Orange Money API
4. SagaKore → Redirige → Orange Money Payment
5. Utilisateur → Paiement → Orange Money
6. Orange Money → Webhook → SagaKore
7. Orange Money → Retour → SagaKore
8. SagaKore → Confirme commande → Utilisateur
```

Ce workflow garantit une intégration sécurisée et fiable avec l'API Orange Money Web Payment.
