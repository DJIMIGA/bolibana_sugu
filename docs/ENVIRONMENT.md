# Guide de Configuration des Environnements

## Table des Matières
1. [Environnements](#environnements)
2. [Configuration de Base](#configuration-de-base)
3. [Sécurité](#sécurité)
4. [Base de Données](#base-de-données)
5. [Vérification et Maintenance](#vérification-et-maintenance)
6. [Bonnes Pratiques](#bonnes-pratiques)

## Environnements

### Production (Heroku)
```bash
# Configuration principale
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=votre_clé_secrète
heroku config:set ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com

# Base de données
heroku config:set DATABASE_URL=postgres://...

# Services externes
heroku config:set AWS_ACCESS_KEY_ID=votre_clé
heroku config:set AWS_SECRET_ACCESS_KEY=votre_clé_secrète_aws
heroku config:set STRIPE_PUBLIC_KEY=votre_clé
heroku config:set STRIPE_SECRET_KEY=votre_clé_secrète_stripe
```

### Développement (Local)
```bash
# Fichier .env
DEBUG=True
SECRET_KEY=clé_secrète_de_développement
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données locale
DB_NAME=nom_base
DB_USER=utilisateur
DB_PASSWORD=mot_de_passe
DB_HOST=localhost
DB_PORT=5432
```

## Configuration de Base

### Mode DEBUG
- **Production** : `DEBUG=False`
  - Sécurité renforcée
  - Pas d'informations sensibles exposées
  - Gestion sécurisée des erreurs
  - Protection contre les attaques

- **Développement** : `DEBUG=True`
  - Affichage des erreurs détaillées
  - Outils de débogage Django
  - Rechargement automatique des templates
  - Développement facilité

### Variables d'Environnement
```bash
# Structure recommandée du fichier .env
DEBUG=True/False
SECRET_KEY=votre_clé
ALLOWED_HOSTS=domaine1,domaine2
DATABASE_URL=postgres://...
AWS_ACCESS_KEY_ID=votre_clé
AWS_SECRET_ACCESS_KEY=votre_clé_secrète
STRIPE_PUBLIC_KEY=votre_clé
STRIPE_SECRET_KEY=votre_clé_secrète
```

## Sécurité

### Configuration SSL/HTTPS
```python
# En production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Protection des Données
- Clés secrètes différentes par environnement
- Variables sensibles dans .env
- Pas de données sensibles dans le code
- Utilisation de HTTPS en production

## Base de Données

### Production (Heroku)
```python
DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=True
    )
}
```

### Développement (Local)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
```

## Vérification et Maintenance

### En Production
```bash
# Vérification des variables
heroku config

# Surveillance des logs
heroku logs --tail

# Vérification de la base de données
heroku pg:info
```

### En Développement
```bash
# Vérification de la configuration
python manage.py check
python manage.py diffsettings

# Vérification de la base de données
python manage.py dbshell
```

## Bonnes Pratiques

### 1. Gestion des Fichiers
- Ne jamais commiter les fichiers .env
- Utiliser .env.example comme modèle
- Documenter toutes les variables requises
- Maintenir une liste des variables d'environnement

### 2. Sécurité
- Vérifier régulièrement DEBUG=False en production
- Roter les clés secrètes périodiquement
- Utiliser des mots de passe forts
- Limiter l'accès aux variables sensibles

### 3. Maintenance
- Documenter tous les changements de configuration
- Maintenir à jour la documentation
- Faire des sauvegardes régulières
- Tester la configuration après les changements

### 4. Déploiement
- Vérifier la configuration avant le déploiement
- Tester en environnement de staging
- Avoir un plan de rollback
- Documenter les procédures de déploiement 