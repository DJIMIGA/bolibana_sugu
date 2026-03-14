# Identité de Couleur - SagaKore

## Palette de Couleurs Principales

### Couleurs Primaires
- **Vert (PRIMARY)**: `#10B981`
  - Utilisation : Actions principales, succès, éléments actifs
  - Opacités recommandées : 5-8% (fonds), 30-40% (bordures), 50-60% (accents)

- **Jaune (SECONDARY)**: `#F59E0B`
  - Utilisation : Avertissements, éléments secondaires, highlights
  - Opacités recommandées : 5-8% (fonds), 30-40% (bordures), 50-60% (accents)

- **Rouge (DANGER)**: `#EF4444`
  - Utilisation : Erreurs, suppressions, alertes importantes
  - Opacités recommandées : 5-8% (fonds), 30-40% (bordures), 50-60% (accents)

### Accent Chaud
- **Beige/Terre cuite (BEIGE/TERRACOTTA)**: `#C08A5B`
  - Utilisation : Éléments "souvenirs", photos, badges, catégories spéciales
  - Opacités recommandées : 6-8% (fonds), 30-40% (bordures), 50-60% (accents)
  - **Note** : Utilisé dans les catégories pour varier la palette

## Utilisation des Opacités

### Fonds (Background)
- **Très subtil** : 5-6% (`${COLOR}05`, `${COLOR}06`)
- **Subtil** : 8-10% (`${COLOR}08`, `${COLOR}10`)
- **Moyen** : 12-15% (`${COLOR}12`, `${COLOR}15`)

### Bordures (Borders)
- **Très subtil** : 30% (`${COLOR}30`)
- **Subtil** : 40% (`${COLOR}40`)
- **Visible** : 50-60% (`${COLOR}50`, `${COLOR}60`)

### Accents
- **Discret** : 50% (`${COLOR}50`)
- **Visible** : 60% (`${COLOR}60`)
- **Plein** : 100% (couleur directe)

## Ombres et Élévations

### Ombres Subtiles
```javascript
shadowColor: '#000',
shadowOffset: { width: 0, height: 1 },
shadowOpacity: 0.03-0.04,
shadowRadius: 2,
elevation: 1-2,
```

### Ombres Moyennes
```javascript
shadowColor: '#000',
shadowOffset: { width: 0, height: 1 },
shadowOpacity: 0.05-0.06,
shadowRadius: 3,
elevation: 2-3,
```

## Exemples d'Utilisation

### Cartes de Catégories
```javascript
backgroundColor: `${categoryColor}06`,  // Fond très subtil
borderTopColor: `${categoryColor}50`,   // Bordure visible
borderTopWidth: 2,                       // Bordure fine
```

### Headers
```javascript
borderBottomColor: `${COLORS.PRIMARY}40`,  // Bordure subtile
borderBottomWidth: 1.5,                     // Bordure fine
backgroundColor: '#FAFAFA',                // Fond légèrement grisé
```

### Badges et Indicateurs
```javascript
backgroundColor: `${color}08`,             // Fond subtil
borderColor: `${color}30`,                 // Bordure très subtile
```

## Règles de Design

1. **Subtilité** : Toujours privilégier des opacités faibles pour les fonds
2. **Bordures fines** : Utiliser 1.5-2px maximum pour les bordures
3. **Ombres discrètes** : Opacité entre 0.03 et 0.06 pour les ombres
4. **Cohérence** : Utiliser les mêmes opacités pour des éléments similaires
5. **Hiérarchie** : Utiliser des opacités plus fortes pour les éléments importants

## Mapping des Couleurs de Catégories

Les catégories peuvent avoir différentes couleurs dans la base de données. Le mapping se fait ainsi :

- `green` → Vert (#10B981)
- `yellow` → Jaune (#F59E0B)
- `red` → Rouge (#EF4444)
- `beige`, `terracotta`, `brown`, `tan` → Beige/Terre cuite (#C08A5B)
- Autres couleurs → Distribution cyclique entre les 4 couleurs principales

## Fichiers de Configuration

Les couleurs sont définies dans :
- `mobile/src/utils/constants.ts` : Constantes COLORS
- `mobile/src/screens/CategoryScreen.tsx` : Fonction getCategoryColor
- `mobile/src/screens/SubCategoryScreen.tsx` : Fonction getCategoryColor

## Mise à Jour

Pour ajouter de nouvelles couleurs :
1. Ajouter la couleur dans `mobile/src/utils/constants.ts`
2. Mettre à jour les fonctions `getCategoryColor` dans les écrans
3. Documenter ici avec les opacités recommandées
