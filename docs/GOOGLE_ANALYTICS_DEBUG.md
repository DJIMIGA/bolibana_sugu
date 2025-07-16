# 🔍 Debug Google Analytics - SagaKore

## 📊 **Problème Identifié**

Google Analytics ne fonctionne pas malgré une configuration correcte.

## ✅ **Configuration Vérifiée**

- ✅ ID Google Analytics configuré : `G-CX5XPTXF1V`
- ✅ Consentement cookies fonctionnel
- ✅ Script généré correctement
- ✅ Middleware analytics actif

## 🔧 **Solutions Implémentées**

### 1. **Script Google Analytics Corrigé**

Le script a été mis à jour pour :
- Supporter Google Analytics 4 (GA4)
- Fonctionner en développement local
- Ajouter des logs de debug
- Gérer les événements différés

### 2. **Script de Test Ajouté**

Fichier `static/js/test-ga.js` pour :
- Vérifier que gtag est disponible
- Tester les événements manuellement
- Afficher des logs de debug

### 3. **Gestion des Événements Améliorée**

- Stockage des événements en session
- Envoi différé via JavaScript
- Logs détaillés pour le debugging

## 🧪 **Tests à Effectuer**

### **Étape 1 : Vérifier la Console Navigateur**

1. Ouvrez votre site : `http://127.0.0.1:8000`
2. Acceptez les cookies analytics
3. Ouvrez la console développeur (F12)
4. Vérifiez les messages :

```
🔍 Google Analytics chargé avec ID: G-CX5XPTXF1V
📊 Consentement analytics: true
✅ Google Analytics (gtag) disponible
📊 Test automatique Google Analytics
```

### **Étape 2 : Tester Manuellement**

Dans la console, tapez :
```javascript
// Test d'événement simple
gtag('event', 'test_event', {
    'event_category': 'test',
    'event_label': 'debug'
});

// Test avec notre fonction
window.testGAEvent('manual_test', {
    'custom_param': 'test_value'
});
```

### **Étape 3 : Vérifier Google Analytics**

1. Allez sur [Google Analytics](https://analytics.google.com)
2. Sélectionnez votre propriété
3. Allez dans **Temps réel** > **Événements**
4. Vous devriez voir les événements apparaître

### **Étape 4 : Vérifier le Réseau**

1. Dans la console, onglet **Network**
2. Filtrez par `google-analytics` ou `gtag`
3. Vérifiez que les requêtes sont envoyées

## 🚨 **Problèmes Courants**

### **1. Bloqueur de Publicités**

- Désactivez temporairement uBlock Origin
- Désactivez AdBlock Plus
- Vérifiez les extensions de navigateur

### **2. Mode Incognito**

- Testez en mode normal (pas incognito)
- Les bloqueurs sont plus stricts en incognito

### **3. Configuration GA4**

- Vérifiez que l'ID commence par `G-`
- Assurez-vous que la propriété GA4 est active
- Vérifiez les paramètres de collecte de données

### **4. Cookies Bloqués**

- Vérifiez les paramètres de cookies du navigateur
- Acceptez les cookies tiers
- Vérifiez les paramètres de confidentialité

## 🔍 **Debug Avancé**

### **Vérifier la Configuration**

```bash
python manage.py shell -c "from core.models import SiteConfiguration; config = SiteConfiguration.get_config(); print(f'GA ID: {config.google_analytics_id}')"
```

### **Tester le Script**

```bash
python manage.py shell -c "from core.templatetags.cookie_tags import render_analytics_scripts; from django.test import RequestFactory; from django.template import Context; from core.models import CookieConsent; factory = RequestFactory(); request = factory.get('/'); request.session = {}; consent = CookieConsent.objects.create(session_id='test', analytics=True); request.cookie_consent = consent; context = Context({'request': request}); script = render_analytics_scripts(context); print('Script:', script[:200] + '...' if len(script) > 200 else script); consent.delete()"
```

### **Vérifier les Logs**

Dans les logs Django, cherchez :
```
DEBUG: Consentement analytics donné, chargement du script...
📊 Analytics Event: page_view - {...}
```

## 📋 **Checklist de Vérification**

- [ ] ID Google Analytics configuré dans l'admin
- [ ] Consentement cookies accepté
- [ ] Console navigateur sans erreurs
- [ ] Script GA chargé (vérifier dans Elements)
- [ ] Requêtes réseau vers Google Analytics
- [ ] Événements visibles dans GA Temps réel
- [ ] Pas de bloqueur de publicités actif
- [ ] Mode développement désactivé en production

## 🆘 **Si Rien Ne Fonctionne**

1. **Vérifiez l'ID GA4** : Assurez-vous qu'il est correct
2. **Testez sur un autre navigateur** : Chrome, Firefox, Edge
3. **Vérifiez les paramètres GA4** : Collecte de données active
4. **Contactez le support** : Problème possible côté Google

## 📞 **Support**

Si le problème persiste, fournissez :
- Screenshot de la console navigateur
- Logs Django
- ID Google Analytics (masqué si nécessaire)
- Navigateur et version utilisés 

---

## **Étape 1 : Vérifier si le script Google Analytics est dans le HTML**

1. **Ouvre ton site dans le navigateur** (http://127.0.0.1:8000)
2. **Fais un clic droit** sur la page et choisis **« Afficher le code source de la page »**.
3. **Cherche** (Ctrl+F) la ligne suivante dans le code source :
   ```
   googletagmanager.com/gtag/js
   ```
   ou
   ```
   G-CX5XPTXF1V
   ```

**Dis-moi si tu trouves cette ligne dans le code source de la page.**
- Oui → On passe à l’étape suivante.
- Non → On corrige l’injection du script.

---

**Dis-moi ce que tu trouves, et je te guide pour la suite (une étape à la fois).** 