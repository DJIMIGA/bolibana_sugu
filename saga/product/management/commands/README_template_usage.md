# 📱 Guide d'Utilisation du Template d'Ajout de Téléphones

## 🎯 Objectif

Ce template permet d'ajouter facilement de nouveaux téléphones à la base de données avec une **normalisation automatique des marques** pour éviter les doublons.

## ✅ Fonctionnalités

### 🔧 Normalisation Automatique des Marques
- **TECNO** : `tecno`, `Tecno`, `TECNO` → `TECNO`
- **Samsung** : `samsung`, `SAMSUNG`, `Samsung` → `Samsung`
- **Apple** : `apple`, `APPLE`, `Apple` → `Apple`
- **Xiaomi** : `xiaomi`, `XIAOMI`, `Xiaomi` → `Xiaomi`
- **Et bien d'autres...**

### 🛡️ Prévention des Doublons
- Évite les doublons de marques avec différentes casses
- Normalisation automatique lors de la création ET mise à jour
- Cohérence dans toute la base de données

## 🚀 Utilisation

### 1. Test de Normalisation
```bash
# Test simple de normalisation
python manage.py add_phone_template --brand "tecno" --test-normalization

# Résultat : "tecno" → "TECNO"
```

### 2. Ajout de Téléphones
```bash
# Ajouter des téléphones avec normalisation automatique
python manage.py add_phone_template --brand "TECNO" --model "CAMON 40 Pro"

# Ou avec une marque non normalisée (sera automatiquement normalisée)
python manage.py add_phone_template --brand "tecno" --model "CAMON 40 Pro"
```

### 3. Personnalisation du Template
1. **Copier le template** : `add_phone_template.py`
2. **Renommer** selon votre modèle : `add_samsung_galaxy_s24.py`
3. **Modifier** la section `phones_data` avec vos données
4. **Ajuster** les spécifications techniques

## 📝 Structure du Template

### Données des Téléphones
```python
phones_data = [
    {
        'title': f'{normalized_brand} {model} 256GB 16GB Noir Galaxy',
        'rom': 256,
        'ram': 16,
        'color_name': 'Noir Galaxy',
        'color_hex': '#000000',
        'price': 185000,
        'stock': 15,
        'sku': f'{normalized_brand.upper()}-{model.replace(" ", "")}-256-16-BLACK'
    },
    # ... autres variantes
]
```

### Spécifications Techniques
```python
defaults={
    'brand': normalized_brand,  # ✅ Normalisation automatique
    'model': model,
    'operating_system': 'Android 15',
    'processor': 'MediaTek Helio G100 Ultimate Processor',
    'network': '2G, 3G, 4G, 5G',
    'screen_size': 6.78,
    'resolution': '1080 x 2436',
    'camera_front': '50 MP AF',
    'camera_main': '50 MP 1/1.56" OIS + 8 MP Wide-angle',
    'battery_capacity': 5200,
    'storage': phone_data['rom'],
    'ram': phone_data['ram'],
    'color': color,
    'is_new': True,
    'box_included': True,
    'accessories': 'Chargeur 45W, Câble Type-C, Coque, Écouteurs'
}
```

## 🔄 Processus Automatique

1. **Normalisation** : La marque est automatiquement normalisée
2. **Couleurs** : Création automatique des couleurs si elles n'existent pas
3. **Produits** : Création ou mise à jour des produits
4. **Téléphones** : Création ou mise à jour des téléphones
5. **Cohérence** : Toutes les marques sont normalisées partout

## 📊 Exemples de Normalisation

| Marque Originale | Marque Normalisée |
|------------------|-------------------|
| `tecno`          | `TECNO`           |
| `Tecno`          | `TECNO`           |
| `TECNO`          | `TECNO`           |
| `samsung`        | `Samsung`         |
| `SAMSUNG`        | `Samsung`         |
| `xiaomi`         | `Xiaomi`          |
| `apple`          | `Apple`           |
| `huawei`         | `Huawei`          |

## 🛠️ Personnalisation Avancée

### Ajouter de Nouvelles Marques
Modifiez `saga/product/utils.py` :
```python
brand_mappings = {
    # ... marques existantes
    'nouvelle_marque': 'Nouvelle Marque',
    'NOUVELLE_MARQUE': 'Nouvelle Marque',
    'Nouvelle Marque': 'Nouvelle Marque',
}
```

### Modifier les Spécifications
Ajustez les valeurs par défaut dans la section `defaults` du template selon vos besoins.

## ✅ Avantages

- **Pas de doublons** : Normalisation automatique
- **Facilité d'utilisation** : Template prêt à l'emploi
- **Flexibilité** : Personnalisable pour chaque modèle
- **Cohérence** : Même logique partout
- **Maintenance** : Centralisé dans `utils.py`

## 🎉 Résultat

Plus jamais de problèmes de doublons de marques ! Tous les téléphones auront des marques normalisées et cohérentes dans la base de données. 