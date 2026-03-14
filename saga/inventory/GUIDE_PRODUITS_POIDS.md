# Guide : Gestion des Produits au Poids B2B

## Vue d'ensemble

Le service de synchronisation B2B gère maintenant automatiquement les produits vendus au poids. Ces produits sont détectés et traités différemment des produits vendus à l'unité.

## Détection des Produits au Poids

Un produit est considéré comme "au poids" si l'API B2B retourne l'un de ces indicateurs :

- `sold_by_weight: true`
- `by_weight: true`
- `unit_type: "weight"`, `"kg"`, `"kilogram"`, ou `"poids"`
- `selling_unit: "weight"`, `"kg"`, `"kilogram"`, ou `"poids"`

## Gestion du Stock

### Produits au Poids

- **Stock disponible** : Stocké dans le champ `weight` (en kg)
- **Stock en unités** : 
  - Si `is_salam=True` : `stock = 0` (produit sur commande)
  - Sinon : `stock = int(weight_available)` (valeur symbolique pour indiquer la disponibilité)
- **Spécifications** : 
  - `sold_by_weight: true`
  - `unit_type: "weight"`
  - `available_weight_kg`: poids disponible en kg
  - `price_per_kg`: prix au kilogramme

### Produits Normaux (à l'unité)

- **Stock** : Stocké dans le champ `stock` (entier)
- **Poids** : Stocké dans `weight` si fourni (pour la livraison)

## Gestion du Prix

### Produits au Poids

- Le prix est interprété comme **prix au kilogramme**
- Stocké dans `price` (prix unitaire)
- Également stocké dans `specifications.price_per_kg` pour référence

### Produits Normaux

- Le prix est le **prix unitaire** du produit

## Produits Salam (Sur Commande)

Les produits au poids sont automatiquement marqués comme `is_salam=True` car ils sont généralement vendus sur commande. Cela signifie :

- `can_order()` retourne toujours `True`
- `has_stock()` retourne toujours `True`
- Le stock en unités est à `0`
- Le poids disponible est stocké dans `weight` et `specifications.available_weight_kg`

## Exemple de Données B2B

### Produit au Poids

```json
{
  "id": 47,
  "name": "Riz Premium",
  "price": "2500",
  "stock": "12.000",
  "unit_type": "kg",
  "sold_by_weight": true,
  "description": "Riz de qualité supérieure"
}
```

**Résultat dans SagaKore :**
- `title`: "Riz Premium"
- `price`: 2500 (FCFA par kg)
- `stock`: 12 (unité symbolique)
- `weight`: 12.0 (kg disponibles)
- `is_salam`: `True`
- `specifications`:
  - `sold_by_weight`: `true`
  - `unit_type`: `"weight"`
  - `available_weight_kg`: 12.0
  - `price_per_kg`: 2500

### Produit Normal

```json
{
  "id": 48,
  "name": "Téléphone",
  "price": "150000",
  "stock": "5",
  "unit_type": "unit",
  "description": "Smartphone"
}
```

**Résultat dans SagaKore :**
- `title`: "Téléphone"
- `price`: 150000 (FCFA par unité)
- `stock`: 5 (unités)
- `is_salam`: `False`

## Utilisation dans l'Interface

### Affichage du Prix

Pour les produits au poids, vous pouvez afficher :
- Prix au kg : `{{ product.price }} FCFA/kg`
- Ou utiliser : `{{ product.specifications.price_per_kg }} FCFA/kg`

### Affichage du Stock

Pour les produits au poids :
```python
{% if product.specifications.sold_by_weight %}
    Disponible : {{ product.weight }} kg
{% else %}
    En stock : {{ product.stock }} unités
{% endif %}
```

### Commande

Les produits au poids (marqués `is_salam=True`) :
- Peuvent toujours être commandés
- Le système de réservation de stock ne s'applique pas
- La quantité commandée peut être en kg

## Configuration

### Désactiver le Mode Salam Automatique

Si vous ne voulez pas que tous les produits au poids soient automatiquement en mode Salam, modifiez dans `services.py` :

```python
# Au lieu de :
is_salam_product = sold_by_weight

# Utilisez :
is_salam_product = external_data.get('is_salam', False) or \
                  external_data.get('made_to_order', False) or \
                  external_data.get('on_demand', False)
```

### Ajuster la Détection

Pour ajouter d'autres indicateurs de produits au poids, modifiez :

```python
sold_by_weight = external_data.get('sold_by_weight', False) or \
                external_data.get('by_weight', False) or \
                external_data.get('unit_type', '').lower() in ['weight', 'kg', 'kilogram', 'poids'] or \
                external_data.get('selling_unit', '').lower() in ['weight', 'kg', 'kilogram', 'poids'] or \
                external_data.get('votre_nouveau_champ', False)  # Ajoutez ici
```

## Notes Importantes

1. **Conversion des Types** : Le service convertit automatiquement les chaînes comme `'12.000'` en nombres
2. **Stock Symbolique** : Pour les produits au poids non-Salam, le stock en unités est une valeur symbolique basée sur le poids disponible
3. **Prix** : Le prix est toujours stocké comme prix unitaire, même pour les produits au poids (prix au kg)
4. **Spécifications** : Les informations sur le type de vente sont stockées dans `specifications` pour faciliter l'affichage

## Dépannage

### Le produit n'est pas détecté comme "au poids"

Vérifiez que l'API B2B retourne bien l'un des indicateurs listés ci-dessus. Vous pouvez ajouter des logs pour déboguer :

```python
logger.info(f"Produit {external_id}: sold_by_weight={sold_by_weight}, unit_type={external_data.get('unit_type')}")
```

### Le stock n'est pas correct

Vérifiez que le stock dans l'API B2B est bien en kg pour les produits au poids. Le service convertit automatiquement les chaînes en nombres.

### Le prix n'est pas au kg

Le prix est toujours stocké comme prix unitaire. Pour les produits au poids, c'est le prix au kg. Utilisez `specifications.price_per_kg` pour l'affichage.

