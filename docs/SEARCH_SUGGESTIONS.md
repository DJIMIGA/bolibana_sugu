# Système de Suggestions de Recherche

## Vue d'ensemble

Le système de suggestions de recherche remplace l'affichage direct des produits par des suggestions intelligentes de mots-clés et catégories. Cela améliore l'expérience utilisateur en guidant la recherche vers des termes plus précis.

## Fonctionnalités

### 🔍 **Suggestions Intelligentes**
- **Produits** : Suggestions basées sur les titres de produits
- **Catégories** : Suggestions basées sur les catégories
- **Mots-clés populaires** : Suggestions de termes fréquemment recherchés

### 🎯 **URLs de Redirection**
Format : `/search/results/?text={terme_principal}&keywords={terme_principal}`

Exemples :
- `/search/results/?text=iPhone%2012&keywords=iPhone%2012`
- `/search/results/?text=Électronique&keywords=Électronique`

**Comportement intelligent :**
- Le clic sur une suggestion utilise le texte de la suggestion (pas le texte du champ)
- Le champ de recherche se remplit automatiquement avec le texte de la suggestion
- Recherche combinée si text et keywords sont différents

### ⌨️ **Navigation Clavier**
- **Flèches haut/bas** : Naviguer dans les suggestions
- **Entrée** : Sélectionner la suggestion active
- **Échap** : Fermer les suggestions

### 📱 **Responsive Design**
- Optimisé pour desktop, tablette et mobile
- Animations fluides et transitions
- Interface tactile adaptée

## Architecture

### Backend (Django)

#### Vues
- `search_suggestions()` : Génère les suggestions
- `search_results_page()` : Page de résultats dédiée

#### URLs
```python
path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
path('search/results/', views.search_results_page, name='search_results_page'),
```

### Frontend (JavaScript)

#### Scripts
- `search-suggestions.js` : Gestion des interactions
- `search-utils.js` : Utilitaires communs
- `search-error-handler.js` : Gestion des erreurs

#### Templates
- `search_suggestions.html` : Template des suggestions
- `search_results_page.html` : Page de résultats

## Utilisation

### 1. **Recherche Basique**
```
Utilisateur tape → Suggestions apparaissent → Clic sur suggestion → Redirection
```

### 2. **Navigation Clavier**
```
Focus sur champ → Flèches pour naviguer → Entrée pour sélectionner
```

### 3. **URLs Directes**
```
/search/results/?text=iPhone&keywords=smartphone
```

## Configuration

### Styles CSS
```css
.search-suggestions-container {
    max-height: 400px;
    overflow-y: auto;
}

.suggestion-item {
    transition: all 0.2s ease;
}
```

### Paramètres HTMX
```html
hx-get="{% url 'suppliers:search_suggestions' %}"
hx-trigger="keyup changed delay:300ms"
hx-target="#results-desktop"
```

## Types de Suggestions

### 🏷️ **Produit**
- **Icône** : Boîte bleue
- **Source** : Titres de produits
- **URL** : `/search/results/?text={titre_produit}&keywords={recherche}`

### 📂 **Catégorie**
- **Icône** : Dossier vert
- **Source** : Noms de catégories
- **URL** : `/search/results/?text={nom_categorie}&keywords={recherche}`

### 🔍 **Mot-clé**
- **Icône** : Loupe jaune
- **Source** : Mots-clés populaires
- **URL** : `/search/results/?text={mot_cle}&keywords={recherche}`

## Améliorations Futures

### 🚀 **Fonctionnalités Prévues**
- [ ] Historique des recherches
- [ ] Suggestions personnalisées
- [ ] Recherche vocale
- [ ] Autocomplétion avancée
- [ ] Filtres de catégorie

### 🔧 **Optimisations**
- [ ] Cache des suggestions
- [ ] Indexation des mots-clés
- [ ] Analyse des tendances
- [ ] A/B testing des suggestions

## Tests

### 🧪 **Script de Test**
Le fichier `search-test.js` fournit des outils de débogage :

```javascript
// Appuyer sur F12 pour tester la navigation clavier
// Appuyer sur F11 pour tester les suggestions
// Vérifier la console pour les logs
// Tester le remplissage automatique du champ
```

### ✅ **Points de Test**
- [ ] Affichage des suggestions
- [ ] Navigation clavier
- [ ] Redirection des URLs
- [ ] Responsive design
- [ ] Gestion des erreurs
- [ ] Remplissage automatique du champ
- [ ] Prévisualisation au survol
- [ ] Tri par pertinence des suggestions
- [ ] Affichage des cartes de produits
- [ ] Prévention du débordement
- [ ] Grille responsive

## Support

### 🐛 **Dépannage**
1. Vérifier la console pour les erreurs
2. Tester avec le script de test (F12)
3. Vérifier les URLs de redirection
4. Contrôler les requêtes HTMX

### 📞 **Contact**
Pour toute question ou problème, consulter la documentation ou contacter l'équipe de développement. 