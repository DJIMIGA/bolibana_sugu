# Fichiers Statiques - Application Product

## 📁 Structure des Fichiers

```
saga/product/static/product/
├── css/
│   └── filter-dropdowns.css      # Styles pour les menus déroulants avec scroll
├── js/
│   ├── script.js                 # Script principal de l'application product
│   └── filter-dropdowns.js       # Gestionnaire des menus déroulants avec scroll
└── README.md                     # Ce fichier
```

## 🎯 Fichiers de Filtres

### `filter-dropdowns.css`
Styles standardisés pour les menus déroulants avec scroll dans les filtres de produits.

**Classes principales :**
- `.filter-dropdown-container` : Conteneur principal avec scroll
- `.mobile-filter-section` : Sections mobiles avec scroll
- `.select-with-scroll` : Selects avec scroll personnalisé
- `.filter-option` : Options de filtres avec hover et sélection

**Caractéristiques :**
- Scrollbars personnalisées (3-4px de largeur)
- Couleurs cohérentes avec la charte graphique (vert/jaune)
- Support Firefox avec `scrollbar-width` et `scrollbar-color`
- Responsive design avec breakpoints

### `filter-dropdowns.js`
Gestionnaire JavaScript pour améliorer l'expérience utilisateur des filtres.

**Fonctionnalités :**
- Navigation au clavier (flèches, Entrée, Échap)
- Indicateurs visuels de dépassement
- Touch scrolling optimisé pour mobile
- Optimisations de performance (Intersection Observer, debouncing)

**API disponible :**
```javascript
// Ouvrir/fermer des sections
FilterDropdownManager.openSection('sectionId');
FilterDropdownManager.closeSection('sectionId');

// Recherche dans les filtres
FilterDropdownManager.searchInFilters('terme', '#container');
```

## 🔧 Utilisation

### Inclusion dans les templates :
```html
{% load static %}

<!-- CSS -->
<link rel="stylesheet" href="{% static 'product/css/filter-dropdowns.css' %}">

<!-- JavaScript -->
<script src="{% static 'product/js/filter-dropdowns.js' %}"></script>
```

### Classes CSS à utiliser :
```html
<!-- Conteneur avec scroll -->
<div class="filter-dropdown-container">
    <div class="filter-option">Option 1</div>
    <div class="filter-option selected">Option 2</div>
</div>

<!-- Section mobile -->
<div class="mobile-filter-section">
    <input type="radio" name="filter" value="1">
    <label>Option 1</label>
</div>

<!-- Select avec scroll -->
<select class="select-with-scroll">
    <option>Option 1</option>
    <option>Option 2</option>
</select>
```

## 🎨 Cohérence Visuelle

### Couleurs utilisées :
- **Scrollbar track** : `#f9fafb` (gris très clair)
- **Scrollbar thumb** : `#d1d5db` (gris moyen)
- **Scrollbar hover** : `#9ca3af` (gris foncé)
- **Sélection active** : `#ecfdf5` avec `#059669` (vert)

### Dimensions :
- **Desktop** : `max-height: 200px`
- **Mobile** : `max-height: 12rem` (192px)
- **Responsive** : `max-height: 10rem` (160px) sur petits écrans

## 📱 Responsive Design

Les styles s'adaptent automatiquement selon la taille d'écran :
- **Desktop** : Hauteurs maximales pour une meilleure lisibilité
- **Tablet** : Adaptation progressive des dimensions
- **Mobile** : Hauteurs réduites pour économiser l'espace d'écran

## 🔄 Maintenance

### Bonnes pratiques :
1. **Toujours utiliser** les classes CSS standardisées
2. **Tester** sur différents appareils et navigateurs
3. **Maintenir** la cohérence avec la charte graphique
4. **Documenter** les nouvelles fonctionnalités

### Mises à jour :
- Vérifier la compatibilité avec les nouvelles versions de navigateurs
- Tester les performances avec des listes plus grandes
- Valider l'accessibilité selon les normes WCAG

## 🧪 Tests

### Tests d'accessibilité :
- ✅ Navigation au clavier complète
- ✅ Support des lecteurs d'écran
- ✅ Contraste des couleurs conforme WCAG
- ✅ Focus visible et logique

### Tests de compatibilité :
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile (iOS/Android)

---

**Dernière mise à jour** : Décembre 2024  
**Version** : 1.0.0  
**Application** : Product 