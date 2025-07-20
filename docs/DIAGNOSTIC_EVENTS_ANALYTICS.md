# 🔍 Diagnostic des Événements Analytics - SagaKore

## 📊 **Problème Identifié**

D'après votre rapport Facebook Pixel, seuls les événements suivants apparaissent :
- **PageView** : 111 événements ✅
- **TestEvent** : 5 événements (tests manuels) ⚠️
- **AddToCart** : 1 événement ⚠️
- **Purchase** : 1 événement ⚠️
- **ViewContent** : 1 événement ⚠️

## 🎯 **Événements Manquants**

### **Événements E-commerce**
- ❌ **ViewCart** : Vue du panier
- ❌ **InitiateCheckout** : Début de commande

### **Événements d'Authentification**
- ❌ **CompleteRegistration** : Inscription
- ❌ **Login** : Connexion
- ❌ **Logout** : Déconnexion

### **Événements de Recherche**
- ❌ **Search** : Recherche de produits

## 🔧 **Diagnostic et Solutions**

### **1. Vérification de l'Implémentation**

#### **✅ Événements Correctement Implémentés**

**Côté Serveur (Django) :**
```python
# saga/cart/views.py - Ligne 89-95
track_add_to_cart(
    request=request,
    product_id=product.id,
    product_name=product.title,
    quantity=quantity,
    price=str(product.price)
)

# saga/cart/views.py - Ligne 125-135
track_view_cart(
    request=request,
    total_amount=str(cart.get_total_price()),
    currency='XOF',
    items_count=cart.cart_items.count(),
    cart_id=cart.id
)

# saga/cart/views.py - Ligne 152-200
track_initiate_checkout(
    request=request,
    total_amount=str(total_amount),
    currency='XOF',
    items_count=total_items,
    cart_id=cart.id
)

# saga/cart/views.py - Ligne 1186-1200
track_purchase(
    request=request,
    order_id=str(order.id),
    total_amount=str(order.total),
    currency='XOF',
    items_count=order.items.count()
)
```

**Côté Client (Templates) :**
```html
<!-- saga/suppliers/templates/suppliers/product_detail.html -->
{% if request.cookie_consent and request.cookie_consent.marketing %}
<script>
  fbq('track', 'ViewContent', {
    value: {{ product.price|floatformat:2 }},
    currency: 'XOF',
    content_ids: [{{ product.id }}],
    content_type: 'product',
    content_name: '{{ product.title|escapejs }}',
    content_category: '{{ product.category.name|escapejs }}'
  });
</script>
{% endif %}

<!-- saga/cart/templates/cart/order_confirmation.html -->
{% if request.cookie_consent and request.cookie_consent.marketing %}
<script>
  fbq('track', 'Purchase', {
    value: {{ order.total|floatformat:2 }},
    currency: 'XOF',
    content_ids: [{% for item in items %}{{ item.product.id }}{% if not forloop.last %},{% endif %}{% endfor %}],
    content_type: 'product',
    num_items: {{ items.count }},
    order_id: '{{ order.order_number }}'
  });
</script>
{% endif %}
```

### **2. Problèmes Potentiels**

#### **A. Consentement Cookies**
- **Problème** : Les événements ne s'envoient que si `request.cookie_consent.marketing = True`
- **Vérification** : Ouvrir les DevTools → Console → Taper `console.log('Consentement marketing:', typeof fbq !== 'undefined')`

#### **B. Erreurs JavaScript**
- **Problème** : Erreurs JavaScript empêchent l'exécution des scripts
- **Vérification** : DevTools → Console → Chercher les erreurs en rouge

#### **C. Timing des Scripts**
- **Problème** : Les scripts s'exécutent avant que fbq soit disponible
- **Solution** : Vérifier que `typeof fbq !== 'undefined'` avant d'envoyer

#### **D. Données Manquantes**
- **Problème** : Variables Django non définies dans le contexte
- **Vérification** : Vérifier que `order`, `items`, `product` existent

### **3. Tests de Diagnostic**

#### **Test 1 : Vérification des Scripts**
```javascript
// Dans la console du navigateur
console.log('Google Analytics:', typeof gtag !== 'undefined');
console.log('Facebook Pixel:', typeof fbq !== 'undefined');
console.log('Page URL:', window.location.href);
```

#### **Test 2 : Test Manuel des Événements**
```javascript
// Test Facebook Pixel
if (typeof fbq !== 'undefined') {
    fbq('track', 'ViewContent', {
        content_name: 'Test Product',
        content_category: 'Test',
        value: 1000,
        currency: 'XOF'
    });
    console.log('✅ Événement ViewContent envoyé');
}

// Test Google Analytics
if (typeof gtag !== 'undefined') {
    gtag('event', 'view_content', {
        product_id: 'test-123',
        product_name: 'Test Product',
        category: 'Test',
        price: 1000,
        currency: 'XOF'
    });
    console.log('✅ Événement ViewContent envoyé');
}
```

#### **Test 3 : Script de Test Complet**
```javascript
// Utiliser le script de test créé
testAllEvents();
```

### **4. Solutions par Événement**

#### **ViewCart (Vue Panier)**
**Problème** : Événement côté serveur uniquement
**Solution** : Ajouter côté client dans `cart.html`
```html
{% if request.cookie_consent and request.cookie_consent.marketing %}
<script>
  if (typeof fbq !== 'undefined') {
    fbq('track', 'ViewCart', {
      value: {{ cart.get_total_price|floatformat:2 }},
      currency: 'XOF',
      content_type: 'product',
      content_ids: [{% for item in cart.cart_items.all %}{{ item.product.id }}{% if not forloop.last %},{% endif %}{% endfor %}]
    });
  }
</script>
{% endif %}
```

#### **InitiateCheckout (Début Commande)**
**Problème** : Événement côté serveur uniquement
**Solution** : Ajouter côté client dans `checkout.html`
```html
{% if request.cookie_consent and request.cookie_consent.marketing %}
<script>
  if (typeof fbq !== 'undefined') {
    fbq('track', 'InitiateCheckout', {
      value: {{ cart.get_total_price|floatformat:2 }},
      currency: 'XOF',
      num_items: {{ cart.cart_items.count }},
      content_ids: [{% for item in cart.cart_items.all %}{{ item.product.id }}{% if not forloop.last %},{% endif %}{% endfor %}],
      content_type: 'product'
    });
  }
</script>
{% endif %}
```

#### **CompleteRegistration (Inscription)**
**Problème** : Non implémenté côté client
**Solution** : Ajouter dans le template de confirmation d'inscription
```html
{% if request.cookie_consent and request.cookie_consent.marketing %}
<script>
  if (typeof fbq !== 'undefined') {
    fbq('track', 'CompleteRegistration', {
      value: 0,
      currency: 'XOF'
    });
  }
</script>
{% endif %}
```

#### **Search (Recherche)**
**Problème** : Événement côté serveur uniquement
**Solution** : Ajouter côté client dans les résultats de recherche
```html
{% if request.cookie_consent and request.cookie_consent.marketing %}
<script>
  if (typeof fbq !== 'undefined') {
    fbq('track', 'Search', {
      search_string: '{{ query|escapejs }}',
      content_category: '{{ category.name|escapejs }}'
    });
  }
</script>
{% endif %}
```

### **5. Vérification en Temps Réel**

#### **Facebook Pixel Helper**
1. Installer l'extension "Facebook Pixel Helper" sur Chrome
2. Ouvrir les DevTools (F12)
3. Aller dans l'onglet "Facebook Pixel Helper"
4. Naviguer sur le site et vérifier les événements

#### **Google Analytics DebugView**
1. Google Analytics → Admin → DebugView
2. Activer le mode debug
3. Naviguer sur le site
4. Vérifier les événements en temps réel

#### **Console du Navigateur**
```javascript
// Vérifier les événements envoyés
console.log('Événements Facebook:', window.fbq);
console.log('Événements Google:', window.gtag);
```

### **6. Actions Immédiates**

#### **Étape 1 : Diagnostic**
1. Ouvrir le site en mode développement
2. Exécuter `testAllEvents()` dans la console
3. Vérifier les erreurs dans la console
4. Contrôler le consentement cookies

#### **Étape 2 : Correction**
1. Ajouter les événements manquants côté client
2. Vérifier les conditions de consentement
3. Tester chaque événement individuellement

#### **Étape 3 : Validation**
1. Utiliser Facebook Pixel Helper
2. Vérifier dans Google Analytics DebugView
3. Confirmer l'apparition des événements

### **7. Monitoring Continu**

#### **Scripts de Monitoring**
```javascript
// Ajouter dans analytics-events.js
function monitorEvents() {
    // Monitorer les événements envoyés
    const originalFbq = window.fbq;
    window.fbq = function(...args) {
        console.log('🎯 Facebook Pixel Event:', args);
        return originalFbq.apply(this, args);
    };
    
    const originalGtag = window.gtag;
    window.gtag = function(...args) {
        console.log('📊 Google Analytics Event:', args);
        return originalGtag.apply(this, args);
    };
}

// Activer le monitoring en développement
if (window.location.hostname === 'localhost') {
    monitorEvents();
}
```

## 🎯 **Conclusion**

Les événements sont correctement implémentés côté serveur, mais certains manquent côté client. Le problème principal semble être :

1. **Événements côté serveur uniquement** : ViewCart, InitiateCheckout
2. **Événements non implémentés** : CompleteRegistration, Search côté client
3. **Conditions de consentement** : Vérifier que les cookies marketing sont acceptés

**Action recommandée** : Ajouter les événements manquants côté client et tester avec le script `testAllEvents()`. 