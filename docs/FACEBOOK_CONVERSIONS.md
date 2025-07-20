# Facebook Conversions API - SagaKore

## 📋 **Vue d'ensemble**

Cette documentation explique l'intégration de l'API Facebook Conversions avec SagaKore pour le tracking des événements marketing.

## 🔧 **Configuration**

### **1. Modèle SiteConfiguration**

Les paramètres Facebook sont stockés dans le modèle `SiteConfiguration` :

```python
# saga/core/models.py
class SiteConfiguration(models.Model):
    # ... autres champs ...
    facebook_pixel_id = models.CharField(max_length=50, blank=True, null=True)
    facebook_access_token = models.CharField(max_length=500, blank=True, null=True)
```

### **2. Configuration dans l'Admin Django**

1. Aller dans **Admin Django** → **Core** → **Site Configuration**
2. Remplir :
   - **Facebook Pixel ID** : Votre ID de pixel Facebook
   - **Facebook Access Token** : Votre token d'accès Facebook

## 🎯 **Événements Intégrés**

### **1. Événements d'Utilisateur**

#### **CompleteRegistration** (Inscription)
- **Vue** : `saga/accounts/views.py` → `signup()`
- **Déclencheur** : Quand un utilisateur s'inscrit
- **Données** : Email, téléphone, nom du contenu

#### **Login** (Connexion)
- **Vue** : `saga/accounts/views.py` → `LoginView.form_valid()`
- **Déclencheur** : Quand un utilisateur se connecte
- **Données** : Email, téléphone, nom du contenu

### **2. Événements de Commerce**

#### **AddToCart** (Ajout au panier)
- **Vue** : `saga/cart/views.py` → `add_to_cart()`
- **Déclencheur** : Quand un produit est ajouté au panier
- **Données** : Email, téléphone, nom du produit, prix, devise

#### **InitiateCheckout** (Début de commande)
- **Vue** : `saga/cart/views.py` → `checkout()`
- **Déclencheur** : Quand l'utilisateur commence le processus de paiement
- **Données** : Email, téléphone, montant total, devise

#### **Purchase** (Achat)
- **Vue** : `saga/cart/views.py` → `payment_success()`
- **Déclencheur** : Quand un client paie vos services
- **Données** : Email, téléphone, montant, devise, nom du contenu

### **3. Événements de Lead**

#### **Lead** (Demande de comparaison)
- **Vue** : `saga/price_checker/views.py` → `PriceSubmissionCreateView.form_valid()`
- **Déclencheur** : Quand un utilisateur soumet une demande de comparaison de prix
- **Données** : Email, téléphone, nom du contenu

### **4. Événements de Navigation**

#### **PageView** (Visite de page)
- **Vue** : `saga/suppliers/views.py` → `ProductDetailView.get_context_data()`
- **Vue** : `saga/suppliers/views.py` → `CategoryListView.get_context_data()`
- **Vue** : `saga/suppliers/category_views.py` → `BaseCategoryView.get_context_data()`
- **Vue** : `saga/suppliers/category_views.py` → `CategoryListView.get_context_data()`
- **Déclencheur** : Quand un utilisateur visite une page produit ou catégorie
- **Données** : Email, téléphone (si connecté), nom du contenu, catégorie

#### **Search** (Recherche)
- **Vue** : `saga/suppliers/views.py` → `search()`
- **Déclencheur** : Quand un utilisateur effectue une recherche
- **Données** : Email, téléphone (si connecté), terme de recherche, catégorie

## 🔄 **Service Facebook Conversions**

### **Classe FacebookConversionsAPI**

```python
# saga/core/facebook_conversions.py
class FacebookConversionsAPI:
    def send_lead_event(self, user_data, content_name)
    def send_purchase_event(self, user_data, amount, currency, content_name)
    def send_complete_registration_event(self, user_data, content_name)
    def send_login_event(self, user_data, content_name)
    def send_add_to_cart_event(self, user_data, content_name, value, currency)
    def send_initiate_checkout_event(self, user_data, content_name, value, currency)
    def send_pageview_event(self, user_data=None, content_name=None, content_category=None)
    def send_view_content_event(self, user_data, content_name=None, content_category=None, value=None, currency="XOF")
    def send_search_event(self, user_data, search_string, content_category=None)
```

### **Utilisation**

```python
from core.facebook_conversions import facebook_conversions

# Exemple d'envoi d'événement
facebook_conversions.send_purchase_event(
    user_data={"email": user.email, "phone": user.phone},
    amount=5000,
    currency="XOF",
    content_name="Service Salam BoliBana"
)
```

## 🧪 **Tests**

### **Test Local**

```python
# Dans le shell Django
from core.facebook_conversions import facebook_conversions
from accounts.models import Shopper

user = Shopper.objects.first()

# Test Lead Event
facebook_conversions.send_lead_event(
    user_data={"email": user.email, "phone": getattr(user, 'phone', '')},
    content_name="Comparateur de Prix Salam"
)

# Test Purchase Event
facebook_conversions.send_purchase_event(
    user_data={"email": user.email, "phone": getattr(user, 'phone', '')},
    amount=5000,
    currency="XOF",
    content_name="Service Salam BoliBana"
)

# Test PageView Event
facebook_conversions.send_pageview_event(
    user_data={"email": user.email, "phone": getattr(user, 'phone', '')},
    content_name="Page Produit - iPhone 15",
    content_category="Téléphones"
)

# Test Search Event
facebook_conversions.send_search_event(
    user_data={"email": user.email, "phone": getattr(user, 'phone', '')},
    search_string="iPhone",
    content_category="Produits BoliBana"
)
```

### **Test Production (Heroku)**

```bash
heroku run python manage.py shell
```

Puis exécuter le même code de test.

## 📊 **Vérification des Événements**

1. **Facebook Events Manager** → Votre Pixel → Événements
2. **Attendre 5-10 minutes** pour voir les événements
3. **Vérifier les paramètres** : email, téléphone, montants

## 🔒 **Sécurité et Conformité**

### **Hachage des Données**

- **Email** : Haché avec SHA256
- **Téléphone** : Haché avec SHA256
- **Conformité** : Respect des normes de protection des données

### **Gestion des Erreurs**

- **Logs** : Toutes les erreurs sont loggées
- **Fallback** : Les erreurs n'interrompent pas le flux utilisateur
- **Validation** : Vérification des données avant envoi

## 🚀 **Déploiement**

### **1. Migration de Base de Données**

```bash
python manage.py makemigrations
python manage.py migrate
```

### **2. Configuration Production**

1. **Heroku** : Configurer les variables d'environnement
2. **Admin** : Remplir Facebook Pixel ID et Access Token
3. **Test** : Vérifier les événements dans Facebook Events Manager

## 📈 **Optimisation**

### **Audiences Personnalisées**

Créer des audiences basées sur :
- **Utilisateurs inscrits** (CompleteRegistration)
- **Utilisateurs actifs** (Login)
- **Acheteurs** (Purchase)
- **Leads qualifiés** (Lead)

### **Campagnes Ciblées**

- **Retargeting** : Utilisateurs qui ont ajouté au panier
- **Lookalike** : Audiences similaires aux acheteurs
- **Conversion** : Optimisation pour les achats

## 🔧 **Maintenance**

### **Monitoring**

- **Vérifier les logs** : Erreurs d'API
- **Facebook Events Manager** : Qualité des données
- **Performance** : Temps de réponse des événements

### **Mises à Jour**

- **API Facebook** : Surveiller les changements
- **Dépendances** : Mettre à jour les packages
- **Tests** : Vérifier régulièrement les événements

## 📞 **Support**

En cas de problème :
1. **Vérifier les logs** Django
2. **Tester** avec le shell Django
3. **Consulter** Facebook Events Manager
4. **Contacter** l'équipe technique 