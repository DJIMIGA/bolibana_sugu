# 🔍 Diagnostic Problème Persistance Événements - SagaKore

## 📊 **Problème Identifié**

**Symptôme** : Les événements Meta Pixel apparaissent pendant les tests mais disparaissent après avoir quitté la page.

**Comportement observé** :
- ✅ **Pendant les tests** : Tous les événements sont détectés par Meta Pixel Helper
- ❌ **Après navigation** : Seuls PageView et TestEvent persistent

## 🎯 **Analyse de l'Implémentation Existante**

### **Événements Déjà Implémentés**

#### **1. ViewContent** ✅
**Fichier** : `saga/suppliers/templates/suppliers/product_detail.html` (lignes 94-104)
```html
{% if request.cookie_consent and request.cookie_consent.marketing %}
<script>
  if (typeof fbq !== 'undefined') {
    fbq('track', 'ViewContent', {
      value: {{ product.price|floatformat:2 }},
      currency: 'XOF',
      content_ids: [{{ product.id }}],
      content_type: 'product',
      content_name: '{{ product.title|escapejs }}',
      content_category: '{{ product.category.name|escapejs }}'
    });
  }
</script>
{% endif %}
```

#### **2. AddToCart** ✅
**Fichier** : `saga/suppliers/templates/suppliers/components/_add_to_cart_card_button.html` (lignes 105-120)
```html
{% if request.cookie_consent and request.cookie_consent.marketing %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    const addToCartForm = document.querySelector('#add-to-cart-{{ product.id }} form');
    if (addToCartForm) {
        addToCartForm.addEventListener('htmx:afterRequest', function(evt) {
            if (evt.detail.successful && typeof fbq !== 'undefined') {
                fbq('track', 'AddToCart', {
                    value: {{ product.price|floatformat:2 }},
                    currency: 'EUR',
                    content_ids: [{{ product.id }}],
                    content_type: 'product',
                    content_name: '{{ product.title|escapejs }}'
                });
            }
        });
    }
});
</script>
{% endif %}
```

#### **3. ViewCart** ✅
**Fichier** : `saga/cart/templates/cart/cart.html` (lignes 6-16)
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

#### **4. InitiateCheckout** ✅
**Fichiers** : `saga/cart/templates/checkout.html` et `saga/cart/templates/checkout_mixed.html`
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

#### **5. Purchase** ✅
**Fichier** : `saga/cart/templates/cart/order_confirmation.html` (lignes 6-18)
```html
{% if request.cookie_consent and request.cookie_consent.marketing %}
<script>
  if (typeof fbq !== 'undefined') {
    fbq('track', 'Purchase', {
      value: {{ order.total|floatformat:2 }},
      currency: 'XOF',
      content_ids: [{% for item in items %}{{ item.product.id }}{% if not forloop.last %},{% endif %}{% endfor %}],
      content_type: 'product',
      num_items: {{ items.count }},
      order_id: '{{ order.order_number }}'
    });
  }
</script>
{% endif %}
```

## 🔍 **Diagnostic du Problème**

### **Causes Possibles**

#### **1. Problème de Timing** ⚠️
- **Symptôme** : Les événements sont envoyés trop rapidement
- **Cause** : Pas de délai entre les événements
- **Solution** : Ajouter des délais entre les événements

#### **2. Données d'Événements Incorrectes** ⚠️
- **Symptôme** : Variables Django non définies
- **Cause** : `product`, `cart`, `order` non disponibles dans le contexte
- **Solution** : Vérifier les variables dans le contexte

#### **3. Configuration Events Manager** ⚠️
- **Symptôme** : Événements envoyés mais non reçus
- **Cause** : Événements non activés dans Facebook Events Manager
- **Solution** : Activer les événements dans Events Manager

#### **4. Filtres Meta Pixel Helper** ⚠️
- **Symptôme** : Événements visibles puis disparaissent
- **Cause** : Filtres appliqués dans l'extension
- **Solution** : Vérifier les filtres dans Meta Pixel Helper

#### **5. Problème de Consentement** ⚠️
- **Symptôme** : Événements ne se déclenchent pas
- **Cause** : `request.cookie_consent.marketing = False`
- **Solution** : Vérifier le consentement marketing

## 🧪 **Tests de Diagnostic**

### **Test 1: Vérification des Variables Django**
```javascript
// Dans la console du navigateur
console.log('Variables Django:');
console.log('  product:', typeof product !== 'undefined' ? '✅' : '❌');
console.log('  cart:', typeof cart !== 'undefined' ? '✅' : '❌');
console.log('  order:', typeof order !== 'undefined' ? '✅' : '❌');
console.log('  request.cookie_consent:', typeof request !== 'undefined' && request.cookie_consent ? '✅' : '❌');
```

### **Test 2: Vérification du Consentement**
```javascript
// Vérifier les cookies de consentement
const cookies = document.cookie.split(';').map(c => c.trim());
const marketingConsent = cookies.find(c => c.includes('marketing'));
console.log('Consentement marketing:', marketingConsent ? '✅' : '❌');
```

### **Test 3: Test des Événements Existants**
```javascript
// Utiliser le script de test
testExistingEvents();
```

### **Test 4: Vérification des Templates**
```javascript
// Vérifier les éléments détectés
checkExistingTemplates();
```

### **Test 5: Simulation des Actions**
```javascript
// Simuler les actions utilisateur
simulateUserActions();
```

## 🔧 **Solutions Proposées**

### **Solution 1: Améliorer la Détection Automatique**

Le script `real-ecommerce-events.js` ajoute une détection automatique qui complète l'implémentation existante :

```javascript
// Détection automatique des pages produit
function detectViewContent() {
    const isProductPage = document.querySelector('[data-product-id]') || 
                         document.querySelector('.product-detail') ||
                         window.location.pathname.includes('/product/');
    
    if (isProductPage) {
        setTimeout(() => {
            trackViewContent();
        }, 1000);
    }
}
```

### **Solution 2: Ajouter des Data Attributes**

Pour améliorer la détection, ajouter des data attributes :

```html
<!-- Sur les pages produit -->
<div data-product-id="{{ product.id }}" data-product-price="{{ product.price }}">
    <button data-add-to-cart data-product-id="{{ product.id }}">
        Ajouter au panier
    </button>
</div>

<!-- Sur les boutons panier -->
<button class="cart-button" data-cart>
    Panier
</button>

<!-- Sur les boutons checkout -->
<button class="checkout-button" data-checkout>
    Commander
</button>
```

### **Solution 3: Vérifier Events Manager**

1. **Aller sur Facebook Events Manager**
2. **Sélectionner le Pixel** `2046663719482491`
3. **Aller dans "Test Events"**
4. **Vérifier que tous les événements sont activés**
5. **Attendre 15-30 minutes** pour voir les événements

### **Solution 4: Améliorer les Données d'Événements**

```javascript
// Données plus robustes
function getProductData() {
    const productData = {
        content_type: 'product',
        content_ids: [],
        content_name: '',
        value: 0,
        currency: 'XOF',
        num_items: 1
    };
    
    // Récupérer depuis les meta tags
    const metaTags = document.querySelectorAll('meta[property*="product"]');
    metaTags.forEach(tag => {
        const property = tag.getAttribute('property');
        const content = tag.getAttribute('content');
        
        if (property.includes('price')) {
            productData.value = parseFloat(content) || 0;
        } else if (property.includes('name')) {
            productData.content_name = content;
        } else if (property.includes('id')) {
            productData.content_ids.push(content);
        }
    });
    
    return productData;
}
```

## 📋 **Plan d'Action**

### **Étape 1: Diagnostic Immédiat**
1. **Exécuter** `testExistingEvents()` dans la console
2. **Vérifier** Meta Pixel Helper pendant les tests
3. **Noter** quels événements apparaissent/disparaissent

### **Étape 2: Vérification Configuration**
1. **Vérifier** Facebook Events Manager
2. **Activer** tous les événements e-commerce
3. **Attendre** 15-30 minutes pour voir les résultats

### **Étape 3: Amélioration Implémentation**
1. **Ajouter** les data attributes manquants
2. **Tester** la détection automatique
3. **Vérifier** la persistance des événements

### **Étape 4: Validation Finale**
1. **Naviguer** sur le site normalement
2. **Vérifier** Meta Pixel Helper
3. **Confirmer** que les événements persistent

## 🎯 **Résultat Attendu**

Après l'implémentation des solutions :

1. **Navigation normale** : Les événements se déclenchent automatiquement
2. **Meta Pixel Helper** : Tous les événements sont détectés et persistent
3. **Facebook Events Manager** : Les événements sont reçus avec les bonnes données
4. **Données cohérentes** : Tous les événements utilisent le même format

---

## 📞 **Support**

### **Si les événements ne persistent toujours pas :**
1. **Vérifier** Events Manager > Test Events
2. **Attendre** 15-30 minutes pour voir les événements
3. **Vérifier** les filtres dans Meta Pixel Helper
4. **Tester** avec des données d'événements plus simples

### **Si les événements ne se déclenchent pas :**
1. **Vérifier** le consentement marketing
2. **Vérifier** les variables Django dans le contexte
3. **Tester** manuellement avec les commandes
4. **Vérifier** les erreurs JavaScript dans la console

**L'implémentation existante est correcte, le problème semble être lié à la configuration ou au timing des événements.** 🔧 