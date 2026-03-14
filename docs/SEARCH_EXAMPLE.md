# Exemple d'Utilisation du Système de Suggestions

## Scénario : Recherche d'iPhone

### 1. **L'utilisateur tape "iph" dans le champ de recherche**

```
Champ de recherche: "iph"
```

### 2. **Les suggestions apparaissent automatiquement**

```
🏷️ iPhone 12 Pro Max
🏷️ iPhone 13
🏷️ iPhone 14
📂 Électronique
🔍 iPhone
🔍 Smartphone
```

### 3. **L'utilisateur clique sur "iPhone 12 Pro Max"**

**Avant le clic :**
- Champ de recherche : "iph"
- URL actuelle : `/`

**Après le clic :**
- Champ de recherche : "iPhone 12 Pro Max" (rempli automatiquement)
- URL de redirection : `/search/results/?text=iPhone%2012%20Pro%20Max&keywords=iPhone%2012%20Pro%20Max`
- Page affichée : Page de résultats avec tous les iPhone 12 Pro Max

### 4. **Page de résultats affichée**

```
Résultats de recherche
Recherche pour "iPhone 12 Pro Max" (contexte: iPhone 12 Pro Max)

Statistiques :
- 15 produits trouvés
- Terme principal: iPhone 12 Pro Max
- Contexte: iPhone 12 Pro Max

[Grille de produits iPhone 12 Pro Max]
```

## Scénario : Navigation Clavier

### 1. **L'utilisateur tape "sam" et utilise les flèches**

```
Champ de recherche: "sam"
Suggestions:
🔍 Samsung (focused) ← Flèche bas sélectionne cette suggestion
🏷️ Samsung Galaxy S23
📂 Électronique
```

### 2. **L'utilisateur appuie sur Entrée**

- La suggestion "Samsung" est sélectionnée
- Le champ se remplit avec "Samsung"
- Redirection vers `/search/results/?text=Samsung&keywords=Samsung`

## Scénario : Recherche Combinée

### 1. **URL directe avec paramètres différents**

```
/search/results/?text=iPhone&keywords=smartphone
```

### 2. **Recherche intelligente**

Le système recherche les produits qui contiennent :
- "iPhone" OU "smartphone" dans le titre
- "iPhone" OU "smartphone" dans la description  
- "iPhone" OU "smartphone" dans la catégorie

### 3. **Résultats affichés**

```
Résultats de recherche
Recherche pour "iPhone" (contexte: smartphone)

[Produits contenant "iPhone" ou "smartphone"]
```

## Avantages du Système

### ✅ **Pour l'utilisateur**
- Suggestions intelligentes basées sur les données réelles
- Remplissage automatique du champ de recherche
- Navigation clavier intuitive
- URLs propres et partageables

### ✅ **Pour le développeur**
- Code modulaire et extensible
- Gestion d'erreurs robuste
- Tests automatisés
- Documentation complète

### ✅ **Pour le SEO**
- URLs structurées et descriptives
- Paramètres de recherche clairs
- Possibilité d'indexation des pages de résultats

## Tests Pratiques

### 🧪 **Test 1 : Recherche basique**
1. Aller sur la page d'accueil
2. Taper "iph" dans le champ de recherche
3. Vérifier que les suggestions apparaissent
4. Cliquer sur une suggestion
5. Vérifier que la page de résultats s'affiche correctement

### 🧪 **Test 2 : Navigation clavier**
1. Taper "sam" dans le champ de recherche
2. Utiliser les flèches haut/bas pour naviguer
3. Appuyer sur Entrée pour sélectionner
4. Vérifier la redirection

### 🧪 **Test 3 : URL directe**
1. Aller directement sur `/search/results/?text=iPhone&keywords=iPhone`
2. Vérifier que la page s'affiche correctement
3. Vérifier que les statistiques sont correctes

### 🧪 **Test 4 : Recherche combinée**
1. Aller sur `/search/results/?text=iPhone&keywords=smartphone`
2. Vérifier que les résultats incluent les deux termes
3. Vérifier l'affichage des paramètres 