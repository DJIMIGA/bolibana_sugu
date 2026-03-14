# 🔍 Dépannage Meta Pixel Helper - SagaKore

## 🚨 **Problème Identifié**
Meta Pixel Helper détecte le pixel mais certains événements (AddToCart, ViewCart, etc.) n'apparaissent pas.

## 📊 **Diagnostic Actuel**
- ✅ **PageView** : Détecté
- ✅ **TestEvent** : Détecté
- ❌ **AddToCart** : Non détecté
- ❌ **ViewCart** : Non détecté
- ❌ **InitiateCheckout** : Non détecté
- ❌ **Purchase** : Non détecté

## 🔧 **Solutions par Ordre de Priorité**

### **1. Test Immédiat des Événements**

#### **Étape 1: Ouvrir la Console**
1. Aller sur votre site
2. Appuyer sur **F12** pour ouvrir les DevTools
3. Aller dans l'onglet **Console**

#### **Étape 2: Tester Tous les Événements**
Taper dans la console :
```javascript
testAllEcommerceEvents()
```

**Résultat attendu** :
```
🚀 Test de tous les événements e-commerce...
🎯 Envoi événement: PageView {}
✅ Événement PageView envoyé
🎯 Envoi événement: ViewContent {...}
✅ Événement ViewContent envoyé
...
```

#### **Étape 3: Vérifier Meta Pixel Helper**
1. Ouvrir Meta Pixel Helper
2. Vérifier que tous les événements apparaissent
3. Noter les événements manquants

### **2. Test d'Événements Spécifiques**

Si certains événements ne fonctionnent pas, tester individuellement :

```javascript
// Test AddToCart
testSpecificEvent("AddToCart")

// Test ViewCart
testSpecificEvent("ViewCart")

// Test InitiateCheckout
testSpecificEvent("InitiateCheckout")

// Test Purchase
testSpecificEvent("Purchase")
```

### **3. Vérification de la Configuration**

```javascript
// Vérifier la configuration du pixel
checkPixelConfig()
```

## 🎯 **Causes Possibles et Solutions**

### **Cause A: Événements Non Configurés dans Events Manager**

#### **Solution**
1. Aller sur [Facebook Events Manager](https://business.facebook.com/events_manager2)
2. Sélectionner votre pixel `2046663719482491`
3. Aller dans **Événements** > **Configurer les événements**
4. Vérifier que les événements sont activés :
   - AddToCart
   - ViewCart
   - InitiateCheckout
   - Purchase
   - ViewContent
   - Search
   - CompleteRegistration

### **Cause B: Filtres dans Meta Pixel Helper**

#### **Solution**
1. Dans Meta Pixel Helper, vérifier les filtres
2. S'assurer qu'aucun filtre n'exclut les événements
3. Vérifier l'onglet "Events" et non "Warnings"

### **Cause C: Paramètres d'Événements Incorrects**

#### **Solution**
Les événements doivent avoir les bons paramètres :

```javascript
// AddToCart correct
{
    content_type: 'product',
    content_ids: ['product-id'],
    content_name: 'Product Name',
    value: 15000,
    currency: 'XOF',
    num_items: 1
}

// ViewCart correct
{
    content_type: 'product',
    content_ids: ['product-id'],
    value: 15000,
    currency: 'XOF',
    num_items: 1
}
```

### **Cause D: Problème de Timing**

#### **Solution**
1. Attendre 2-3 secondes entre chaque événement
2. Vérifier que le pixel est complètement chargé
3. Utiliser `setTimeout` pour les tests

## 🧪 **Tests de Validation**

### **Test 1: Événement Simple**
```javascript
testEvent("AddToCart", {
    content_type: 'product',
    content_ids: ['test-123'],
    value: 15000,
    currency: 'XOF'
})
```

### **Test 2: Événement Complet**
```javascript
testEvent("Purchase", {
    content_type: 'product',
    content_ids: ['test-123'],
    value: 15000,
    currency: 'XOF',
    num_items: 1,
    order_id: 'test-order-123'
})
```

### **Test 3: Vérification en Temps Réel**
1. Ouvrir Meta Pixel Helper
2. Exécuter `testAllEcommerceEvents()`
3. Vérifier que chaque événement apparaît instantanément

## 📋 **Checklist de Diagnostic**

### **Étape 1: Vérification de Base**
- [ ] Pixel détecté dans Meta Pixel Helper
- [ ] ID correct : `2046663719482491`
- [ ] PageView fonctionne
- [ ] TestEvent fonctionne

### **Étape 2: Test des Événements**
- [ ] Exécuter `testAllEcommerceEvents()`
- [ ] Vérifier chaque événement dans Meta Pixel Helper
- [ ] Noter les événements manquants

### **Étape 3: Configuration Events Manager**
- [ ] Événements activés dans Events Manager
- [ ] Paramètres d'événements corrects
- [ ] Aucun filtre restrictif

### **Étape 4: Validation**
- [ ] Tous les événements apparaissent dans Meta Pixel Helper
- [ ] Aucun warning dans Meta Pixel Helper
- [ ] Événements reçus dans Events Manager (délai 15-30 min)

## 🚀 **Commandes de Test Disponibles**

```javascript
// Test complet
testAllEcommerceEvents()

// Test spécifique
testSpecificEvent("AddToCart")

// Vérification configuration
checkPixelConfig()

// Test personnalisé
testEvent("EventName", { param1: "value1" })
```

## 📞 **Support**

### **Si le problème persiste**
1. Capturer les messages de la console
2. Faire une capture d'écran de Meta Pixel Helper
3. Vérifier la configuration dans Events Manager
4. Contacter le support avec les informations

### **Informations Utiles**
- **ID Pixel** : `2046663719482491`
- **URL de test** : https://bolibana-sugu-d56937020d1c.herokuapp.com/
- **Mode** : Production

---

## 🎯 **Résumé des Actions**

1. **Exécuter** `testAllEcommerceEvents()`
2. **Vérifier** Meta Pixel Helper
3. **Configurer** Events Manager si nécessaire
4. **Valider** tous les événements

**Le problème devrait être résolu après ces étapes !** 