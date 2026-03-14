# 📦 Exploitation des Catégories Synchronisées depuis B2B

## 🎯 Vue d'ensemble

Les catégories récupérées depuis l'API B2B sont automatiquement synchronisées dans SagaKore via le service `ProductSyncService`. Ce document explique comment les exploiter dans votre projet.

## 🔄 Flux de Synchronisation

```
1. Appel API B2B → get_categories_list()
   └─> Récupère les catégories depuis B2B

2. ProductSyncService.sync_categories()
   └─> Crée/met à jour les Category dans SagaKore
   └─> Crée les ExternalCategory pour le mapping

3. Les catégories sont disponibles dans SagaKore
   └─> Utilisables comme des Category normales
   └─> Avec mapping vers B2B via ExternalCategory
```

## 🛠️ Utilisation dans le Code

### 1. Récupérer les Catégories Synchronisées

```python
from inventory.utils import get_synced_categories, get_synced_categories_for_user
from inventory.models import InventoryConnection

# Toutes les catégories synchronisées
all_synced = get_synced_categories()

# Catégories pour un utilisateur spécifique
connection = InventoryConnection.objects.filter(user=request.user).first()
user_synced = get_synced_categories_for_user(request.user)
```

### 2. Vérifier si une Catégorie est Synchronisée

```python
from inventory.utils import is_category_synced_from_b2b

category = Category.objects.get(slug='telephones')
is_synced = is_category_synced_from_b2b(category, connection)
```

### 3. Récupérer les Produits d'une Catégorie Synchronisée

```python
from inventory.utils import get_products_in_synced_category

# Les produits sont automatiquement filtrés selon la synchronisation
products = get_products_in_synced_category(category, connection)
```

### 4. Construire l'Arbre Hiérarchique

```python
from inventory.utils import get_category_tree_from_b2b

# Récupère l'arbre complet avec parent/enfant
tree = get_category_tree_from_b2b(connection)
# Retourne une liste de dictionnaires avec structure hiérarchique
```

## 📍 Vues Disponibles

### Liste des Catégories Synchronisées

**URL**: `/inventory/categories/`

Affiche toutes les catégories synchronisées depuis B2B avec leur arbre hiérarchique.

```python
# Dans votre template
{% for category in synced_categories %}
    <a href="{% url 'inventory:category_detail_synced' category.slug %}">
        {{ category.name }}
    </a>
{% endfor %}
```

### Détail d'une Catégorie

**URL**: `/inventory/categories/<slug>/`

Affiche les détails d'une catégorie et tous ses produits synchronisés.

```python
# Dans votre template
<h1>{{ category.name }}</h1>
{% if is_synced %}
    <span class="badge">Synchronisé depuis B2B</span>
{% endif %}

{% for product in products %}
    <div>{{ product.title }} - {{ product.price }} FCFA</div>
{% endfor %}
```

### API JSON - Arbre des Catégories

**URL**: `/inventory/api/categories/tree/`

Retourne l'arbre complet des catégories en JSON (nécessite authentification).

```javascript
// Exemple d'utilisation en JavaScript
fetch('/inventory/api/categories/tree/', {
    headers: {
        'Authorization': 'Bearer ' + token
    }
})
.then(response => response.json())
.then(data => {
    console.log(data.categories); // Arbre des catégories
});
```

### API JSON - Produits d'une Catégorie

**URL**: `/inventory/api/categories/<id>/products/`

Retourne les produits d'une catégorie en JSON.

```javascript
fetch('/inventory/api/categories/1/products/')
.then(response => response.json())
.then(data => {
    console.log(data.products); // Liste des produits
    console.log(data.is_synced); // Si synchronisée depuis B2B
});
```

## 🎨 Utilisation dans les Templates

### Context Processor Automatique

Les catégories synchronisées sont automatiquement disponibles dans tous les templates via le context processor :

```django
{# Dans n'importe quel template #}
{% if has_synced_categories %}
    <h2>Catégories depuis B2B</h2>
    {% for category in synced_categories %}
        <a href="{% url 'inventory:category_detail_synced' category.slug %}">
            {{ category.name }}
        </a>
    {% endfor %}
{% endif %}
```

### Filtrer les Catégories dans les Vues Existantes

Vous pouvez adapter vos vues existantes pour utiliser les catégories synchronisées :

```python
# Dans product/views.py
from inventory.utils import is_category_synced_from_b2b, get_products_in_synced_category

def product_list_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    
    # Vérifier si synchronisée
    connection = InventoryConnection.objects.filter(
        user=request.user,
        is_active=True
    ).first() if request.user.is_authenticated else None
    
    if connection and is_category_synced_from_b2b(category, connection):
        # Utiliser les produits synchronisés
        products = get_products_in_synced_category(category, connection)
    else:
        # Comportement normal
        products = category.products.filter(is_available=True)
    
    return render(request, 'product/list.html', {
        'category': category,
        'products': products,
    })
```

## 🔍 Exemples d'Utilisation

### Exemple 1: Menu de Navigation avec Catégories B2B

```django
{# templates/nav.html #}
<nav>
    <ul>
        {% for category in synced_categories %}
            {% if not category.parent %}
                <li>
                    <a href="{% url 'inventory:category_detail_synced' category.slug %}">
                        {{ category.name }}
                    </a>
                    {% if category.children %}
                        <ul>
                            {% for child in category.children %}
                                <li>
                                    <a href="{% url 'inventory:category_detail_synced' child.slug %}">
                                        {{ child.name }}
                                    </a>
                                </li>
                            {% endfor %}
                        </ul>
                    {% endif %}
                </li>
            {% endif %}
        {% endfor %}
    </ul>
</nav>
```

### Exemple 2: Widget de Catégories Synchronisées

```python
# Dans une vue
from inventory.utils import get_synced_categories_for_user

def dashboard(request):
    if request.user.is_authenticated:
        synced_categories = get_synced_categories_for_user(request.user)
    else:
        synced_categories = []
    
    return render(request, 'dashboard.html', {
        'synced_categories': synced_categories,
    })
```

### Exemple 3: API REST pour Mobile

```python
# Dans inventory/api/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from inventory.utils import get_synced_categories, get_category_tree_from_b2b

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    
    @action(detail=False, methods=['get'])
    def synced(self, request):
        """Retourne les catégories synchronisées depuis B2B"""
        connection = InventoryConnection.objects.filter(
            user=request.user,
            is_active=True
        ).first()
        
        if connection:
            categories = get_synced_categories(connection)
            tree = get_category_tree_from_b2b(connection)
            return Response({
                'categories': CategorySerializer(categories, many=True).data,
                'tree': tree
            })
        return Response({'error': 'No active connection'}, status=404)
```

## 📊 Structure des Données

### ExternalCategory

Chaque catégorie synchronisée a un mapping :

```python
external_category = ExternalCategory.objects.get(category=category)
# external_category.external_id → ID dans B2B
# external_category.external_parent_id → ID parent dans B2B
# external_category.connection → Connexion utilisée
```

### Arbre Hiérarchique

```python
tree = get_category_tree_from_b2b(connection)
# Retourne:
[
    {
        'id': 1,
        'external_id': 10,
        'name': 'Électronique',
        'slug': 'electronique',
        'parent_id': None,
        'category': <Category instance>,
        'children': [
            {
                'id': 2,
                'external_id': 11,
                'name': 'Téléphones',
                'slug': 'telephones',
                'parent_id': 10,
                'category': <Category instance>,
                'children': []
            }
        ]
    }
]
```

## 🚀 Commandes Utiles

### Synchroniser les Catégories

```bash
# Synchroniser toutes les catégories
python manage.py sync_categories_from_inventory

# Pour une connexion spécifique
python manage.py sync_categories_from_inventory --connection-id 1
```

### Vérifier les Catégories Synchronisées

```python
# Dans le shell Django
from inventory.models import ExternalCategory
from inventory.utils import get_synced_categories

# Compter les catégories synchronisées
ExternalCategory.objects.count()

# Lister toutes les catégories synchronisées
categories = get_synced_categories()
for cat in categories:
    print(f"{cat.name} (ID externe: {cat.external_category.external_id})")
```

## ⚠️ Notes Importantes

1. **Hiérarchie Parent/Enfant** : Les relations parent/enfant sont gérées automatiquement lors de la synchronisation
2. **Multi-connexions** : Un même utilisateur peut avoir plusieurs connexions, les catégories sont filtrées par connexion
3. **Performance** : Utilisez `select_related` et `prefetch_related` pour optimiser les requêtes
4. **Compatibilité** : Les catégories synchronisées fonctionnent comme des Category normales de Django

## 🔗 Intégration avec les Vues Existantes

Pour intégrer les catégories B2B dans vos vues existantes :

```python
# product/views.py
from inventory.utils import is_category_synced_from_b2b, get_products_in_synced_category

def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    
    # Détecter si synchronisée et adapter le comportement
    connection = get_user_connection(request.user) if request.user.is_authenticated else None
    is_synced = is_category_synced_from_b2b(category, connection)
    
    if is_synced:
        products = get_products_in_synced_category(category, connection)
    else:
        products = category.products.filter(is_available=True)
    
    return render(request, 'product/category.html', {
        'category': category,
        'products': products,
        'is_synced': is_synced,
    })
```

