# 📱 Commandes de Gestion des Téléphones - SagaKore

## 🚀 Commandes Intelligentes (Recommandées)

### Ajout de Téléphones avec Détection Automatique

#### `add_missing_pop`
**Ajoute uniquement les modèles POP manquants**
```bash
# Ajouter tous les modèles POP manquants
python manage.py add_missing_pop

# Ajouter un modèle spécifique
python manage.py add_missing_pop --model "POP 8"

# Mode simulation (dry-run)
python manage.py add_missing_pop --dry-run
```

**Fonctionnalités :**
- ✅ Détection automatique des modèles existants
- ✅ Évite les doublons (insensible à la casse)
- ✅ Ajout sélectif des modèles manquants
- ✅ Gestion intelligente des couleurs
- ✅ Prix cohérents selon la gamme

#### `add_tecno_spark_phones`
**Ajoute les téléphones TECNO SPARK avec gestion intelligente**
```bash
python manage.py add_tecno_spark_phones
```

**Fonctionnalités :**
- ✅ Ajout de toute la gamme SPARK
- ✅ Gestion automatique des couleurs
- ✅ Spécifications techniques complètes
- ✅ Prix adaptés au marché

### Commandes de Diagnostic

#### `check_existing_pop`
**Vérifie les modèles POP existants**
```bash
python manage.py check_existing_pop
```

**Affiche :**
- 📋 Liste des modèles existants
- 📊 Nombre de téléphones par modèle
- 🎨 Variantes de couleurs et mémoire
- ⚠️ Incohérences de capitalisation
- 💡 Recommandations

#### `show_urls`
**Affiche toutes les URLs de l'application**
```bash
python manage.py show_urls
```

### Commandes de Maintenance

#### `fix_duplicate_brands`
**Normalise les marques de téléphones**
```bash
# Mode simulation
python manage.py fix_duplicate_brands --dry-run

# Application des changements
python manage.py fix_duplicate_brands
```

#### `clean_duplicate_colors`
**Nettoie les couleurs en double**
```bash
python manage.py clean_duplicate_colors
```

#### `optimize_phone_dropdown`
**Optimise les listes déroulantes de téléphones**
```bash
python manage.py optimize_phone_dropdown
```

### Commandes de Données

#### `sync_products`
**Synchronise les produits entre environnements**
```bash
python manage.py sync_products
```

#### `dump_products`
**Exporte les produits vers un fichier JSON**
```bash
python manage.py dump_products
```

#### `deploy_products`
**Déploie les produits vers Heroku**
```bash
python manage.py deploy_products
```

#### `clean_dumps`
**Nettoie les fichiers de dump temporaires**
```bash
python manage.py clean_dumps
```

### Commandes Utilitaires

#### `generate_category_slugs`
**Génère les slugs pour les catégories**
```bash
python manage.py generate_category_slugs
```

## 📋 Template pour Nouvelles Commandes

### `add_phone_template.py`
**Template pour créer de nouvelles commandes d'ajout de téléphones**
- 📝 Structure standardisée
- 🔧 Gestion des erreurs
- 📊 Logs détaillés
- 🎨 Support des couleurs
- 💰 Configuration des prix

**Documentation complète :** `README_PHONE_TEMPLATE.md`

## 🎯 Bonnes Pratiques

### 1. Utilisation des Commandes Intelligentes
- ✅ Préférer `add_missing_pop` pour les ajouts POP
- ✅ Utiliser `check_existing_pop` avant tout ajout
- ✅ Tester en mode `--dry-run` quand possible

### 2. Gestion des Données
- ✅ Vérifier les doublons avant ajout
- ✅ Normaliser les marques avec `fix_duplicate_brands`
- ✅ Nettoyer les couleurs avec `clean_duplicate_colors`

### 3. Déploiement
- ✅ Tester en local avant Heroku
- ✅ Utiliser `sync_products` pour la synchronisation
- ✅ Vérifier avec `check_existing_pop` après déploiement

## 🔧 Commandes Supprimées

Les commandes suivantes ont été supprimées car remplacées par des versions intelligentes :
- ❌ `add_tecno_pop.py` → Remplacé par `add_missing_pop`
- ❌ `add_tecno_pop_colors.py` → Intégré dans `add_missing_pop`
- ❌ `add_tecnocamon_30_*.py` → Utiliser le template pour de nouveaux modèles
- ❌ `test_*.py` → Commandes de test temporaires

## 📊 Statistiques

### Gammes Disponibles
- **POP** : 10 modèles, 50 téléphones
- **SPARK** : Gamme complète
- **CAMON** : Modèles 30, 30S, 30 Pro, 30 Premier

### Prix par Gamme
- **POP** : 12,000 - 65,000 FCFA
- **SPARK** : 25,000 - 85,000 FCFA
- **CAMON** : 80,000 - 200,000+ FCFA

## 🚀 Prochaines Étapes

1. **Ajouter de nouveaux modèles** : Utiliser `add_phone_template.py`
2. **Maintenir la cohérence** : Utiliser les commandes de diagnostic
3. **Optimiser les performances** : Utiliser `optimize_phone_dropdown`
4. **Synchroniser les données** : Utiliser `sync_products`

---

💡 **Conseil :** Toujours utiliser les commandes intelligentes qui détectent automatiquement les doublons et évitent les conflits ! 