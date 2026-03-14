# 📊 Événements Google Analytics Complets - SagaKore

## 🎯 **Vue d'ensemble**

Ce document détaille tous les événements Google Analytics 4 (GA4) implémentés dans le projet SagaKore, organisés par catégorie et avec leurs paramètres spécifiques.

---

## 📈 **Événements Automatiques**

### **PageView** (Vue de page)
- **Déclencheur** : Automatique via `AnalyticsMiddleware`
- **Fréquence** : À chaque visite de page (sauf admin et fichiers statiques)
- **Paramètres** :
  - `page_url` : URL de la page
  - `user_agent` : Navigateur (anonymisé)
  - `referrer` : Page d'origine
  - `ip_anonymized` : IP anonymisée (si analytics seulement)

```python
# Dans core/middleware.py
track_page_view(request)
```

---

## 🛒 **Événements E-commerce**

### **AddToCart** (Ajout au panier)
- **Déclencheur** : Ajout d'un produit au panier
- **Localisation** : `cart/views.py` ligne 89-95
- **Paramètres** :
  - `product_id` : ID du produit
  - `product_name` : Nom du produit
  - `quantity` : Quantité ajoutée
  - `price` : Prix du produit

```python
track_add_to_cart(
    request=request,
    product_id=product.id,
    product_name=product.title,
    quantity=quantity,
    price=str(product.price)
)
```

### **ViewContent** (Vue de produit)
- **Déclencheur** : Visite d'une page produit
- **Localisation** : `suppliers/views.py` - `ProductDetailView`
- **Paramètres** :
  - `product_id` : ID du produit
  - `product_name` : Nom du produit
  - `category` : Catégorie du produit
  - `price` : Prix du produit

```python
track_view_content(
    request=self.request,
    product_id=product.id,
    product_name=product.title,
    category=product.category.name,
    price=str(product.price)
)
```

### **ViewCart** (Vue du panier)
- **Déclencheur** : Visite de la page panier
- **Localisation** : `cart/views.py` - `cart()`
- **Paramètres** :
  - `total_amount` : Montant total du panier
  - `currency` : Devise (XOF)
  - `items_count` : Nombre d'articles
  - `cart_id` : ID du panier

```python
track_view_cart(
    request=request,
    total_amount=str(cart.get_total_price()),
    currency='XOF',
    items_count=cart.cart_items.count(),
    cart_id=cart.id
)
```

### **InitiateCheckout** (Début de commande)
- **Déclencheur** : Accès à la page de commande
- **Localisation** : `cart/views.py` - `checkout()`
- **Paramètres** :
  - `total_amount` : Montant total
  - `currency` : Devise (XOF)
  - `items_count` : Nombre d'articles
  - `cart_id` : ID du panier

```python
track_initiate_checkout(
    request=request,
    total_amount=str(order_total),
    currency='XOF',
    items_count=total_items,
    cart_id=cart.id
)
```

### **Purchase** (Achat finalisé)
- **Déclencheur** : Finalisation d'une commande
- **Localisation** : `cart/views.py` - `order_confirmation()`
- **Paramètres** :
  - `order_id` : ID de la commande
  - `total_amount` : Montant total
  - `currency` : Devise (XOF)
  - `items_count` : Nombre d'articles

```python
track_purchase(
    request=request,
    order_id=order.id,
    total_amount=str(order.total_amount),
    currency='XOF',
    items_count=order.items.count()
)
```

---

## 🔍 **Événements de Recherche**

### **Search** (Recherche)
- **Déclencheur** : Effectuer une recherche
- **Localisation** : `suppliers/views.py` - `search()`
- **Paramètres** :
  - `search_term` : Terme recherché
  - `results_count` : Nombre de résultats

```python
track_search(
    request=request,
    search_term=query,
    results_count=products.count() if products else 0
)
```

---

## 👤 **Événements d'Authentification**

### **User_Registration** (Inscription)
- **Déclencheur** : Création d'un compte
- **Localisation** : `accounts/views.py` - `signup()`
- **Paramètres** :
  - `method` : Méthode d'inscription (email)
  - `source` : Source d'inscription (website)

```python
track_user_registration(request, method='email', source='website')
```

### **Login** (Connexion)
- **Déclencheur** : Connexion utilisateur
- **Localisation** : `accounts/views.py` - `LoginView.form_valid()`
- **Paramètres** :
  - `method` : Méthode de connexion (email)
  - `source` : Source de connexion (website)

```python
track_login(self.request, method='email', source='website')
```

### **Logout** (Déconnexion)
- **Déclencheur** : Déconnexion utilisateur
- **Localisation** : `accounts/views.py` - `logout_user()`
- **Paramètres** :
  - `session_duration` : Durée de la session (optionnel)

```python
track_logout(request)
```

---

## 🎯 **Événements d'Engagement (Côté Client)**

### **Scroll** (Défilement)
- **Déclencheur** : Défilement de page
- **Seuils** : 25%, 50%, 75%, 90%
- **Paramètres** :
  - `scroll_percentage` : Pourcentage atteint
  - `scroll_depth` : Profondeur de défilement

### **Engagement** (Temps passé)
- **Déclencheur** : 30 secondes sur la page
- **Paramètres** :
  - `time_spent_seconds` : Temps passé en secondes
  - `engagement_level` : Niveau d'engagement (low/medium/high)

### **Button_Click** (Clic sur bouton)
- **Déclencheur** : Clic sur un bouton
- **Paramètres** :
  - `button_text` : Texte du bouton
  - `button_class` : Classes CSS
  - `button_id` : ID du bouton
  - `button_type` : Type de bouton

### **Link_Click** (Clic sur lien)
- **Déclencheur** : Clic sur un lien
- **Paramètres** :
  - `link_text` : Texte du lien
  - `link_url` : URL du lien
  - `is_external` : Lien externe ou non
  - `link_type` : Type de lien

### **Form_Submit** (Soumission de formulaire)
- **Déclencheur** : Soumission d'un formulaire
- **Paramètres** :
  - `form_id` : ID du formulaire
  - `form_action` : Action du formulaire
  - `form_method` : Méthode du formulaire
  - `form_type` : Type de formulaire

### **Product_Image_Click** (Clic sur image produit)
- **Déclencheur** : Clic sur une image de produit
- **Paramètres** :
  - `product_id` : ID du produit
  - `image_src` : Source de l'image

### **Favorite_Toggle** (Ajout/Suppression favori)
- **Déclencheur** : Ajout/suppression d'un favori
- **Paramètres** :
  - `product_id` : ID du produit
  - `action` : Action (add/remove)

### **JavaScript_Error** (Erreur JavaScript)
- **Déclencheur** : Erreur JavaScript
- **Paramètres** :
  - `error_message` : Message d'erreur
  - `error_filename` : Fichier source
  - `error_lineno` : Numéro de ligne
  - `error_colno` : Numéro de colonne

### **Page_Performance** (Performance de page)
- **Déclencheur** : Chargement de page
- **Paramètres** :
  - `load_time` : Temps de chargement
  - `dom_content_loaded` : Temps DOM content loaded
  - `first_paint` : Premier rendu
  - `first_contentful_paint` : Premier contenu visible

---

## 🔧 **Configuration et Gestion**

### **Gestion du Consentement**
Tous les événements respectent le consentement cookies :
- **Analytics** : Événements envoyés si `request.cookie_consent.analytics = True`
- **Marketing** : Événements Facebook Pixel si `request.cookie_consent.marketing = True`

### **Stockage Différé**
Les événements côté serveur sont stockés en session et envoyés au prochain chargement de page :
```python
# Stockage en session
analytics_events = request.session.get('analytics_events', [])
event_data = {
    'event_type': event_type,
    'parameters': tracking_data,
    'timestamp': timezone.now().isoformat()
}
request.session['analytics_events'].append(event_data)
```

### **Anonymisation**
- IP anonymisée pour les utilisateurs analytics uniquement
- Données sensibles limitées
- User-Agent tronqué à 100 caractères

---

## 📊 **Vérification dans Google Analytics**

### **Temps réel**
1. Google Analytics → **Temps réel** → **Événements**
2. Vérifier que les événements apparaissent

### **Rapports**
1. Google Analytics → **Rapports** → **Engagement** → **Événements**
2. Analyser les événements par type et paramètres

### **DebugView** (Recommandé)
1. Google Analytics → **Admin** → **DebugView**
2. Tester les événements en temps réel

---

## 🚀 **Événements à Ajouter (Futur)**

### **E-commerce Avancé**
- `AddPaymentInfo` : Ajout d'informations de paiement
- `AddShippingInfo` : Ajout d'informations de livraison
- `BeginCheckout` : Début de processus de commande
- `ViewPromotion` : Vue d'une promotion

### **Engagement Avancé**
- `Video_Start` : Démarrage vidéo
- `Video_Complete` : Fin vidéo
- `File_Download` : Téléchargement de fichier
- `Print` : Impression de page

### **Personnalisation**
- `Custom_Event` : Événements personnalisés
- `User_Property` : Propriétés utilisateur
- `Conversion` : Conversions personnalisées

---

## 🛡️ **Conformité RGPD**

### **Obligations Respectées**
- ✅ **Consentement explicite** avant tracking
- ✅ **Anonymisation** des données sensibles
- ✅ **Possibilité de retrait** du consentement
- ✅ **Information claire** dans la politique de confidentialité

### **Implémentation Technique**
```python
# Vérification du consentement
if not has_analytics_consent(request):
    return False

# Anonymisation
if has_analytics_consent(request) and not has_marketing_consent(request):
    # Anonymiser l'IP
```

---

## 📚 **Fichiers Clés**

### **Backend**
- `saga/core/utils.py` : Fonctions de tracking
- `saga/core/templatetags/cookie_tags.py` : Scripts conditionnels
- `saga/core/middleware.py` : Middleware analytics

### **Frontend**
- `static/js/analytics-events.js` : Événements d'engagement
- `static/js/test-ga.js` : Script de test (développement)

### **Templates**
- `saga/templates/base.html` : Injection des scripts
- `saga/cart/templates/checkout.html` : Événements e-commerce
- `saga/suppliers/templates/suppliers/product_detail.html` : Événements produits

---

## 🎯 **Utilisation pour l'Analyse**

### **Funnel E-commerce**
1. **ViewContent** → Vue produit
2. **AddToCart** → Ajout au panier
3. **ViewCart** → Vue panier
4. **InitiateCheckout** → Début commande
5. **Purchase** → Achat finalisé

### **Engagement Utilisateur**
- **Scroll** : Qualité du contenu
- **Engagement** : Temps passé
- **Button_Click** : Interactions
- **Form_Submit** : Conversions

### **Performance**
- **Page_Performance** : Vitesse de chargement
- **JavaScript_Error** : Stabilité
- **User_Registration/Login** : Acquisition

---

**Cette implémentation complète permet un tracking détaillé et conforme RGPD de l'activité utilisateur sur SagaKore, facilitant l'analyse des performances et l'optimisation de l'expérience utilisateur.** 