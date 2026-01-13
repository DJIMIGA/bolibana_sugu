# Diagnostic : Pourquoi tous les produits B2B ne sont pas dans B2C

## Problème identifié

Tous les produits du JSON B2B ne sont pas visibles dans B2C. Voici les raisons possibles et les solutions.

## Raisons possibles

### 1. **Filtre `is_available=True` dans l'API**

**Localisation :** `saga/inventory/api/views.py` ligne 262

L'endpoint `/api/inventory/products/synced/` filtre uniquement les produits avec `is_available=True` :

```python
products = Product.objects.filter(
    id__in=product_ids,
    is_available=True  # ← Ce filtre exclut les produits non disponibles
)
```

**Impact :** Les produits synchronisés mais marqués comme `is_available=False` ne sont pas retournés par l'API.

**Solution :** Vérifier pourquoi les produits sont marqués comme non disponibles dans le JSON B2B.

### 2. **Logique de `is_available` lors de la synchronisation**

**Localisation :** `saga/inventory/services.py` lignes 796-799

La valeur `is_available` est définie avec cette logique :

```python
'is_available': external_data.get('is_available_b2c', 
                                external_data.get('is_available', 
                                external_data.get('is_active', 
                                external_data.get('available', True)))),
```

**Ordre de priorité :**
1. `is_available_b2c` (priorité la plus haute)
2. `is_available`
3. `is_active`
4. `available`
5. `True` (par défaut)

**Impact :** Si le JSON B2B contient `is_available_b2c=False` ou `is_available=False`, le produit sera marqué comme non disponible.

### 3. **Erreurs de synchronisation**

**Localisation :** `saga/inventory/services.py` lignes 616-623

Si la catégorie n'est pas trouvée ou créée, le produit n'est pas synchronisé :

```python
if not category:
    error_msg = (
        f"Impossible de trouver ou créer la catégorie pour le produit B2B (ID externe: {external_id}). "
        f"Category ID externe: {external_category_id}. "
        f"Veuillez synchroniser les catégories avant de synchroniser les produits."
    )
    raise ValidationError(error_msg)
```

**Impact :** Les produits sans catégorie valide ne sont pas synchronisés.

**Solution :** Synchroniser les catégories avant les produits :
```bash
python manage.py sync_categories_from_inventory
python manage.py sync_products_from_inventory
```

### 4. **Produits sans relation Product**

**Localisation :** `saga/inventory/api/views.py` lignes 250-257

Si `ExternalProduct` existe mais sans relation `Product` valide, le produit n'est pas retourné :

```python
product_ids = [ep.product.id for ep in external_products if ep.product]
if not product_ids:
    # Aucun produit valide trouvé
```

**Impact :** Les `ExternalProduct` orphelins (sans `Product`) ne sont pas inclus.

**Solution :** Vérifier et corriger les `ExternalProduct` sans `Product` associé.

## Commandes de diagnostic

### 1. Exécuter le diagnostic complet

```bash
python manage.py diagnostic_b2b_b2c
```

Cette commande affiche :
- Nombre de produits dans l'API B2B
- Nombre de produits synchronisés
- Nombre de produits avec relation Product
- Nombre de produits disponibles
- Liste des produits manquants et raisons

### 2. Vérifier les produits non disponibles

```python
from inventory.models import ExternalProduct
from product.models import Product

# Produits synchronisés mais non disponibles
synced_products = ExternalProduct.objects.filter(
    sync_status='synced',
    is_b2b=True,
    product__isnull=False
)
unavailable = Product.objects.filter(
    id__in=[ep.product.id for ep in synced_products],
    is_available=False
)
print(f"Produits synchronisés mais non disponibles: {unavailable.count()}")
for p in unavailable[:10]:
    print(f"  - {p.title} (ID: {p.id})")
```

### 3. Vérifier les erreurs de synchronisation

```python
from inventory.models import ExternalProduct

# Produits avec erreur de synchronisation
errors = ExternalProduct.objects.filter(sync_status='error')
print(f"Produits avec erreur: {errors.count()}")
for ep in errors[:10]:
    print(f"  - ID externe {ep.external_id}: {ep.sync_error}")
```

### 4. Vérifier les produits sans catégorie

```python
from inventory.models import ExternalProduct
from product.models import Product

# Produits synchronisés sans catégorie
synced = ExternalProduct.objects.filter(
    sync_status='synced',
    is_b2b=True,
    product__isnull=False
)
no_category = Product.objects.filter(
    id__in=[ep.product.id for ep in synced],
    category__isnull=True
)
print(f"Produits sans catégorie: {no_category.count()}")
```

## Solutions recommandées

### Solution 1 : Vérifier les données B2B

Vérifier dans le JSON B2B si les produits ont :
- `is_available_b2c=True` ou `is_available=True`
- Une catégorie valide (`category_id` ou `category`)

### Solution 2 : Synchroniser les catégories d'abord

```bash
# 1. Synchroniser les catégories
python manage.py sync_categories_from_inventory

# 2. Synchroniser les produits
python manage.py sync_products_from_inventory
```

### Solution 3 : Forcer la synchronisation

```bash
# Forcer la synchronisation même si récente
python manage.py sync_products_from_inventory --auto --force
```

### Solution 4 : Modifier le filtre API (si nécessaire)

Si vous voulez inclure les produits non disponibles dans l'API, modifier `saga/inventory/api/views.py` :

```python
# Avant (ligne 262)
products = Product.objects.filter(
    id__in=product_ids,
    is_available=True
)

# Après (inclure tous les produits synchronisés)
products = Product.objects.filter(
    id__in=product_ids
    # Retirer le filtre is_available=True si nécessaire
)
```

**⚠️ Attention :** Retirer ce filtre peut exposer des produits non disponibles aux clients.

## Checklist de vérification

- [ ] Exécuter `python manage.py diagnostic_b2b_b2c`
- [ ] Vérifier les produits avec `is_available=False` dans le JSON B2B
- [ ] Synchroniser les catégories avant les produits
- [ ] Vérifier les erreurs de synchronisation dans `ExternalProduct.sync_error`
- [ ] Vérifier que tous les produits ont une catégorie valide
- [ ] Vérifier les `ExternalProduct` sans relation `Product`

## Fichiers concernés

- `saga/inventory/services.py` - Logique de synchronisation
- `saga/inventory/api/views.py` - Endpoint API `/api/inventory/products/synced/`
- `saga/inventory/models.py` - Modèles `ExternalProduct` et `ExternalCategory`
- `saga/inventory/management/commands/diagnostic_b2b_b2c.py` - Commande de diagnostic
