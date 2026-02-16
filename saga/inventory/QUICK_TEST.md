# ⚡ Test Rapide en 5 Minutes

## Test Ultra-Rapide

### 1. Configuration (1 min)

Vérifier `.env` :
```env
B2B_API_URL=https://www.bolibanastock.com/api/v1
INVENTORY_ENCRYPTION_KEY=votre_cle
```

### 2. Ajouter la Clé API (2 min)

**Via l'admin** (`/admin/inventory/`) :

1. **Ajouter la clé API** :
   - `/admin/inventory/apikey/add/`
   - Nom : "Clé principale" (ou autre nom descriptif)
   - Clé API : Entrer la clé API réelle depuis B2B (ex: `b2c_1_xxxxx`)
   - Cocher "Active"
   - Sauvegarder

**Note** : Le système utilise une seule clé API active à la fois. Si vous avez plusieurs clés, assurez-vous qu'une seule est active.

### 3. Tester la Connexion (1 min)

Vérifier la connexion en lançant la synchronisation des catégories (voir étape 4). En cas d’erreur, consulter `TEST_GUIDE.md`.

### 4. Synchroniser (1 min)

```bash
# Catégories
python manage.py sync_categories_from_inventory

# Produits (tous)
python manage.py sync_products_from_inventory

# Produits d'un site spécifique
python manage.py sync_products_from_inventory --site-id 1
```

### 5. Vérifier (30 sec)

**Dans l'admin** :
- `/admin/product/category/` → Vérifier les catégories avec `external_id`
- `/admin/product/product/` → Vérifier les produits avec `external_id`

**Sur le site** :
- `/inventory/categories/` → Voir les catégories synchronisées

## ✅ Si tout fonctionne

Vos produits B2B sont maintenant visibles dans B2C ! 🎉

## ❌ Si ça ne fonctionne pas

Consultez `TEST_GUIDE.md` pour le dépannage détaillé.

