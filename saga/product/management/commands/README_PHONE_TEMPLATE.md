# 📱 Template d'Ajout de Téléphones

## 🎯 Objectif
Ce template évite les erreurs courantes lors de l'ajout de téléphones et sert de référence pour créer de nouvelles commandes.

## ⚠️ Erreurs Évitées
- **Erreur "Cannot resolve keyword 'title'"** : Le modèle `Phone` n'a pas de champ `title`
- **Structure incorrecte** : Création dans le mauvais ordre (Phone avant Product)
- **Champs manquants** : Oubli des champs requis

## 🔧 Structure Correcte
1. **Créer d'abord le `Product`** (contient le titre, prix, stock, etc.)
2. **Créer ensuite le `Phone`** (contient les spécifications techniques)
3. **Lier les deux** via `OneToOneField`

## 📝 Utilisation

### Méthode 1 : Template générique
```bash
python manage.py add_phone_template --brand "TECNO" --model "CAMON 40 Pro"
```

### Méthode 2 : Copier et adapter
1. Copiez `add_phone_template.py`
2. Renommez-le selon votre modèle
3. Modifiez les données dans `phones_data`
4. Ajustez les spécifications techniques

## 🏗️ Structure des Données
```python
phones_data = [
    {
        'title': 'TECNO CAMON 40 Pro 256GB 16GB Noir Galaxy',
        'rom': 256,                    # Stockage en GB
        'ram': 16,                     # RAM en GB
        'color_name': 'Noir Galaxy',   # Nom de la couleur
        'color_hex': '#000000',        # Code hexadécimal
        'price': 185000,               # Prix en FCFA
        'stock': 15,                   # Stock disponible
        'sku': 'TECNO-CAMON40PRO-256-16-BLACK'  # SKU unique
    }
]
```

## 🔧 Spécifications Techniques
Modifiez ces champs dans les `defaults` du Phone :
- `operating_system`: Système d'exploitation
- `processor`: Processeur
- `network`: Réseaux supportés
- `screen_size`: Taille d'écran en pouces
- `resolution`: Résolution d'écran
- `camera_front`: Caméra frontale
- `camera_main`: Caméra principale
- `battery_capacity`: Capacité batterie en mAh
- `accessories`: Accessoires inclus

## ✅ Bonnes Pratiques
1. **Titres en français** : "Noir Galaxy" au lieu de "Galaxy Black"
2. **SKU uniques** : Format cohérent et descriptif
3. **Prix réalistes** : Basés sur le marché local
4. **Stock varié** : Différent selon les couleurs populaires
5. **Spécifications complètes** : Tous les détails techniques

## 🚀 Exemple Complet
```bash
# Ajouter des Samsung Galaxy
python manage.py add_phone_template --brand "Samsung" --model "Galaxy S24"

# Ajouter des iPhone
python manage.py add_phone_template --brand "Apple" --model "iPhone 15"
```

## 📋 Checklist avant Déploiement
- [ ] Titres en français
- [ ] Couleurs avec codes hexadécimaux
- [ ] Prix cohérents
- [ ] SKU uniques
- [ ] Spécifications techniques complètes
- [ ] Test local avant déploiement Heroku 