# 🔍 Diagnostic Meta Pixel Helper - SagaKore

## 🚨 **Problème Identifié**
Meta Pixel Helper ne détecte plus même les événements PageView.

## 🔧 **Diagnostic et Solutions**

### **1. Vérification Immédiate**

#### **Étape 1: Ouvrir la Console**
1. Ouvrir votre site (localhost ou production)
2. Appuyer sur **F12** pour ouvrir les DevTools
3. Aller dans l'onglet **Console**

#### **Étape 2: Vérifier les Messages**
Vous devriez voir des messages comme :
```
🔍 === VÉRIFICATION RAPIDE FACEBOOK PIXEL ===
❌ PROBLÈME: fbq n'est pas défini
🔧 CAUSE: Le script Facebook Pixel n'est pas chargé
```

### **2. Solutions par Ordre de Priorité**

#### **Solution A: Consentement Marketing (Plus Probable)**
Si vous voyez `❌ Consentement marketing non donné` :

1. **Accepter les cookies marketing** dans la bannière de consentement
2. **OU** taper dans la console : `simulateMarketingConsent()`
3. **Recharger la page**

#### **Solution B: Test Forcé (Développement)**
Si le consentement ne fonctionne pas :

1. Taper dans la console : `runForceTest()`
2. Attendre 2-3 secondes
3. Vérifier Meta Pixel Helper

#### **Solution C: Vérification Manuelle**
Si rien ne fonctionne :

1. Taper dans la console : `checkCookieConsent()`
2. Taper dans la console : `diagnoseFacebookPixel()`
3. Suivre les instructions affichées

### **3. Commandes de Diagnostic Disponibles**

#### **Diagnostic Rapide**
```javascript
// Vérification immédiate
checkCookieConsent()
diagnoseFacebookPixel()
```

#### **Test Forcé**
```javascript
// Forcer le consentement et recharger le pixel
runForceTest()

// Tester tous les événements
testAllEventsForced()
```

#### **Test Manuel**
```javascript
// Forcer le consentement
forceMarketingConsent()

// Charger le pixel manuellement
loadFacebookPixel()
```

### **4. Vérification dans Meta Pixel Helper**

#### **Étape 1: Installer l'Extension**
1. Aller sur [Chrome Web Store - Meta Pixel Helper](https://chrome.google.com/webstore/detail/meta-pixel-helper/fdgfkebogiimcoedlicjlajpkdmockpc)
2. Installer l'extension
3. Recharger votre site

#### **Étape 2: Vérifier les Événements**
1. Cliquer sur l'icône Meta Pixel Helper
2. Vérifier que l'ID `2046663719482491` apparaît
3. Vérifier les événements dans l'onglet "Events"

### **5. Problèmes Courants et Solutions**

#### **Problème: fbq n'est pas défini**
**Cause** : Consentement marketing non donné
**Solution** : `simulateMarketingConsent()` puis recharger

#### **Problème: Aucun événement détecté**
**Cause** : Script Facebook non chargé
**Solution** : `runForceTest()`

#### **Problème: Erreurs JavaScript**
**Cause** : Conflit avec d'autres scripts
**Solution** : Vérifier la console pour les erreurs

### **6. Test de Validation**

#### **Test Complet**
1. Ouvrir la console
2. Taper : `runCompleteDiagnostic()`
3. Suivre les instructions affichées
4. Vérifier Meta Pixel Helper

#### **Test des Événements**
1. Taper : `testAllEvents()`
2. Vérifier que tous les événements apparaissent
3. Contrôler dans Meta Pixel Helper

### **7. Configuration de Production**

#### **Vérification Heroku**
1. Aller sur votre site Heroku
2. Ouvrir la console
3. Vérifier que les scripts de debug ne sont pas chargés
4. Tester avec `runForceTest()` si nécessaire

#### **Vérification Consentement**
1. Vérifier que la bannière de consentement s'affiche
2. Accepter les cookies marketing
3. Vérifier que le pixel se charge

### **8. Logs de Debug**

#### **Activation des Logs**
En mode développement, les logs sont automatiquement activés.

#### **Vérification des Logs**
1. Console du navigateur
2. Onglet Network (requêtes vers Facebook)
3. Meta Pixel Helper

### **9. Contact et Support**

#### **Si le problème persiste**
1. Capturer les messages de la console
2. Noter les erreurs JavaScript
3. Vérifier la configuration dans l'admin Django

#### **Informations Utiles**
- **ID Facebook Pixel** : `2046663719482491`
- **ID Google Analytics** : `G-CX5XPTXF1V`
- **Mode Debug** : Activé en développement

---

## 🎯 **Résumé des Actions**

1. **Ouvrir la console** (F12)
2. **Vérifier les messages** de diagnostic
3. **Tester le consentement** : `checkCookieConsent()`
4. **Forcer le test** si nécessaire : `runForceTest()`
5. **Vérifier Meta Pixel Helper** après 2-3 secondes

**Le problème vient probablement du consentement marketing non donné.** 