# 📱 Guide d'ajout de nouveaux téléphones

## 🎯 Vue d'ensemble

Cette commande permet d'ajouter facilement de nouveaux téléphones au système BoliBana. Elle supporte trois modes :
- **Mode fichier JSON** : Ajout en lot depuis un fichier JSON
- **Mode interactif** : Ajout manuel téléphone par téléphone
- **Mode commande intégrée** : Ajout direct avec données intégrées dans le code

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

### 3. Mode commande intégrée (pour des modèles spécifiques)

Cette méthode est idéale pour ajouter des modèles spécifiques avec toutes leurs variantes, sans fichier externe.

#### Exemple : Samsung Galaxy F16

```bash
# Ajouter tous les variants Samsung Galaxy F16
python manage.py add_samsung_f16_phones
```

**Avantages de cette méthode :**
- ✅ Pas de fichier externe nécessaire
- ✅ Fonctionne parfaitement sur Heroku
- ✅ Titres uniques générés automatiquement (ROM + RAM + Couleur)
- ✅ Couleurs pré-créées automatiquement
- ✅ Gestion des stocks différenciée par variante

#### Créer une nouvelle commande intégrée

Pour ajouter un nouveau modèle, créez une nouvelle commande basée sur `add_samsung_f16_phones.py` :

```python
# Exemple de structure pour un nouveau modèle
class Command(BaseCommand):
    help = 'Ajoute les téléphones [Marque] [Modèle] avec toutes les variantes'

    def handle(self, *args, **options):
        # Définir les données des téléphones
        phones_data = [
            {
                "description": "Description du téléphone...",
                "price": 95000,
                "brand": "Marque",
                "model": "Modèle",
                "storage": 128,
                "ram": 4,
                "color": "Couleur",
                "stock": 25,
                "sku": "SKU-UNIQUE",
                # ... autres champs
            }
        ]
        
        # Logique d'ajout similaire à add_samsung_f16_phones.py
```

## 🎯 Quand utiliser quelle méthode ?

### 📁 Mode fichier JSON
**Utilisez cette méthode quand :**
- Vous avez beaucoup de téléphones différents à ajouter
- Les données viennent d'un export Excel/CSV converti en JSON
- Vous voulez réutiliser les données pour d'autres environnements
- Vous travaillez en local (pas sur Heroku)

### 💬 Mode interactif
**Utilisez cette méthode quand :**
- Vous ajoutez seulement 1-2 téléphones
- Vous voulez un contrôle total sur chaque champ
- Vous testez de nouvelles fonctionnalités
- Vous ajoutez des téléphones uniques

### 🔧 Mode commande intégrée
**Utilisez cette méthode quand :**
- Vous ajoutez un modèle spécifique avec toutes ses variantes
- Vous déployez sur Heroku (pas de fichier externe)
- Vous voulez des titres uniques automatiques (ROM + RAM + Couleur)
- Vous voulez une gestion des stocks différenciée
- Vous voulez que les couleurs soient pré-créées automatiquement

## 📱 Exemple concret : Samsung Galaxy F16

### Étape 1 : Ajouter les couleurs officielles

```bash
# Ajouter les couleurs officielles Samsung Galaxy F16
python manage.py add_samsung_colors
```

**Résultat :**
```
✅ Couleur créée: Noir Brillant (#1a1a1a)
✅ Couleur créée: Bleu Vibrant (#0066cc)
✅ Couleur créée: Vert Glamour (#00cc66)
```

### Étape 2 : Ajouter tous les variants

```bash
# Ajouter tous les variants Samsung Galaxy F16
python manage.py add_samsung_f16_phones
```

**Résultat :**
```
✅ Téléphone créé: Samsung Galaxy F16 128GB 4GB Noir Brillant
✅ Téléphone créé: Samsung Galaxy F16 128GB 6GB Noir Brillant
✅ Téléphone créé: Samsung Galaxy F16 128GB 8GB Noir Brillant
✅ Téléphone créé: Samsung Galaxy F16 128GB 4GB Bleu Vibrant
✅ Téléphone créé: Samsung Galaxy F16 128GB 6GB Bleu Vibrant
✅ Téléphone créé: Samsung Galaxy F16 128GB 8GB Bleu Vibrant
✅ Téléphone créé: Samsung Galaxy F16 128GB 4GB Vert Glamour
✅ Téléphone créé: Samsung Galaxy F16 128GB 6GB Vert Glamour
✅ Téléphone créé: Samsung Galaxy F16 128GB 8GB Vert Glamour

📱 Résumé: 9 téléphones créés, 0 mis à jour
```

### Variantes créées

| **Configuration** | **Titre unique** | **Prix** | **Stock** |
|-------------------|------------------|----------|-----------|
| 4GB + Noir Brillant | `Samsung Galaxy F16 128GB 4GB Noir Brillant` | 95,000 FCFA | 25 |
| 6GB + Noir Brillant | `Samsung Galaxy F16 128GB 6GB Noir Brillant` | 105,000 FCFA | 20 |
| 8GB + Noir Brillant | `Samsung Galaxy F16 128GB 8GB Noir Brillant` | 115,000 FCFA | 15 |
| 4GB + Bleu Vibrant | `Samsung Galaxy F16 128GB 4GB Bleu Vibrant` | 95,000 FCFA | 20 |
| 6GB + Bleu Vibrant | `Samsung Galaxy F16 128GB 6GB Bleu Vibrant` | 105,000 FCFA | 18 |
| 8GB + Bleu Vibrant | `Samsung Galaxy F16 128GB 8GB Bleu Vibrant` | 115,000 FCFA | 12 |
| 4GB + Vert Glamour | `Samsung Galaxy F16 128GB 4GB Vert Glamour` | 95,000 FCFA | 15 |
| 6GB + Vert Glamour | `Samsung Galaxy F16 128GB 6GB Vert Glamour` | 105,000 FCFA | 12 |
| 8GB + Vert Glamour | `Samsung Galaxy F16 128GB 8GB Vert Glamour` | 115,000 FCFA | 8 |

### Avantages de cette approche

- ✅ **Titres uniques** : Chaque variante a un titre distinctif
- ✅ **Couleurs en français** : Respect de la langue locale
- ✅ **Gestion des stocks intelligente** : Plus de stock pour les couleurs populaires
- ✅ **SKU uniques** : Codes produits distincts pour chaque variante
- ✅ **Fonctionne sur Heroku** : Pas de fichier externe nécessaire

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

## 🚀 Déploiement sur Heroku

### Problème avec les fichiers externes

Sur Heroku, les commandes avec `--file` ne fonctionnent pas car :
- Heroku ne peut pas accéder aux fichiers locaux
- Les fichiers n'existent que sur votre machine locale
- `heroku run` exécute les commandes dans l'environnement distant

### Solution recommandée : Mode commande intégrée

Pour ajouter des produits sur Heroku, utilisez le **mode commande intégrée** :

```bash
# 1. Déployer le code avec la nouvelle commande
git add .
git commit -m "✨ Ajout commande pour téléphones Samsung Galaxy F16"
git push heroku main

# 2. Exécuter la commande sur Heroku
heroku run python manage.py add_samsung_f16_phones
```

### Alternative : Copier un fichier sur Heroku

Si vous devez absolument utiliser un fichier JSON :

```bash
# Créer un fichier temporaire sur Heroku
heroku run bash -c "cat > /tmp/phones.json" < local_phones.json

# Utiliser le fichier temporaire
heroku run python manage.py add_phones --file /tmp/phones.json
```

**⚠️ Note :** Cette méthode est plus complexe et moins fiable que le mode commande intégrée.

### Vérification après déploiement

```bash
# Vérifier que les produits ont été créés
heroku run python manage.py shell
```

```python
from product.models import Product, Phone
Product.objects.filter(brand='Samsung').count()
Phone.objects.filter(brand='Samsung').count()
```

## 📈 Bonnes pratiques pour Heroku

### 1. Utilisez le mode commande intégrée
- Plus fiable sur Heroku
- Pas de problème de fichiers
- Déploiement plus simple

### 2. Testez en local d'abord
- Vérifiez que la commande fonctionne localement
- Corrigez les erreurs avant le déploiement

### 3. Surveillez les logs
```bash
# Voir les logs en temps réel
heroku logs --tail

# Voir les logs d'une commande spécifique
heroku logs --tail | grep "add_samsung"
```

### 4. Utilisez des transactions
- Les commandes intégrées utilisent des transactions
- En cas d'erreur, tout est annulé
- Pas de données corrompues 