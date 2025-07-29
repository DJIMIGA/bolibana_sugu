# 📱 Guide d'ajout de nouveaux téléphones

## 🎯 Vue d'ensemble

Cette commande permet d'ajouter facilement de nouveaux téléphones au système BoliBana. Elle supporte deux modes :
- **Mode fichier JSON** : Ajout en lot depuis un fichier JSON
- **Mode interactif** : Ajout manuel téléphone par téléphone

## 🚀 Utilisation

### 1. Mode fichier JSON (recommandé pour les lots)

```bash
# Ajouter des téléphones depuis un fichier JSON
python manage.py add_phones --file product/fixtures/new_phones_sample.json

# Spécifier une catégorie et un fournisseur différents
python manage.py add_phones --file phones.json --category 2 --supplier 3
```

### 2. Mode interactif (pour un téléphone unique)

```bash
# Ajouter un téléphone manuellement
python manage.py add_phones --interactive

# Spécifier une catégorie et un fournisseur
python manage.py add_phones --interactive --category 1 --supplier 1
```

## 📋 Structure du fichier JSON

### Format requis

```json
[
  {
    "title": "Nom complet du téléphone",
    "description": "Description détaillée du produit",
    "price": 85000,
    "brand": "Marque",
    "model": "Modèle",
    "operating_system": "Système d'exploitation",
    "screen_size": 6.5,
    "resolution": "2400x1080",
    "processor": "Processeur",
    "battery_capacity": 5000,
    "camera_main": "Caméra principale",
    "camera_front": "Caméra frontale",
    "network": "4G LTE",
    "storage": 128,
    "ram": 6,
    "color": "Couleur",
    "stock": 15,
    "sku": "Code SKU",
    "is_new": true,
    "box_included": true,
    "accessories": "Liste des accessoires",
    "condition": "new",
    "has_warranty": true,
    "is_trending": true
  }
]
```

### Champs obligatoires

- `title` : Titre du téléphone
- `price` : Prix en FCFA
- `brand` : Marque
- `model` : Modèle

### Champs optionnels avec valeurs par défaut

- `description` : "" (vide)
- `operating_system` : "Android"
- `screen_size` : 6.0
- `resolution` : "1920x1080"
- `processor` : "Inconnu"
- `battery_capacity` : 3000
- `camera_main` : "Inconnue"
- `camera_front` : "Inconnue"
- `network` : "4G"
- `storage` : 64
- `ram` : 4
- `color` : "Noir"
- `stock` : 0
- `sku` : "" (vide)
- `is_new` : true
- `box_included` : true
- `accessories` : "" (vide)
- `condition` : "new"
- `has_warranty` : true
- `is_trending` : false

## 🔧 Prérequis

### 1. Catégories existantes

Assurez-vous qu'une catégorie pour les téléphones existe :

```bash
# Vérifier les catégories existantes
python manage.py shell
```

```python
from product.models import Category
Category.objects.filter(name__icontains='téléphone').values('id', 'name')
```

### 2. Fournisseurs existants

Vérifiez qu'au moins un fournisseur existe :

```python
from suppliers.models import Supplier
Supplier.objects.all().values('id', 'company_name')
```

### 3. Couleurs disponibles

Les couleurs sont créées automatiquement, mais vous pouvez les pré-créer :

```python
from product.models import Color
Color.objects.all().values('name', 'code')
```

## 📊 Exemples d'utilisation

### Exemple 1 : Ajout en lot

```bash
# Créer un fichier JSON avec vos téléphones
# Puis lancer la commande
python manage.py add_phones --file mes_telephones.json
```

### Exemple 2 : Ajout interactif

```bash
python manage.py add_phones --interactive
```

Réponses aux questions :
```
📝 Titre du téléphone: Samsung Galaxy A15
📄 Description (optionnel): Excellent téléphone économique
💰 Prix (FCFA): 85000
📦 Stock disponible: 15
🏷️ SKU (optionnel): SAM-A15-128-6-BK
🏭 Marque: Samsung
📱 Modèle: Galaxy A15 4G
💻 Système d'exploitation (défaut: Android): Android 14
📺 Taille d'écran en pouces (défaut: 6.0): 6.5
🖥️ Résolution (défaut: 1920x1080): 2400x1080
⚡ Processeur (défaut: Inconnu): MediaTek Helio G99
🔋 Capacité batterie en mAh (défaut: 3000): 5000
📷 Caméra principale (défaut: Inconnue): 50MP + 5MP + 2MP
📸 Caméra frontale (défaut: Inconnue): 13MP
📡 Réseau (défaut: 4G): 4G LTE
💾 Stockage en GB (défaut: 64): 128
🧠 RAM en GB (défaut: 4): 6
🎨 Couleur (défaut: Noir): Noir
🆕 Neuf? (y/n, défaut: y): y
📦 Boîte incluse? (y/n, défaut: y): y
🔧 Accessoires (optionnel): Téléphone, Chargeur, Câble USB-C
🔢 IMEI (optionnel): 
```

## 🔍 Vérification

Après l'ajout, vérifiez que les téléphones ont été créés :

```bash
# Dans l'admin Django
python manage.py runserver
# Puis aller sur http://localhost:8000/admin/

# Ou via la ligne de commande
python manage.py shell
```

```python
from product.models import Product, Phone
Product.objects.filter(brand='Samsung').count()
Phone.objects.filter(brand='Samsung').count()
```

## 🛠️ Dépannage

### Erreur : "Category matching query does not exist"

```bash
# Vérifier les catégories disponibles
python manage.py shell
```

```python
from product.models import Category
Category.objects.all().values('id', 'name')
```

### Erreur : "Supplier matching query does not exist"

```bash
# Vérifier les fournisseurs disponibles
python manage.py shell
```

```python
from suppliers.models import Supplier
Supplier.objects.all().values('id', 'company_name')
```

### Erreur de format JSON

Vérifiez que votre fichier JSON est valide :

```bash
# Tester la validité du JSON
python -m json.tool votre_fichier.json
```

## 📈 Bonnes pratiques

### 1. Préparation des données

- Utilisez des SKU uniques et descriptifs
- Incluez des descriptions détaillées
- Spécifiez tous les accessoires inclus
- Utilisez des prix cohérents

### 2. Gestion des images

Les images peuvent être ajoutées via l'admin Django après la création des produits.

### 3. Vérification des données

Toujours vérifier les données créées avant de les mettre en production.

## 🔄 Mise à jour des produits existants

La commande utilise `update_or_create`, donc :
- Si le titre existe déjà, le produit sera mis à jour
- Si le titre n'existe pas, un nouveau produit sera créé

## 📞 Support

Pour toute question ou problème, consultez :
- Les logs Django
- L'admin Django pour vérifier les données
- La documentation des modèles dans `product/models.py` 