# Guide de Configuration Orange Money

## 📋 Étapes de configuration

### 1. Inscription sur le portail développeur
- URL : https://developer.orange.com/myapps
- Créer un compte développeur
- Accepter les conditions d'utilisation

### 2. Création de l'application
- Créer une nouvelle application
- Ajouter l'API "Orange Money WebPayDev"
- Configurer avec les paramètres reçus

### 3. Génération de la clé marchande
Utiliser les paramètres reçus :
- **MSISDN** : Numéro de téléphone du Channel User
- **Agent Code** : Code agent fourni

### 4. Configuration des variables d'environnement

Ajoutez ces variables à votre fichier `.env` :

```bash
# Configuration Orange Money
ORANGE_MONEY_ENABLED=True
ORANGE_MONEY_ENV=dev

# Credentials Orange Money (à remplacer par vos vraies valeurs)
ORANGE_MONEY_MERCHANT_KEY=your_merchant_key_here
ORANGE_MONEY_CLIENT_ID=your_client_id_here
ORANGE_MONEY_CLIENT_SECRET=your_client_secret_here

# Configuration des paiements
ORANGE_MONEY_CURRENCY=OUV
ORANGE_MONEY_LANGUAGE=fr
ORANGE_MONEY_TIMEOUT=600
ORANGE_MONEY_MAX_RETRIES=3
```

### 5. Test avec le simulateur
- URL du simulateur : https://mpayment.orange-money.com/mpayment-otp/login
- Login : MSISDN du Channel User
- Mot de passe : id/login/name du Channel User

## 🔧 Paramètres reçus

### Channel User (Compte marchand)
- **id/login/name** : [Valeur fournie]
- **MSISDN** : [Numéro de téléphone]
- **Agent Code** : [Code agent]
- **PIN** : [Code PIN]
- **balance** : [Solde]

### Subscriber (Compte utilisateur de test)
- **id/login/name** : [Valeur fournie]
- **MSISDN** : [Numéro de téléphone]
- **PIN** : [Code PIN]
- **balance** : [Solde]

## 🧪 Test du flux de paiement

1. **Création de session** : Votre application crée une session de paiement
2. **Redirection** : L'utilisateur est redirigé vers Orange Money
3. **Paiement** : L'utilisateur saisit son numéro et OTP
4. **Notification** : Orange Money notifie votre application
5. **Confirmation** : La commande est confirmée

## 📱 URLs importantes

- **Portail développeur** : https://developer.orange.com/myapps
- **Simulateur OTP** : https://mpayment.orange-money.com/mpayment-otp/login
- **API Token** : https://api.orange.com/oauth/v3/token
- **API WebPayment** : https://api.orange.com/orange-money-webpay/dev/v1/webpayment
- **API Status** : https://api.orange.com/orange-money-webpay/dev/v1/transactionstatus

## ⚠️ Points importants

1. **Environnement de test** : Utilisez `OUV` comme devise
2. **Unicité des order_id** : Chaque commande doit avoir un ID unique
3. **HTTPS obligatoire** : Toutes les communications en HTTPS
4. **Timeouts** : Les tokens expirent en 10 minutes
5. **Validation** : Vérifiez toujours les tokens de notification

## 🔍 Vérification de la configuration

Une fois configuré, vous pouvez tester en :
1. Ajoutant des produits au panier
2. Allant au checkout
3. Sélectionnant Orange Money
4. Suivant le flux de paiement

