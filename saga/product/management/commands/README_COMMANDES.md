# 📱 Commandes de Gestion des Produits

## 🎯 Commandes Principales

### 📱 Ajout de Téléphones

#### `add_phone_template.py`
**Template générique pour ajouter des téléphones**
```bash
python manage.py add_phone_template --brand "MARQUE" --model "MODELE"
```
- **Usage :** Template réutilisable pour ajouter n'importe quel modèle de téléphone
- **Avantages :** Évite les erreurs courantes, structure correcte (Product → Phone)
- **Documentation :** Voir `README_PHONE_TEMPLATE.md`

## 🔧 Commandes Utilitaires

### 📊 Gestion des Données

#### `dump_products.py`
**Export des produits vers JSON**
```bash
python manage.py dump_products
```
- **Usage :** Sauvegarde tous les produits dans un fichier JSON
- **Fichier :** `products_dump.json`

#### `deploy_products.py`
**Import des produits depuis JSON**
```bash
python manage.py deploy_products
```
- **Usage :** Importe les produits depuis `products_dump.json`
- **Utile :** Migration de données entre environnements

#### `sync_products.py`
**Synchronisation des produits**
```bash
python manage.py sync_products
```
- **Usage :** Synchronise les données entre Product et Phone
- **Utile :** Correction des incohérences

### 🧹 Maintenance

#### `clean_dumps.py`
**Nettoyage des fichiers de dump**
```bash
python manage.py clean_dumps
```
- **Usage :** Supprime les anciens fichiers de dump
- **Utile :** Libération d'espace disque

#### `generate_category_slugs.py`
**Génération des slugs de catégories**
```bash
python manage.py generate_category_slugs
```
- **Usage :** Génère les slugs manquants pour les catégories
- **Utile :** Correction des URLs

### 🔍 Diagnostic

#### `show_urls.py`
**Affichage des URLs du projet**
```bash
python manage.py show_urls
```
- **Usage :** Liste toutes les URLs disponibles
- **Utile :** Debug et vérification des routes

### 🎨 Gestion des Marques

#### `fix_duplicate_brands.py`
**Correction des marques dupliquées**
```bash
python manage.py fix_duplicate_brands
```
- **Usage :** Corrige les marques en double dans la base de données
- **Utile :** Nettoyage des données

#### `optimize_phone_dropdown.py`
**Optimisation du dropdown des téléphones**
```bash
python manage.py optimize_phone_dropdown
```
- **Usage :** Optimise l'affichage du dropdown des téléphones
- **Utile :** Amélioration des performances

#### `test_phone_brands_dropdown.py`
**Test du dropdown des marques**
```bash
python manage.py test_phone_brands_dropdown
```
- **Usage :** Teste le fonctionnement du dropdown des marques
- **Utile :** Debug et validation

## 📋 Bonnes Pratiques

### ✅ Avant d'ajouter un nouveau modèle :
1. **Vérifier les couleurs existantes** dans la base de données
2. **Utiliser le template** `add_phone_template.py` pour éviter les erreurs
3. **Tester en local** avant de déployer sur Heroku
4. **Documenter** les spécifications techniques

### ✅ Après l'ajout :
1. **Vérifier l'affichage** sur le site
2. **Tester les prix** et la disponibilité
3. **Nettoyer** les commandes spécifiques utilisées
4. **Sauvegarder** avec `dump_products.py` si nécessaire

## 🚀 Déploiement Heroku

### Utilisation du template générique :
```bash
heroku run python manage.py add_phone_template --brand "TECNO" --model "CAMON 40"
```

### Vérification :
```bash
heroku run python manage.py show_urls
```

## 📝 Notes Importantes

- **Structure correcte :** Toujours créer `Product` avant `Phone`
- **Titres uniques :** Inclure ROM, RAM et couleur dans le titre
- **SKU uniques :** Format cohérent et descriptif
- **Prix réalistes :** Basés sur le marché local
- **Couleurs en français :** "Noir Galaxy" au lieu de "Galaxy Black"

## 🧹 Nettoyage Effectué

Les commandes suivantes ont été supprimées après utilisation :
- `add_tecnocamon_30s_colors.py` - Couleurs CAMON 30S ajoutées
- `add_tecnocamon_30s.py` - Téléphones CAMON 30S ajoutés
- `add_tecnocamon_40_colors.py` - Couleurs CAMON 40 ajoutées
- `add_tecnocamon_40.py` - Téléphones CAMON 40 ajoutés

**✅ Seul le template générique `add_phone_template.py` est conservé pour les futurs ajouts.** 