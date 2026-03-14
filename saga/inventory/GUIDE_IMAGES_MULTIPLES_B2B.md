# Guide : Gestion des Images Multiples B2B

## Vue d'ensemble

Le service de synchronisation B2B gère maintenant automatiquement plusieurs images par produit, comme dans B2C. Les images sont téléchargées, optimisées et stockées dans la galerie du produit.

## Format des Données API B2B

L'API B2B peut retourner les images sous différents formats :

### Format 1 : Liste d'images (`images`)

```json
{
  "id": 47,
  "name": "Produit Exemple",
  "images": [
    "https://api.example.com/images/product-47-1.jpg",
    "https://api.example.com/images/product-47-2.jpg",
    "https://api.example.com/images/product-47-3.jpg"
  ]
}
```

### Format 2 : Liste d'URLs (`image_urls`)

```json
{
  "id": 47,
  "name": "Produit Exemple",
  "image_urls": [
    "https://api.example.com/images/product-47-1.jpg",
    "https://api.example.com/images/product-47-2.jpg"
  ]
}
```

### Format 3 : Galerie (`gallery`)

```json
{
  "id": 47,
  "name": "Produit Exemple",
  "gallery": [
    "https://api.example.com/images/product-47-1.jpg",
    "https://api.example.com/images/product-47-2.jpg"
  ]
}
```

### Format 4 : Image unique (compatibilité)

```json
{
  "id": 47,
  "name": "Produit Exemple",
  "image_url": "https://api.example.com/images/product-47.jpg"
}
```

Ou :

```json
{
  "id": 47,
  "name": "Produit Exemple",
  "image": "https://api.example.com/images/product-47.jpg",
  "main_image": "https://api.example.com/images/product-47.jpg",
  "photo": "https://api.example.com/images/product-47.jpg"
}
```

## Traitement des Images

### Image Principale

- **Première image** de la liste → `product.image` (ImageField principal)
- Si une seule image est fournie, elle devient l'image principale
- Ordre : `0` (première position)

### Images de Galerie

- **Images supplémentaires** (à partir de la 2ème) → `ImageProduct` (modèle de galerie)
- Chaque image est stockée avec un `ordre` unique (1, 2, 3, ...)
- Accessible via `product.images.all()` (relation ForeignKey)

## Stockage

### Structure de Données

1. **Image Principale** (`product.image`)
   - Stockée dans le champ `image` du modèle `Product`
   - Chemin : `products/{product_id}/b2b_{product_id}_{slug}.{ext}`

2. **Images de Galerie** (`ImageProduct`)
   - Stockées dans le modèle `ImageProduct`
   - Relation : `product.images.all()`
   - Champs :
     - `image` : ImageField
     - `ordre` : Position dans la galerie (1, 2, 3, ...)
     - `created_at` / `updated_at` : Horodatage

3. **Spécifications** (`product.specifications`)
   - `b2b_image_urls` : Liste de toutes les URLs originales
   - `b2b_image_url` : URL de l'image principale (compatibilité)

### Optimisation

Les images sont automatiquement :
- **Converties en RGB** (pour compatibilité)
- **Compressées** pour réduire la taille
- **Validées** (format, taille, type MIME)
- **Nommées** de manière unique : `b2b_{product_id}_{slug}.{ext}`

## Exemple de Synchronisation

### Données API B2B

```json
{
  "id": 47,
  "name": "Riz Premium",
  "images": [
    "https://api.example.com/images/riz-1.jpg",
    "https://api.example.com/images/riz-2.jpg",
    "https://api.example.com/images/riz-3.jpg"
  ]
}
```

### Résultat dans SagaKore

```python
product = Product.objects.get(external_id=47)

# Image principale
product.image  # → b2b_47_riz-premium.jpg

# Images de galerie
product.images.all()  # → [ImageProduct(ordre=1), ImageProduct(ordre=2)]

# URLs originales
product.specifications['b2b_image_urls']
# → [
#     "https://api.example.com/images/riz-1.jpg",
#     "https://api.example.com/images/riz-2.jpg",
#     "https://api.example.com/images/riz-3.jpg"
#   ]
```

## Utilisation dans les Templates

### Afficher l'Image Principale

```django
{% if product.image %}
    <img src="{{ product.image.url }}" alt="{{ product.title }}">
{% endif %}
```

### Afficher la Galerie

```django
{% for image in product.images.all %}
    <img src="{{ image.image.url }}" alt="{{ product.title }} - Image {{ image.ordre }}">
{% endfor %}
```

### Afficher avec Swiper (Carousel)

```django
<div class="swiper product-gallery">
    <div class="swiper-wrapper">
        {% if product.image %}
            <div class="swiper-slide">
                <img src="{{ product.image.url }}" alt="{{ product.title }}">
            </div>
        {% endif %}
        {% for image in product.images.all %}
            <div class="swiper-slide">
                <img src="{{ image.image.url }}" alt="{{ product.title }} - Image {{ image.ordre }}">
            </div>
        {% endfor %}
    </div>
    <div class="swiper-pagination"></div>
</div>
```

## Gestion des Erreurs

### Image Non Disponible

Si une image ne peut pas être téléchargée :
- **Log d'erreur** enregistré
- **Synchronisation continue** (ne bloque pas le processus)
- **Image suivante** traitée normalement

### Image Invalide

Si une URL ne retourne pas une image valide :
- **Vérification du Content-Type** (doit commencer par `image/`)
- **Validation du format** (JPEG, PNG, WebP, GIF)
- **Log d'avertissement** si invalide

### Mise à Jour

Lors d'une resynchronisation :
- **Images existantes** sont mises à jour si l'ordre correspond
- **Nouvelles images** sont ajoutées
- **Images supprimées** dans l'API ne sont pas supprimées automatiquement (conservation)

## Configuration

### Désactiver le Téléchargement d'Images

Pour désactiver le téléchargement automatique, modifiez dans `services.py` :

```python
# Commenter ou supprimer cette section :
# if image_urls:
#     # ... code de téléchargement ...
```

### Limiter le Nombre d'Images

Pour limiter le nombre d'images téléchargées :

```python
# Dans create_or_update_product, après image_urls = [...]
MAX_IMAGES = 5
image_urls = image_urls[:MAX_IMAGES]
```

### Changer l'Ordre

Pour inverser l'ordre des images :

```python
image_urls = image_urls[::-1]  # Inverser la liste
```

## Dépannage

### Les Images Ne Sont Pas Téléchargées

1. **Vérifier les logs** : `logger.error` pour les erreurs de téléchargement
2. **Vérifier les URLs** : Les URLs doivent être accessibles publiquement
3. **Vérifier les permissions** : Le système de fichiers doit être accessible en écriture

### Images Dupliquées

Si des images sont dupliquées :
- Vérifier que l'API B2B ne retourne pas d'URLs dupliquées
- Vérifier que `order` est correctement géré

### Images Manquantes

Si certaines images ne sont pas téléchargées :
- Vérifier les logs pour les erreurs spécifiques
- Vérifier que les URLs sont valides et accessibles
- Vérifier la limite de taille des fichiers

## Notes Importantes

1. **Performance** : Le téléchargement d'images peut ralentir la synchronisation
2. **Stockage** : Les images prennent de l'espace disque
3. **Réseau** : Assurez-vous d'avoir une connexion stable pour le téléchargement
4. **Timeout** : Les images sont téléchargées avec un timeout de 30 secondes
5. **Format** : Les images sont converties en RGB et compressées automatiquement

## Compatibilité avec B2C

Le système est compatible avec la gestion d'images B2C :
- Même modèle `ImageProduct`
- Même structure de galerie
- Même affichage dans les templates
- Même logique d'ordre

Les produits B2B et B2C utilisent le même système de galerie d'images.


