# 🏗️ Architecture Django - Guide Simplifié

## 📊 Diagramme Complet du Flux Django

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         🌐 REQUÊTE HTTP (ENTRÉE)                                     │
│                                                                                     │
│  Le client (navigateur, app mobile, etc.) envoie une requête HTTP                  │
│                                                                                     │
│  Exemples de requêtes :                                                             │
│  • GET  /accounts/login/          → Afficher le formulaire de connexion            │
│  • POST /accounts/signup/         → Créer un nouveau compte                         │
│  • GET  /api/profile/             → Récupérer le profil utilisateur (API)          │
│  • POST /api/token/refresh/       → Rafraîchir le token JWT                        │
│                                                                                     │
│  La requête contient :                                                              │
│  - URL (chemin de la ressource)                                                    │
│  - Méthode HTTP (GET, POST, PUT, DELETE)                                           │
│  - Headers (authentification, type de contenu)                                      │
│  - Body (données pour POST/PUT)                                                     │
└──────────────────────────────────────┬──────────────────────────────────────────────┘
                                        │
                                        │ Django reçoit la requête via WSGI/ASGI
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    🔀 URL PATTERNS (ROUTAGE)                                        │
│                    Fichier : saga/urls.py                                           │
│                                                                                     │
│  Django analyse l'URL et la compare avec les patterns définis                      │
│                                                                                     │
│  Exemples de patterns dans votre projet :                                          │
│  • path('accounts/', include('accounts.urls'))                                     │
│    → Si URL commence par /accounts/, charge accounts/urls.py                       │
│                                                                                     │
│  • path('api/token/refresh/', TokenRefreshView.as_view())                          │
│    → URL exacte /api/token/refresh/ → appelle TokenRefreshView                     │
│                                                                                     │
│  • path('cart/', include('cart.urls'))                                             │
│    → Si URL commence par /cart/, charge cart/urls.py                               │
│                                                                                     │
│  Processus :                                                                        │
│  1. Django parcourt urlpatterns de haut en bas                                     │
│  2. Compare l'URL avec chaque pattern                                              │
│  3. Si correspondance trouvée → extrait les paramètres et appelle la vue           │
│  4. Si aucune correspondance → erreur 404                                          │
│                                                                                     │
│  Résultat : Django identifie quelle vue doit traiter la requête                    │
└──────────────────────────────────────┬──────────────────────────────────────────────┘
                                       │
                                       │ Route vers la vue appropriée
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                      🎯 VIEWS (CONTRÔLEUR)                                          │
│                      Fichier : accounts/views.py                                    │
│                                                                                     │
│  La vue est le cœur de la logique métier. Elle traite la requête et               │
│  détermine la réponse à renvoyer.                                                  │
│                                                                                     │
│  Types de vues dans votre projet :                                                 │
│                                                                                     │
│  1. VUES BASÉES SUR LES FONCTIONS (Function-Based Views)                           │
│     def signup(request):                                                            │
│         - Reçoit request (objet HttpRequest)                                      │
│         - Traite les données du formulaire                                         │
│         - Appelle les modèles si nécessaire                                        │
│         - Retourne HttpResponse (HTML, JSON, redirect)                             │
│                                                                                     │
│  2. VUES BASÉES SUR LES CLASSES (Class-Based Views)                                │
│     class LoginView(AuthLoginView):                                                │
│         - Plus structurées et réutilisables                                        │
│         - Méthodes : get(), post(), form_valid(), etc.                             │
│         - Héritage possible pour personnaliser                                     │
│                                                                                     │
│  3. VUES API (Django REST Framework)                                               │
│     class ProfileView(APIView):                                                    │
│         - Retournent du JSON au lieu de HTML                                       │
│         - Utilisent des sérialiseurs pour transformer les données                 │
│         - Gèrent l'authentification via tokens JWT                                 │
│                                                                                     │
│  Actions possibles dans une vue :                                                  │
│  • Valider les données du formulaire                                               │
│  • Vérifier les permissions (login_required, permission_required)                 │
│  • Interroger la base de données via les modèles                                   │
│  • Utiliser des sérialiseurs pour les API                                          │
│  • Rendre un template HTML                                                         │
│  • Retourner une réponse JSON                                                       │
│  • Rediriger vers une autre page                                                    │
└──────────────┬───────────────────────────────────────┬────────────────────────────┘
               │                                       │
               │                                       │
               │ (Pour les API REST)                  │ (Pour accéder aux données)
               │                                       │
               ▼                                       ▼
┌──────────────────────────────────────────┐  ┌──────────────────────────────────────────┐
│      🔄 SERIALIZER (API REST)            │  │      📦 MODELS (ORM Django)              │
│      Fichier : accounts/api/serializers  │  │      Fichier : accounts/models.py        │
│                                          │  │                                          │
│  Utilisé uniquement pour les API REST   │  │  Les modèles définissent la structure    │
│  (Django REST Framework)                 │  │  de vos données et l'interface avec      │
│                                          │  │  la base de données.                     │
│  Rôles principaux :                      │  │                                          │
│                                          │  │  Exemples dans votre projet :            │
│  1. SÉRIALISATION (Modèle → JSON)       │  │                                          │
│     user = User.objects.get(id=1)        │  │  • User (utilisateur Django)             │
│     serializer = UserSerializer(user)    │  │  • Shopper (profil acheteur)             │
│     json_data = serializer.data          │  │  • ShippingAddress (adresses)             │
│     → {"id": 1, "email": "..."}         │  │  • Product (produits)                     │
│                                          │  │  • Cart, CartItem (panier)               │
│  2. DÉSÉRIALISATION (JSON → Modèle)     │  │                                          │
│     data = {"email": "new@example.com"} │  │  Structure d'un modèle :                 │
│     serializer = UserSerializer(data)    │  │                                          │
│     if serializer.is_valid():           │  │  class Shopper(models.Model):            │
│         user = serializer.save()        │  │      user = OneToOneField(User)           │
│                                          │  │      phone = CharField(max_length=20)     │
│  3. VALIDATION                          │  │      created_at = DateTimeField()          │
│     - Vérifie que les données sont      │  │                                          │
│       correctes avant sauvegarde         │  │  Opérations via ORM :                    │
│     - Retourne des erreurs si invalide  │  │                                          │
│                                          │  │  • Lire : Shopper.objects.get(id=1)      │
│  Avantages :                             │  │  • Filtrer : User.objects.filter(...)    │
│  • Séparation claire des responsabilités│  │  • Créer : Shopper.objects.create(...)    │
│  • Validation automatique                │  │  • Modifier : shopper.save()             │
│  • Transformation facile des données     │  │  • Supprimer : shopper.delete()           │
│                                          │  │                                          │
│  Note : Les sérialiseurs peuvent aussi   │  │  Django ORM convertit automatiquement    │
│  interagir avec les modèles pour lire    │  │  ces opérations en requêtes SQL :        │
│  ou écrire des données.                  │  │                                          │
│                                          │  │  Shopper.objects.get(id=1)               │
│                                          │  │  → SELECT * FROM accounts_shopper        │
│                                          │  │     WHERE id = 1                          │
└──────────────────┬───────────────────────┘  └──────────────────┬───────────────────────┘
                   │                                              │
                   │ Les sérialiseurs utilisent aussi les modèles │
                   │                                              │
                   └──────────────────┬───────────────────────────┘
                                      │
                                      │ Requêtes SQL générées par Django ORM
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    💾 DATABASE (BASE DE DONNÉES)                                     │
│                    Type : PostgreSQL (dans votre projet)                           │
│                                                                                     │
│  La base de données stocke toutes les données de manière persistante.              │
│  Django ORM (Object-Relational Mapping) convertit les opérations Python            │
│  en requêtes SQL automatiquement.                                                  │
│                                                                                     │
│  Tables principales dans votre projet :                                             │
│                                                                                     │
│  • auth_user                    → Utilisateurs Django                              │
│  • accounts_shopper             → Profils des acheteurs                            │
│  • accounts_shippingaddress     → Adresses de livraison                            │
│  • product_product              → Produits du catalogue                            │
│  • cart_cart                    → Paniers d'achat                                   │
│  • cart_cartitem                → Articles dans les paniers                         │
│                                                                                     │
│  Opérations SQL générées :                                                         │
│                                                                                     │
│  LECTURE (SELECT) :                                                                │
│  User.objects.filter(email='test@example.com')                                     │
│  → SELECT * FROM auth_user WHERE email = 'test@example.com'                        │
│                                                                                     │
│  CRÉATION (INSERT) :                                                               │
│  Shopper.objects.create(user=user, phone='123456789')                               │
│  → INSERT INTO accounts_shopper (user_id, phone) VALUES (1, '123456789')           │
│                                                                                     │
│  MODIFICATION (UPDATE) :                                                           │
│  shopper.phone = '987654321'                                                       │
│  shopper.save()                                                                    │
│  → UPDATE accounts_shopper SET phone = '987654321' WHERE id = 1                    │
│                                                                                     │
│  SUPPRESSION (DELETE) :                                                            │
│  shopper.delete()                                                                  │
│  → DELETE FROM accounts_shopper WHERE id = 1                                       │
│                                                                                     │
│  Les données sont retournées sous forme d'objets Python (instances de modèles)    │
└──────────────────────────────────────┬──────────────────────────────────────────────┘
                                       │
                                       │ Données retournées (objets Python)
                                       │
                                       │ (Retour vers les modèles, puis la vue)
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    📤 RÉPONSE HTTP (SORTIE)                                         │
│                                                                                     │
│  La vue génère une réponse HTTP qui est renvoyée au client.                        │
│                                                                                     │
│  Types de réponses possibles :                                                     │
│                                                                                     │
│  1. RÉPONSE HTML (Pour les pages web)                                              │
│     return render(request, 'accounts/login.html', {'form': form})                  │
│     → Génère du HTML à partir d'un template                                        │
│     → Status code : 200 OK                                                          │
│                                                                                     │
│  2. RÉPONSE JSON (Pour les API)                                                    │
│     return Response({'status': 'success', 'data': serializer.data})              │
│     → Retourne des données au format JSON                                          │
│     → Status code : 200 OK                                                          │
│                                                                                     │
│  3. REDIRECTION                                                                    │
│     return redirect('accounts:profile')                                            │
│     → Redirige vers une autre URL                                                  │
│     → Status code : 302 Found ou 301 Moved Permanently                            │
│                                                                                     │
│  4. RÉPONSE D'ERREUR                                                               │
│     return HttpResponseNotFound('Page non trouvée')                                │
│     → Status code : 404 Not Found                                                  │
│                                                                                     │
│     return HttpResponseForbidden('Accès refusé')                                   │
│     → Status code : 403 Forbidden                                                  │
│                                                                                     │
│  5. RÉPONSE DE CRÉATION (API)                                                      │
│     return Response(serializer.data, status=201)                                   │
│     → Status code : 201 Created                                                    │
│                                                                                     │
│  La réponse contient :                                                             │
│  - Status code HTTP (200, 404, 500, etc.)                                          │
│  - Headers (Content-Type, Set-Cookie, etc.)                                         │
│  - Body (HTML, JSON, texte, etc.)                                                   │
│                                                                                     │
│  Le client reçoit la réponse et l'affiche (navigateur) ou la traite (app mobile)  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 🔄 Résumé du Flux Complet

1. **REQUÊTE** → Le client envoie une requête HTTP (GET, POST, etc.)
2. **URL PATTERNS** → Django analyse l'URL et trouve la vue correspondante
3. **VIEWS** → La vue traite la requête et exécute la logique métier
4. **SERIALIZER** (si API) → Transforme les données en JSON ou valide les données entrantes
5. **MODELS** → Interface avec la base de données via Django ORM
6. **DATABASE** → Stockage et récupération des données (SQL)
7. **RÉPONSE** → La vue génère une réponse HTTP (HTML, JSON, redirect) qui est renvoyée au client

### ⚡ Points Importants

- **Tout commence par une requête HTTP** et se termine par une réponse HTTP
- **Les URL Patterns** sont le point d'entrée qui route vers la bonne vue
- **Les Views** contiennent toute la logique métier de votre application
- **Les Serializers** sont utilisés uniquement pour les API REST
- **Les Models** permettent d'interagir avec la base sans écrire de SQL
- **La Database** stocke toutes les données de manière persistante
- **Chaque composant a un rôle précis** dans le cycle de vie d'une requête

---

## 🔄 Exemple Concret : Connexion Utilisateur

### Étape 1 : La Requête
```
Client (navigateur) → GET /accounts/login/
```

### Étape 2 : URL Patterns
```python
# saga/urls.py
path('accounts/', include('accounts.urls'))

# accounts/urls.py
path('login/', views.LoginView.as_view(), name="login")
```
✅ **Résultat** : Django trouve que `/accounts/login/` correspond à `LoginView`

### Étape 3 : La Vue
```python
# accounts/views.py
class LoginView(AuthLoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    
    def form_valid(self, form):
        user = form.get_user()
        # Vérifie si 2FA est activée
        if user.has_2fa_enabled():
            # Redirige vers vérification 2FA
        else:
            # Connecte l'utilisateur
```
✅ **Résultat** : La vue traite la requête

### Étape 4 : Les Modèles (si nécessaire)
```python
# accounts/models.py
class Shopper(models.Model):
    user = models.OneToOneField(User)
    # ... autres champs
```
✅ **Résultat** : Si besoin, la vue interroge la base via les modèles

### Étape 5 : La Base de Données
```
SELECT * FROM accounts_shopper WHERE user_id = ?
```
✅ **Résultat** : Les données sont récupérées

### Étape 6 : La Réponse
```python
# La vue retourne
return render(request, 'accounts/login.html', {'form': form})
```
✅ **Résultat** : HTML envoyé au navigateur

---

## 🔄 Exemple Concret : API Token Refresh

### Étape 1 : La Requête
```
Client (app mobile) → POST /api/token/refresh/
```

### Étape 2 : URL Patterns
```python
# saga/urls.py
path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
```
✅ **Résultat** : Django route vers `TokenRefreshView`

### Étape 3 : La Vue
```python
# rest_framework_simplejwt.views
class TokenRefreshView(APIView):
    def post(self, request):
        # Rafraîchit le token JWT
```
✅ **Résultat** : La vue traite le token

### Étape 4 : Le Sérialiseur (pour API)
```python
# Le sérialiseur valide et transforme les données
serializer = TokenRefreshSerializer(data=request.data)
```
✅ **Résultat** : Les données sont validées et transformées

### Étape 5 : La Réponse
```json
{
    "access": "nouveau_token_jwt_ici"
}
```
✅ **Résultat** : JSON envoyé au client

---

## 📚 Les Composants en Détail

### 1️⃣ URL PATTERNS (`urls.py`)
**Rôle** : Routeur - détermine quelle vue appeler selon l'URL

**Dans votre projet** :
- `saga/urls.py` : URLs principales
- `accounts/urls.py` : URLs de l'app accounts
- `product/api/urls.py` : URLs API des produits

**Exemple** :
```python
path('accounts/login/', views.LoginView.as_view())
# Si URL = /accounts/login/ → appelle LoginView
```

---

### 2️⃣ VIEWS (`views.py`)
**Rôle** : Contrôleur - traite la requête et génère la réponse

**Types de vues** :
- **Vues basées sur les fonctions** : `def signup(request):`
- **Vues basées sur les classes** : `class LoginView(AuthLoginView):`
- **Vues API** : `class ProfileView(APIView):`

**Dans votre projet** :
- `accounts/views.py` : Vues web (HTML)
- `accounts/api/views.py` : Vues API (JSON)

---

### 3️⃣ SERIALIZER (DRF - Django REST Framework)
**Rôle** : Transforme les données entre formats

**Utilisations** :
- **Sérialisation** : Modèle Django → JSON
- **Désérialisation** : JSON → Modèle Django
- **Validation** : Vérifie que les données sont correctes

**Exemple** :
```python
# Modèle → JSON
user = User.objects.get(id=1)
serializer = UserSerializer(user)
json_data = serializer.data  # {"id": 1, "email": "..."}

# JSON → Modèle
data = {"email": "new@example.com"}
serializer = UserSerializer(data=data)
if serializer.is_valid():
    user = serializer.save()  # Crée/modifie le modèle
```

---

### 4️⃣ MODELS (`models.py`)
**Rôle** : Structure des données et interface avec la base

**Dans votre projet** :
- `accounts/models.py` : User, Shopper, ShippingAddress
- `product/models.py` : Product, Category
- `cart/models.py` : Cart, CartItem

**Exemple** :
```python
class Shopper(models.Model):
    user = models.OneToOneField(User)
    phone = models.CharField(max_length=20)
    
# Utilisation
shopper = Shopper.objects.get(user=request.user)
```

---

### 5️⃣ DATABASE
**Rôle** : Stockage persistant des données

**Dans votre projet** : PostgreSQL (probablement)

**Opérations** :
- `SELECT` : Lire des données
- `INSERT` : Créer des données
- `UPDATE` : Modifier des données
- `DELETE` : Supprimer des données

**Via Django ORM** :
```python
# Au lieu de SQL brut
User.objects.filter(email='test@example.com')

# Django génère automatiquement :
# SELECT * FROM auth_user WHERE email = 'test@example.com'
```

---

## 🎯 Flux Complet : Création d'un Compte

```
1. REQUÊTE
   POST /accounts/signup/
   {email: "user@example.com", password: "..."}

2. URL PATTERNS
   path('accounts/', include('accounts.urls'))
   → path('signup/', views.signup)

3. VIEWS
   def signup(request):
       form = UserForm(request.POST)
       if form.is_valid():
           user = form.save()  # ← Appelle le modèle

4. MODELS
   class User(AbstractUser):
       # Django crée automatiquement la table

5. DATABASE
   INSERT INTO auth_user (email, password, ...) VALUES (...)

6. RESPONSE
   return redirect('accounts:profile')
   → HTTP 302 Redirect vers /accounts/profile/
```

---

## 🔑 Points Clés à Retenir

1. **URL Patterns** = "Quelle page pour quelle URL ?"
2. **Views** = "Que faire avec cette requête ?"
3. **Models** = "Comment sont structurées mes données ?"
4. **Database** = "Où sont stockées mes données ?"
5. **Serializer** = "Comment transformer mes données pour l'API ?"

---

## 📝 Dans Votre Projet SagaKore

### Structure des URLs
```
saga/urls.py (principal)
├── accounts/ → accounts/urls.py
├── cart/ → cart/urls.py
├── api/ → product/api/urls.py
├── api/ → accounts/api/urls.py
└── price-checker/ → price_checker/urls.py
```

### Types de Vues
- **Web** : `accounts/views.py` → Retourne du HTML
- **API** : `accounts/api/views.py` → Retourne du JSON
- **Admin** : `accounts/admin.py` → Interface d'administration

### Modèles Principaux
- **accounts** : User, Shopper, ShippingAddress
- **product** : Product, Category
- **cart** : Cart, CartItem

---

## 💡 Conseils

1. **Pour déboguer** : Ajoutez `print()` dans vos vues pour voir le flux
2. **Pour comprendre** : Suivez une requête de bout en bout
3. **Pour apprendre** : Modifiez une petite fonctionnalité et observez

---

*Document créé pour simplifier la compréhension de l'architecture Django dans le projet SagaKore*

