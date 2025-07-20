# 🔍 Diagnostic Persistance Meta Pixel - SagaKore

## 🚨 **Problème Identifié**
Les événements Meta Pixel fonctionnent pendant les tests mais ne persistent pas après avoir quitté la page.

## 📊 **Symptômes**
- ✅ **Pendant les tests** : Tous les événements sont détectés par Meta Pixel Helper
- ❌ **Après rechargement** : L'ID du pixel n'est pas détecté
- ⚠️ **Message** : "ID du pixel différent de celui configuré"

## 🔧 **Diagnostic Automatique**

### **Étape 1: Vérification au Chargement**
Le script `pixel-persistence-diagnostic.js` s'exécute automatiquement au chargement de la page.

**Résultat attendu** :
```
🔍 === DIAGNOSTIC PERSISTANCE META PIXEL ===
📱 === VÉRIFICATION AU CHARGEMENT DE LA PAGE ===
🔄 DOM chargé, vérification du pixel...
✅ fbq disponible au chargement
🎯 ID du pixel détecté: 2046663719482491
✅ ID du pixel correct
```

### **Étape 2: Vérification Manuelle**
Si le diagnostic automatique ne fonctionne pas, exécuter manuellement :

```javascript
checkCompleteState()
```

## 🎯 **Causes Possibles et Solutions**

### **Cause A: Problème de Consentement Marketing**

#### **Symptômes**
- fbq disponible mais ID non détecté
- Cookies de consentement manquants

#### **Solution**
```javascript
// Simuler le consentement marketing
simulateMarketingConsent()
```

### **Cause B: Script Facebook Non Chargé**

#### **Symptômes**
- fbq non disponible
- Aucun script Facebook détecté

#### **Solution**
```javascript
// Forcer le rechargement du pixel
forcePixelReload()
```

### **Cause C: Problème de Timing**

#### **Symptômes**
- fbq disponible mais ID non accessible
- Scripts chargés mais pixel non initialisé

#### **Solution**
```javascript
// Attendre et vérifier
setTimeout(() => {
    checkCompleteState();
}, 3000);
```

## 🧪 **Tests de Validation**

### **Test 1: Vérification Complète**
```javascript
checkCompleteState()
```

**Résultat attendu** :
```
🔍 === VÉRIFICATION ÉTAT COMPLET ===
✅ fbq disponible
🎯 ID du pixel: 2046663719482491
🍪 === VÉRIFICATION COOKIES DE CONSENTEMENT ===
✅ Consentement marketing détecté
📜 === VÉRIFICATION SCRIPTS FACEBOOK ===
✅ Scripts Facebook chargés
🧪 Test d'événement...
✅ Événement de test envoyé
```

### **Test 2: Simulation Consentement**
```javascript
simulateMarketingConsent()
```

### **Test 3: Rechargement Pixel**
```javascript
forcePixelReload()
```

## 📋 **Checklist de Diagnostic**

### **Étape 1: Vérification Initiale**
- [ ] Script de diagnostic chargé
- [ ] Diagnostic automatique exécuté
- [ ] fbq disponible
- [ ] ID du pixel détecté

### **Étape 2: Vérification Consentement**
- [ ] Cookies de consentement présents
- [ ] Consentement marketing activé
- [ ] Consentement analytics activé

### **Étape 3: Vérification Scripts**
- [ ] Scripts Facebook chargés
- [ ] Script fbevents.js présent
- [ ] Pas d'erreurs de chargement

### **Étape 4: Test de Persistance**
- [ ] PageView automatique envoyé
- [ ] Événements de test fonctionnels
- [ ] Meta Pixel Helper détecte les événements

## 🚀 **Commandes de Diagnostic Disponibles**

```javascript
// Diagnostic automatique (au chargement)
checkPixelOnLoad()

// Vérification complète
checkCompleteState()

// Simulation consentement marketing
simulateMarketingConsent()

// Forcer rechargement pixel
forcePixelReload()

// Vérification cookies
checkConsentCookies()

// Vérification scripts
checkFacebookScripts()
```

## 🔄 **Processus de Résolution**

### **Si l'ID n'est pas détecté :**
1. Exécuter `checkCompleteState()`
2. Si consentement manquant : `simulateMarketingConsent()`
3. Si scripts manquants : `forcePixelReload()`
4. Vérifier avec `checkCompleteState()`

### **Si fbq n'est pas disponible :**
1. Exécuter `forcePixelReload()`
2. Attendre 3 secondes
3. Vérifier avec `checkCompleteState()`

### **Si les événements ne persistent pas :**
1. Vérifier les cookies de consentement
2. Forcer le rechargement du pixel
3. Tester avec `testAllEcommerceEvents()`

## 📞 **Support**

### **Informations à Fournir**
1. Résultat de `checkCompleteState()`
2. Messages d'erreur de la console
3. État des cookies de consentement
4. Scripts Facebook chargés

### **Informations Utiles**
- **ID Pixel** : `2046663719482491`
- **URL** : https://bolibana-sugu-d56937020d1c.herokuapp.com/
- **Mode** : Production

---

## 🎯 **Résumé des Actions**

1. **Vérifier** l'état au chargement avec `checkCompleteState()`
2. **Simuler** le consentement si nécessaire avec `simulateMarketingConsent()`
3. **Recharger** le pixel si nécessaire avec `forcePixelReload()`
4. **Tester** la persistance avec `testAllEcommerceEvents()`

**Le problème de persistance devrait être résolu après ces étapes !** 