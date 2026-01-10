# Guide : Gestion de la Hiérarchie des Catégories B2B

Ce guide explique comment gérer et afficher la hiérarchie des catégories B2B dans l'accueil de SagaKore.

## Vue d'ensemble

La solution permet de :
1. Structurer les catégories B2B selon leur hiérarchie (niveau 0 = principales, niveau 1+ = sous-catégories)
2. Afficher cette hiérarchie dans l'accueil avec un design cohérent
3. Synchroniser les catégories B2B avec les catégories locales

## Structure des Données

Les catégories B2B ont la structure suivante :
```json
{
  "id": 4,
  "name": "Frais Libre Service",
  "slug": "frais-libre-service",
  "level": 0,  // 0 = catégorie principale, 1+ = sous-catégorie
  "parent": null,  // ID du parent (null pour les principales)
  "order": 1,
  "is_rayon": true,
  "rayon_type": "frais_libre_service",
  "children": []  // Sous-catégories (niveau 1)
}
```

## Composants Créés

### 1. Utilitaires (`inventory/category_utils.py`)

#### `build_category_hierarchy(categories_data)`
Construit une hiérarchie de catégories à partir des données B2B JSON.

**Utilisation :**
```python
from inventory.category_utils import build_category_hierarchy

categories_data = [...]  # Liste de catégories B2B
hierarchy = build_category_hierarchy(categories_data)
# Retourne : {'main_categories': [...], 'total_main': X, 'total_sub': Y}
```

#### `get_b2b_categories_hierarchy()`
Récupère la hiérarchie des catégories B2B depuis la base de données (via ExternalCategory).

**Utilisation :**
```python
from inventory.category_utils import get_b2b_categories_hierarchy

hierarchy = get_b2b_categories_hierarchy()
# Retourne la hiérarchie complète avec les catégories locales mappées
```

#### `sync_b2b_categories_to_local(categories_data)`
Synchronise les catégories B2B avec les catégories locales.

**Utilisation :**
```python
from inventory.category_utils import sync_b2b_categories_to_local

categories_data = [...]  # Liste de catégories B2B
stats = sync_b2b_categories_to_local(categories_data)
# Retourne : {'created': X, 'updated': Y, 'total': Z}
```

### 2. API Endpoints

#### GET `/api/inventory/categories/b2b-hierarchy/`
Retourne la hiérarchie des catégories B2B organisée par niveau.

**Réponse :**
```json
{
  "main_categories": [
    {
      "id": 4,
      "name": "Frais Libre Service",
      "slug": "frais-libre-service",
      "level": 0,
      "order": 1,
      "children": [
        {
          "id": 5,
          "name": "Boucherie",
          "slug": "boucherie",
          "level": 1,
          "order": 1
        }
      ]
    }
  ],
  "total_main": 18,
  "total_sub": 120
}
```

#### POST `/api/inventory/categories/sync-hierarchy/`
Synchronise la hiérarchie des catégories B2B à partir des données JSON.

**Corps de la requête :**
```json
[
  {
    "id": 4,
    "name": "Frais Libre Service",
    "slug": "frais-libre-service",
    "level": 0,
    "parent": null,
    "order": 1
  },
  {
    "id": 5,
    "name": "Boucherie",
    "slug": "boucherie",
    "level": 1,
    "parent": 4,
    "order": 1
  }
]
```

### 3. Vue de l'Accueil

La vue `SupplierListView` a été modifiée pour inclure les catégories B2B dans le contexte :

```python
# Dans suppliers/views.py
from inventory.category_utils import get_b2b_categories_hierarchy

b2b_hierarchy = get_b2b_categories_hierarchy()
context['b2b_categories'] = b2b_hierarchy.get('main_categories', [])
context['b2b_total_main'] = b2b_hierarchy.get('total_main', 0)
context['b2b_total_sub'] = b2b_hierarchy.get('total_sub', 0)
```

### 4. Template

Le composant `_b2b_categories_hierarchy.html` affiche :
- Les 8 premières catégories principales B2B
- Pour chaque catégorie principale, les 3 premières sous-catégories
- Un bouton pour afficher toutes les catégories (si > 8)
- Un design responsive avec Tailwind CSS

## Flux de Synchronisation

### Option 1 : Synchronisation via API

1. Récupérer les catégories B2B depuis l'API externe
2. Appeler `POST /api/inventory/categories/sync-hierarchy/` avec les données
3. Les catégories sont créées/mises à jour dans la base locale
4. Les mappings ExternalCategory sont créés/mis à jour

### Option 2 : Synchronisation via Script

```python
from inventory.category_utils import sync_b2b_categories_to_local
import requests

# Récupérer les catégories depuis l'API B2B
response = requests.get('https://api-b2b.example.com/categories/')
categories_data = response.json()

# Synchroniser
stats = sync_b2b_categories_to_local(categories_data)
print(f"Créées: {stats['created']}, Mises à jour: {stats['updated']}")
```

## Affichage dans l'Accueil

Les catégories B2B sont automatiquement affichées dans l'accueil si :
1. Des catégories B2B sont synchronisées (via ExternalCategory)
2. Le template `supplier_list.html` inclut le composant `_b2b_categories_hierarchy.html`

### Personnalisation

Pour modifier l'affichage :
1. Éditer `suppliers/templates/suppliers/components/_b2b_categories_hierarchy.html`
2. Ajuster le nombre de catégories affichées (actuellement 8 principales)
3. Modifier les couleurs/styles selon votre charte graphique

## Exemple d'Utilisation Complète

```python
# 1. Récupérer les catégories B2B depuis l'API
import requests
from inventory.category_utils import sync_b2b_categories_to_local

api_url = "https://www.bolibanastock.com/api/v1/categories/"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

response = requests.get(api_url, headers=headers)
categories_data = response.json()

# 2. Synchroniser avec la base locale
stats = sync_b2b_categories_to_local(categories_data)
print(f"Synchronisation terminée: {stats}")

# 3. Récupérer la hiérarchie pour affichage
from inventory.category_utils import get_b2b_categories_hierarchy

hierarchy = get_b2b_categories_hierarchy()
print(f"Catégories principales: {hierarchy['total_main']}")
print(f"Sous-catégories: {hierarchy['total_sub']}")
```

## Notes Importantes

1. **Mapping ExternalCategory** : Les catégories B2B doivent être mappées avec des catégories locales via `ExternalCategory`
2. **Ordre d'affichage** : Les catégories sont triées par le champ `order`
3. **Hiérarchie** : Seules les catégories de niveau 0 sont affichées comme principales, les autres sont des sous-catégories
4. **Performance** : La fonction `get_b2b_categories_hierarchy()` utilise `select_related` et `prefetch_related` pour optimiser les requêtes

## Dépannage

### Les catégories B2B ne s'affichent pas
1. Vérifier que des `ExternalCategory` existent dans la base
2. Vérifier que les catégories locales associées existent
3. Vérifier les logs Django pour les erreurs

### Erreur lors de la synchronisation
1. Vérifier le format des données JSON
2. Vérifier que les slugs sont uniques
3. Vérifier les relations parent/enfant

## Prochaines Étapes

- [ ] Ajouter un filtre par rayon_type dans l'interface
- [ ] Implémenter la recherche dans les catégories B2B
- [ ] Ajouter des statistiques de produits par catégorie B2B
- [ ] Créer une vue dédiée pour explorer la hiérarchie complète


