# 🔧 Intégration API Orange Money - Guide Simple

## 🎯 **Qu'est-ce qu'une API ?**

Une API = **Application Programming Interface** = C'est comme un **messager** entre notre site et Orange Money.

```
SagaKore ←→ API Orange Money ←→ Orange Money
```

## 🔄 **Les 3 Appels API Principaux**

### **1. Authentification (OAuth2)**
**But :** Obtenir la permission de parler à Orange Money

```python
# Ce que notre code fait :
POST https://api.orange.com/oauth/v3/token
Headers: Authorization: Basic {client_id:client_secret}
Body: grant_type=client_credentials

# Ce qu'Orange Money répond :
{
  "access_token": "ABC123XYZ789",
  "expires_in": 7776000  # 90 jours
}
```

**En français :** "Bonjour Orange Money, voici mes identifiants, donnez-moi un ticket pour parler avec vous"

### **2. Création de Session de Paiement**
**But :** Dire à Orange Money qu'on veut créer un paiement

```python
# Ce que notre code envoie :
POST https://api.orange.com/orange-money-webpay/dev/v1/webpayment
Headers: Authorization: Bearer ABC123XYZ789
Body: {
  "merchant_key": "notre_cle_marchand",
  "currency": "OUV",
  "order_id": "SagaKore-12345",
  "amount": 50000,  # 50 000 FCFA en centimes
  "return_url": "https://sagakore.com/return",
  "cancel_url": "https://sagakore.com/cancel",
  "notif_url": "https://sagakore.com/webhook",
  "lang": "fr",
  "reference": "SagaKore"
}

# Ce qu'Orange Money répond :
{
  "status": 201,
  "message": "OK",
  "pay_token": "f5720dd906203c62033ffe64ed756147",
  "payment_url": "https://webpayment-qualif.orange-money.com/payment/pay_token/f5720dd906203c62033ffe64ed756147",
  "notif_token": "dd497bda3b250e536186fc0663f32f40"
}
```

**En français :** "Orange Money, créez un paiement de 50 000 FCFA pour la commande SagaKore-12345"

### **3. Vérification du Statut**
**But :** Demander à Orange Money si le paiement est OK

```python
# Ce que notre code envoie :
POST https://api.orange.com/orange-money-webpay/dev/v1/transactionstatus
Headers: Authorization: Bearer ABC123XYZ789
Body: {
  "order_id": "SagaKore-12345",
  "amount": 50000,
  "pay_token": "f5720dd906203c62033ffe64ed756147"
}

# Ce qu'Orange Money répond :
{
  "status": "SUCCESS",
  "order_id": "SagaKore-12345",
  "txnid": "MP150709.1341.A00073"
}
```

**En français :** "Orange Money, le paiement pour SagaKore-12345 est-il OK ?"

## 🏗️ **Notre Code en Action**

### **1. OrangeMoneyService (Notre Messager)**

```python
class OrangeMoneyService:
    def get_access_token(self):
        """Étape 1 : Obtenir le ticket d'accès"""
        # Envoie nos identifiants à Orange Money
        # Reçoit un token d'accès
        
    def create_payment_session(self, order_data):
        """Étape 2 : Créer une session de paiement"""
        # Utilise le token pour créer un paiement
        # Reçoit un pay_token et notif_token
        
    def check_transaction_status(self, order_id, amount, pay_token):
        """Étape 3 : Vérifier le statut"""
        # Demande le statut du paiement
        # Reçoit SUCCESS, FAILED, PENDING, etc.
```

### **2. Les Vues Django (Nos Contrôleurs)**

```python
def orange_money_payment(request):
    """Quand le client clique 'Payer avec Orange Money'"""
    # 1. Vérifier que Orange Money est configuré
    # 2. Créer une commande temporaire
    # 3. Appeler create_payment_session()
    # 4. Rediriger le client vers Orange Money

def orange_money_return(request):
    """Quand le client revient d'Orange Money"""
    # 1. Récupérer les infos de la session
    # 2. Appeler check_transaction_status()
    # 3. Confirmer ou annuler la commande

def orange_money_webhook(request):
    """Quand Orange Money nous notifie"""
    # 1. Recevoir la notification
    # 2. Valider le notif_token
    # 3. Mettre à jour la commande
```

## 🔄 **Flux Complet de l'API**

### **Étape 1 : Authentification**
```
SagaKore → API Orange Money : "Voici mes identifiants"
Orange Money → SagaKore : "Voici votre token ABC123"
```

### **Étape 2 : Création de Paiement**
```
SagaKore → API Orange Money : "Créez un paiement de 50 000 FCFA"
Orange Money → SagaKore : "Voici le code f5720dd906203c62033ffe64ed756147"
```

### **Étape 3 : Redirection Client**
```
SagaKore → Client : "Allez sur https://webpayment-qualif.orange-money.com/payment/pay_token/f5720dd906203c62033ffe64ed756147"
```

### **Étape 4 : Client Paie**
```
Client → Orange Money : "Je paie avec mon numéro 770123456"
Orange Money → Client : "Voici votre code SMS 123456"
Client → Orange Money : "Code 123456 confirmé"
```

### **Étape 5 : Notification (Webhook)**
```
Orange Money → SagaKore : "Paiement OK pour SagaKore-12345"
```

### **Étape 6 : Vérification**
```
SagaKore → API Orange Money : "Confirmez le statut de SagaKore-12345"
Orange Money → SagaKore : "SUCCESS"
```

## 🔧 **Configuration Technique**

### **Variables d'Environnement**
```bash
# Nos identifiants Orange Money
ORANGE_MONEY_CLIENT_ID=notre_client_id
ORANGE_MONEY_CLIENT_SECRET=notre_client_secret
ORANGE_MONEY_MERCHANT_KEY=notre_cle_marchand

# URLs de callback (où Orange Money nous contacte)
ORANGE_MONEY_NOTIFICATION_URL=https://sagakore.com/cart/orange-money/webhook/
ORANGE_MONEY_RETURN_URL=https://sagakore.com/cart/orange-money/return/
ORANGE_MONEY_CANCEL_URL=https://sagakore.com/cart/orange-money/cancel/
```

### **URLs API selon l'Environnement**
```python
# Développement
token_url = "https://api.orange.com/oauth/v3/token"
webpayment_url = "https://api.orange.com/orange-money-webpay/dev/v1/webpayment"
payment_url = "https://webpayment-qualif.orange-money.com"

# Production
token_url = "https://api.orange.com/oauth/v3/token"
webpayment_url = "https://api.orange.com/orange-money-webpay/v1/webpayment"
payment_url = "https://webpayment.orange-money.com"
```

## 🛡️ **Sécurité de l'API**

### **1. Authentification**
- **Client ID + Secret** : Nos identifiants
- **Access Token** : Ticket temporaire (90 jours)
- **Bearer Token** : Utilisé pour chaque requête

### **2. Validation**
- **notif_token** : Vérifie que la notification vient bien d'Orange Money
- **order_id** : Identifiant unique de notre commande
- **amount** : Montant en centimes (évite les erreurs de virgule)

### **3. HTTPS**
- Toutes les communications sont cryptées
- Pas de données sensibles en clair

## 📊 **Gestion des Erreurs**

### **Codes de Réponse HTTP**
```python
200 = OK
201 = Créé avec succès
400 = Requête invalide
401 = Token invalide
403 = Accès refusé
500 = Erreur serveur Orange Money
```

### **Statuts de Transaction**
```python
INITIATED = En attente du client
PENDING = Client a confirmé, en cours
EXPIRED = Trop tard (token expiré)
SUCCESS = Paiement réussi
FAILED = Paiement échoué
```

## 🎯 **En Résumé**

L'intégration API Orange Money = **3 appels simples** :

1. **Authentification** : "Donnez-moi un ticket"
2. **Création** : "Créez un paiement"
3. **Vérification** : "Le paiement est-il OK ?"

**Notre code fait tout automatiquement** :
- Gère les tokens
- Gère les erreurs
- Gère les notifications
- Gère les redirections

**Le développeur n'a qu'à** :
- Configurer les identifiants
- Appeler les bonnes fonctions
- Gérer les réponses

**C'est tout !** 🎉
