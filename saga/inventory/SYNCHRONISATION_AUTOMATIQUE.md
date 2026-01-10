# Synchronisation Automatique des Produits et Catégories B2B

## Vue d'ensemble

La synchronisation automatique des produits et catégories B2B peut être activée de plusieurs façons :

1. **Synchronisation lors de l'accès à la page d'accueil** (via middleware)
2. **Synchronisation lors de l'appel à l'API** (via endpoint)
3. **Synchronisation planifiée** (via cron job ou tâche planifiée)

## Mécanismes de Synchronisation Automatique

### 1. Synchronisation via Middleware (Recommandé)

Le middleware `AutoSyncB2BMiddleware` synchronise automatiquement les produits et catégories B2B lors de l'accès à certaines pages.

**Activation :**

Ajoutez dans `settings.py` :

```python
MIDDLEWARE = [
    # ... autres middlewares ...
    'inventory.middleware.AutoSyncB2BMiddleware',
    # ... autres middlewares ...
]
```

**Comportement :**
- Synchronise automatiquement les produits et catégories lors de l'accès à la page d'accueil (`/`)
- Synchronise automatiquement lors de l'appel aux API produits et catégories B2B
- Ne synchronise pas plus d'une fois toutes les 2 heures (configurable)
- Non bloquant : n'interrompt pas la requête en cas d'erreur

### 2. Synchronisation via API

Les endpoints suivants déclenchent automatiquement une synchronisation si nécessaire :
- `/api/inventory/products/synced/` - Synchronise les produits
- `/api/inventory/categories/synced/` - Synchronise les catégories

**Utilisation :**

```bash
# Appel simple - déclenche la synchronisation si nécessaire
curl http://votre-domaine.com/api/inventory/products/synced/
curl http://votre-domaine.com/api/inventory/categories/synced/
```

### 3. Synchronisation Planifiée (Cron Job)

Pour une synchronisation régulière, utilisez un cron job.

**Linux/Mac :**

```bash
# Éditer le crontab
crontab -e

# Ajouter des lignes pour synchroniser toutes les heures
0 * * * * cd /chemin/vers/sagakore && python manage.py sync_products_from_inventory --auto
0 * * * * cd /chemin/vers/sagakore && python manage.py sync_categories_from_inventory --auto

# Ou toutes les 2 heures
0 */2 * * * cd /chemin/vers/sagakore && python manage.py sync_products_from_inventory --auto
0 */2 * * * cd /chemin/vers/sagakore && python manage.py sync_categories_from_inventory --auto
```

**Windows (Task Scheduler) :**

1. Ouvrir le Planificateur de tâches
2. Créer une tâche de base pour les produits
3. Déclencher : Toutes les heures
4. Action : Exécuter un programme
5. Programme : `python`
6. Arguments : `manage.py sync_products_from_inventory --auto`
7. Démarrer dans : `C:\chemin\vers\sagakore`

8. Créer une deuxième tâche pour les catégories
9. Arguments : `manage.py sync_categories_from_inventory --auto`

### 4. Synchronisation via Vue Admin

Les vues de synchronisation dans l'admin utilisent maintenant la synchronisation automatique avec gestion du cache.

**Accès :**
- `/inventory/sync/products/` - Synchronisation des produits
- `/inventory/sync/categories/` - Synchronisation des catégories

## Configuration

### Intervalle de Synchronisation

Par défaut, la synchronisation ne se fait pas plus d'une fois toutes les 2 heures. Pour modifier cet intervalle :

```python
# Dans inventory/tasks.py
def should_sync_products():
    # ...
    if time_since_sync < 3600:  # Modifier 3600 (1 heure) selon vos besoins
        return False

def should_sync_categories():
    # ...
    if time_since_sync < 3600:  # Modifier 3600 (1 heure) selon vos besoins
        return False
```

### Forcer la Synchronisation

Pour forcer une synchronisation même si récente :

```python
from inventory.tasks import sync_products_auto, sync_categories_auto

# Forcer la synchronisation des produits
result = sync_products_auto(force=True)

# Forcer la synchronisation des catégories
result = sync_categories_auto(force=True)
```

### Commandes de Synchronisation

Les commandes de management supportent maintenant le mode automatique :

```bash
# Synchronisation automatique des produits (avec gestion du cache)
python manage.py sync_products_from_inventory --auto

# Synchronisation automatique des catégories (avec gestion du cache)
python manage.py sync_categories_from_inventory --auto

# Forcer la synchronisation même si récente
python manage.py sync_products_from_inventory --auto --force
python manage.py sync_categories_from_inventory --auto --force
```

## Vérification du Statut

### Via l'Admin

Accédez à `/inventory/status/` pour voir :
- Nombre de produits synchronisés
- Derniers produits synchronisés
- Statut des erreurs

### Via l'API

```bash
curl http://votre-domaine.com/inventory/api/status/
```

## Dépannage

### La synchronisation ne se déclenche pas

1. Vérifiez que le middleware est activé dans `settings.py`
2. Vérifiez les logs : `tail -f logs/django.log`
3. Vérifiez qu'une clé API est configurée : `/admin/inventory/apikey/`

### Erreurs de synchronisation

Les erreurs sont loggées dans les logs Django. Vérifiez :
- La connexion à l'API B2B
- La validité de la clé API
- Les permissions de la clé API

### Synchronisation trop fréquente

Ajustez l'intervalle dans `inventory/tasks.py` ou désactivez le middleware et utilisez uniquement le cron job.

## Recommandations

1. **Production** : Utilisez un cron job pour une synchronisation régulière et prévisible
2. **Développement** : Utilisez le middleware pour une synchronisation à la demande
3. **Performance** : La synchronisation est optimisée pour ne pas bloquer les requêtes utilisateur

## Notes

- La synchronisation automatique récupère les **détails complets** de chaque produit et catégorie
- Les produits et catégories sont mis à jour s'ils existent déjà, créés s'ils sont nouveaux
- Les erreurs sont loggées mais n'interrompent pas le processus
- Les synchronisations des produits et catégories sont indépendantes (cache séparé)
- Chaque type de synchronisation a son propre cache pour éviter les conflits

