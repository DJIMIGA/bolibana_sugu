# 📧 Configuration Email - SagaKore

## 🔍 Problème Identifié

Les emails de confirmation de commande ne sont pas envoyés car l'application est configurée en mode développement avec le backend de console.

## 🛠️ Solutions Implémentées

### 1. Configuration SMTP Améliorée

La configuration email a été mise à jour pour permettre l'envoi d'emails réels même en développement :

```python
# saga/settings.py
if DEBUG:
    # Configuration pour le développement avec envoi d'emails réels
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'dev@localhost')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
    
    # Fallback vers console si pas de configuration SMTP
    if not EMAIL_HOST_PASSWORD:
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### 2. Fonction d'Envoi d'Email Améliorée

La fonction `send_order_confirmation_email` a été améliorée avec :
- Logs détaillés pour le debugging
- Gestion d'erreurs spécifiques
- Retour de statut (True/False)

### 3. Outils de Test

#### A. Vue de Test (Administrateurs uniquement)
- URL : `/cart/test-email/`
- Accessible uniquement aux utilisateurs staff
- Interface web pour tester la configuration

#### B. Commande Django
```bash
python manage.py test_email --email votre-email@exemple.com
```

#### C. Script Python
```bash
python test_email.py
```

## 🔧 Configuration Gmail SMTP

### Étape 1 : Activer l'authentification à 2 facteurs

1. Allez sur [myaccount.google.com](https://myaccount.google.com)
2. Sécurité > Authentification à 2 facteurs
3. Activez l'authentification à 2 facteurs

### Étape 2 : Générer un mot de passe d'application

1. Dans les paramètres Google > Sécurité
2. Authentification à 2 facteurs > Mots de passe d'application
3. Sélectionnez "Application" et "Autre (nom personnalisé)"
4. Entrez "SagaKore" comme nom
5. Copiez le mot de passe généré (16 caractères)

### Étape 3 : Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# Configuration Email Gmail SMTP
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app-16-caracteres

# Configuration de base
DEBUG=True
SECRET_KEY=django-insecure-default-key-for-dev

# Base de données locale
DB_NAME=sagakore_db
DB_USER=sagakore_user
DB_PASSWORD=sagakore_password
DB_HOST=localhost
DB_PORT=5432
```

### Étape 4 : Redémarrer l'application

```bash
python manage.py runserver
```

## 🧪 Tests de Configuration

### Test via l'interface web

1. Connectez-vous en tant qu'administrateur
2. Allez sur `/cart/test-email/`
3. Entrez votre adresse email
4. Cliquez sur "Envoyer un email de test"

### Test via la ligne de commande

```bash
# Test avec email spécifié
python manage.py test_email --email votre-email@exemple.com

# Test interactif
python manage.py test_email
```

### Test via script Python

```bash
python test_email.py
```

## 📋 Vérification de la Configuration

### Logs de Démarrage

Lors du démarrage de l'application, vous devriez voir :

```
📧 Email configuré en mode SMTP (développement)
📧 Email configuré : Oui
```

### Logs d'Envoi d'Email

Lors de l'envoi d'un email de confirmation :

```
📧 === ENVOI EMAIL DE CONFIRMATION ===
Commande: ORD-2024-001
Utilisateur: client@exemple.com
Mode DEBUG: True
EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend
DEFAULT_FROM_EMAIL: votre-email@gmail.com
Domain URL depuis request: http://localhost:8000
Sujet: Confirmation de votre commande ORD-2024-001
✅ Template email rendu avec succès
Longueur HTML: 1234 caractères
Longueur texte: 567 caractères
📤 Tentative d'envoi d'email...
De: votre-email@gmail.com
À: client@exemple.com
✅ Email de confirmation envoyé avec succès à client@exemple.com
```

## 🚨 Erreurs Courantes et Solutions

### Erreur d'authentification SMTP

```
❌ Erreur lors de l'envoi de l'email de confirmation:
   Type d'erreur: SMTPAuthenticationError
   Message: (535, b'5.7.8 Username and Password not accepted.')
   🔐 Erreur d'authentification SMTP - Vérifiez EMAIL_HOST_USER et EMAIL_HOST_PASSWORD
```

**Solutions :**
1. Vérifiez que l'authentification à 2 facteurs est activée
2. Utilisez le mot de passe d'application, pas votre mot de passe Gmail
3. Régénérez un nouveau mot de passe d'application

### Erreur de connexion SMTP

```
❌ Erreur lors de l'envoi de l'email de confirmation:
   Type d'erreur: SMTPConnectError
   Message: [Errno 11001] getaddrinfo failed
   🌐 Erreur de connexion SMTP - Vérifiez EMAIL_HOST et EMAIL_PORT
```

**Solutions :**
1. Vérifiez votre connexion internet
2. Vérifiez que le pare-feu n'empêche pas la connexion
3. Essayez avec un autre réseau

### Destinataire refusé

```
❌ Erreur lors de l'envoi de l'email de confirmation:
   Type d'erreur: SMTPRecipientsRefused
   Message: {'client@exemple.com': (550, b'5.1.1 The email account that you tried to reach does not exist.')}
   📧 Destinataire refusé - Vérifiez l'adresse email: client@exemple.com
```

**Solutions :**
1. Vérifiez que l'adresse email de destination est correcte
2. Vérifiez que l'adresse email existe

## 🔒 Sécurité

### Variables d'Environnement

- **NE JAMAIS** commiter le fichier `.env` dans Git
- Le fichier `.env` est déjà dans `.gitignore`
- Utilisez des variables d'environnement en production

### Mots de Passe d'Application

- **NE JAMAIS** utiliser votre mot de passe Gmail normal
- Utilisez **UNIQUEMENT** les mots de passe d'application
- Régénérez les mots de passe d'application régulièrement

## 📊 Monitoring

### Logs d'Email

Les logs d'email sont écrits dans :
- Console Django (développement)
- Fichier `debug.log` (production)

### Métriques

- Taux de succès d'envoi d'email
- Temps de livraison
- Erreurs par type

## 🚀 Production

### Configuration Heroku

En production sur Heroku, utilisez les variables d'environnement :

```bash
heroku config:set EMAIL_HOST_USER=votre-email@gmail.com
heroku config:set EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
```

### Configuration Alternative

Pour une solution plus robuste en production, considérez :
- SendGrid
- Mailgun
- Amazon SES
- Postmark

## 📞 Support

En cas de problème :
1. Vérifiez les logs de l'application
2. Testez avec l'outil de test intégré
3. Vérifiez la configuration Gmail
4. Consultez la documentation Gmail SMTP 