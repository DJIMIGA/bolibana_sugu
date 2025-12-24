# Compatibilité API Backend ↔ Mobile

## ✅ Endpoints disponibles dans le backend

### Authentification
- **POST** `/api/token/` - Connexion (CustomTokenObtainPairView avec email)
  - Body: `{ "email": "...", "password": "..." }`
  - Response: `{ "access": "...", "refresh": "..." }`
- **POST** `/api/token/refresh/` - Rafraîchir le token
  - Body: `{ "refresh": "..." }`
  - Response: `{ "access": "..." }`
- **POST** `/api/token/verify/` - Vérifier le token

### Profil utilisateur
- **GET** `/api/profile/` - Récupérer le profil
  - Response: `{ "id", "email", "first_name", "last_name", "phone", "date_of_birth", "fidelys_number" }`
- **PUT/PATCH** `/api/profile/update/` - Mettre à jour le profil

### Adresses
- **GET** `/api/addresses/` - Liste des adresses
- **POST** `/api/addresses/create/` - Créer une adresse
- **GET** `/api/addresses/<id>/` - Détails d'une adresse
- **PUT/PATCH** `/api/addresses/<id>/update/` - Mettre à jour
- **DELETE** `/api/addresses/<id>/delete/` - Supprimer
- **POST** `/api/addresses/<id>/set-default/` - Définir comme défaut

### Produits
- **GET** `/api/products/` - Liste des produits
  - Query params: `?category=<id>&brand=<id>&is_available=<bool>&search=<term>&ordering=<field>`
  - Response: `ProductListSerializer` avec `name`, `slug`, `price`, `category`, `brand`, `feature_image`
- **GET** `/api/products/<slug>/` - Détails d'un produit
  - Response: `ProductDetailSerializer` avec `name`, `description`, `images`, `variants`, etc.
- **GET** `/api/products/<id>/variants/` - Variantes d'un produit

### Catégories
- **GET** `/api/categories/` - Liste des catégories
  - Response: `CategorySerializer` avec `id`, `name`, `slug`, `parent`, `children` (récursif)
- **GET** `/api/categories/<slug>/` - Détails d'une catégorie
- **GET** `/api/categories/<slug>/products/` - Produits d'une catégorie

### Panier
- **GET** `/api/cart/` - Récupérer le panier
- **POST** `/api/cart/` - Créer/Ajouter au panier
- **PUT/PATCH** `/api/cart/<id>/` - Modifier le panier
- **DELETE** `/api/cart/<id>/` - Supprimer du panier

## ⚠️ Différences à adapter

### 1. User (Profil)
**Backend retourne :**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+221...",
  "date_of_birth": "1990-01-01",
  "fidelys_number": "FID123"
}
```

**Mobile attend :**
```typescript
{
  id: number;
  email: string;
  full_name?: string;  // ❌ Backend retourne first_name + last_name
  phone?: string;
  // ...
}
```

**Solution :** Adapter le type TypeScript ou mapper dans le slice Redux.

### 2. Product
**Backend retourne :**
```json
{
  "id": 1,
  "name": "Produit",  // ❌ Mobile attend "title"
  "slug": "produit",
  "price": 10000,
  "feature_image": {  // ❌ Structure différente
    "id": 1,
    "image": "/media/...",
    "ordre": 1
  },
  "category": { "id": 1, "name": "...", "slug": "..." },
  "images": [...],
  "variants": [...]
}
```

**Mobile attend :**
```typescript
{
  id: number;
  title: string;  // ❌ Backend retourne "name"
  image?: string;  // ❌ Backend retourne "feature_image" avec structure
  // ...
}
```

**Solution :** Mapper `name` → `title` et `feature_image.image` → `image` dans le slice.

### 3. Category
**Backend retourne :**
```json
{
  "id": 1,
  "name": "Catégorie",
  "slug": "categorie",
  "parent": null,
  "children": [  // ✅ Récursif
    { "id": 2, "name": "Sous-catégorie", ... }
  ]
}
```

**Mobile attend :**
```typescript
{
  id: number;
  name: string;
  slug: string;
  parent?: number;
  // ❌ Pas de "children" dans le type
  color: string;  // ❌ Pas dans le backend
  is_main: boolean;  // ❌ Pas dans le backend
}
```

**Solution :** Adapter le type TypeScript pour inclure `children` et gérer les champs optionnels.

### 4. Cart
**Backend retourne :** `fields = '__all__'` (tous les champs du modèle)

**À vérifier :** Structure exacte du modèle `Cart` pour adapter le type TypeScript.

## 🔧 Actions à effectuer

1. **Adapter les types TypeScript** pour correspondre aux sérialiseurs Django
2. **Créer des mappers** dans les slices Redux pour transformer les données
3. **Tester chaque endpoint** pour valider la compatibilité
4. **Documenter les différences** dans le code avec des commentaires




