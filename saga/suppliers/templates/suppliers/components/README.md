# Composants de l'application Suppliers

Ce dossier contient les composants réutilisables pour l'affichage des fournisseurs et des produits.

## Structure des composants

### `_filters.html`
Composant de filtrage des produits avec les options suivantes :
- Filtre par marque
- Filtre par modèle
- Filtre par stockage
- Filtre par RAM
- Filtre par prix (min/max)
- Bouton de réinitialisation

Utilisation :
```django
{% include "suppliers/components/_filters.html" with is_detail=True %}
```
ou
```django
{% include "suppliers/components/_filters.html" with is_detail=False %}
```

### `_product_grid.html`
Composant d'affichage de la grille des produits avec :
- Grille responsive (1 à 4 colonnes selon la taille d'écran)
- Pagination
- Message si aucun produit disponible

Utilisation :
```django
{% include "suppliers/components/_product_grid.html" %}
```

### `product_card.html`
Composant d'affichage d'un produit individuel avec :
- Image du produit
- Titre
- Caractéristiques (stockage, RAM)
- Prix
- Bouton d'ajout au panier

Utilisation :
```django
{% include "suppliers/components/product_card.html" with product=product %}
```

## Intégration HTMX

Les composants utilisent HTMX pour les mises à jour dynamiques :
- Les filtres déclenchent une requête HTMX lors du changement
- La grille est mise à jour sans rechargement complet de la page
- La pagination est gérée via HTMX

## Variables de contexte requises

### Pour `_filters.html`
- `brands` : Liste des marques disponibles
- `models` : Liste des modèles disponibles
- `storages` : Liste des capacités de stockage disponibles
- `rams` : Liste des capacités RAM disponibles
- `selected_brand` : Marque sélectionnée
- `selected_model` : Modèle sélectionné
- `selected_storage` : Stockage sélectionné
- `selected_ram` : RAM sélectionnée
- `selected_price_min` : Prix minimum sélectionné
- `selected_price_max` : Prix maximum sélectionné
- `is_detail` : Booléen indiquant si on est dans la vue détaillée
- `slug` : Slug de la marque (uniquement pour la vue détaillée)

### Pour `_product_grid.html`
- `products` : Liste paginée des produits à afficher

### Pour `product_card.html`
- `product` : Objet produit à afficher 