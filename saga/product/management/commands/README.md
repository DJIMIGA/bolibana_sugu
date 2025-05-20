# Commandes de Gestion des Produits

Ce dossier contient les commandes de gestion pour l'application `product`. Ces commandes permettent de gérer les données des produits, téléphones et images.

## Commandes Disponibles

### 1. dump_products
Exporte les données des produits, téléphones et images en JSON.

```bash
python manage.py dump_products
```

Le fichier de dump sera créé dans le dossier `product/dumps/` avec un nom au format `products_dump_YYYYMMDD_HHMMSS.json`.

### 2. deploy_products
Déploie les données des produits sur Heroku.

Options disponibles :
- `--force` : Force le déploiement même si des données existent déjà
- `--backup` : Crée une sauvegarde des données existantes avant le déploiement

```bash
# Déploiement simple
heroku run python manage.py deploy_products
python manage.py deploy_products

# Déploiement avec sauvegarde
python manage.py deploy_products --backup

# Déploiement forcé
python manage.py deploy_products --force
```

### 3. update_image_urls
Met à jour les URLs des images des produits.

```bash
python manage.py update_image_urls
```

## Structure des Données

### Format du Dump
Le fichier de dump JSON contient trois sections principales :
1. `products` : Données des produits
2. `phones` : Données des téléphones
3. `images` : Données des images

### Format de la Sauvegarde
Les sauvegardes sont stockées dans le dossier `product/backups/` avec un nom au format `heroku_backup_YYYYMMDD_HHMMSS.json`.

## Structure des Dossiers

```
product/
├── dumps/           # Dossier pour les fichiers de dump
├── backups/         # Dossier pour les sauvegardes Heroku
└── management/
    └── commands/    # Commandes de gestion
```

## Bonnes Pratiques

1. **Avant le Déploiement**
   - Créer un dump local des données
   - Vérifier le contenu du dump
   - Créer une sauvegarde sur Heroku

2. **Pendant le Déploiement**
   - Utiliser l'option `--backup` pour la sécurité
   - Vérifier les logs pour détecter les erreurs
   - Tester les données après le déploiement

3. **Après le Déploiement**
   - Vérifier l'intégrité des données
   - Tester les fonctionnalités principales
   - Conserver les sauvegardes

## Notes Importantes

- Les commandes doivent être exécutées depuis le répertoire racine du projet
- Les dumps et sauvegardes sont stockés dans des dossiers dédiés au sein de l'application product
- Les données sensibles ne sont pas incluses dans les dumps
- Les images sont référencées par leurs URLs 