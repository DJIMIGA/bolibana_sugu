# Configuration Facebook Pixel (Meta Pixel) dans Django

## 1. Récupération de l'ID Facebook Pixel

### Étape 1 : Créer le Pixel
1. Va sur [Meta Events Manager](https://www.facebook.com/events_manager2/list)
2. Clique sur **"Ajouter un événement"** > "Depuis une nouvelle source de données" > "Pixel Internet"
3. Donne un nom à ton Pixel (ex: "BoliBana Website")
4. Associe-le à ton site web
5. **Copie l'ID du Pixel** (suite de chiffres, ex: `123456789012345`)

### Étape 2 : Configurer dans Django
1. Va dans l'admin Django : `/admin/core/siteconfiguration/`
2. Dans la section **"Configuration du site"**, colle ton ID dans le champ **"ID du Facebook Pixel"**
3. Sauvegarde

---

## 2. Fonctionnement automatique

### Consentement cookies
- **Si l'utilisateur accepte les cookies marketing** → Le Pixel est injecté automatiquement
- **Si l'utilisateur refuse** → Aucun script Facebook n'est chargé (conforme RGPD)

### Événements automatiques
- **PageView** : envoyé automatiquement à chaque visite de page
- **Aucune action requise** de ta part pour le tracking de base

---

## 3. Ajouter des événements personnalisés

### Événement d'achat (Purchase)
Dans le template de confirmation d'achat (`order_confirmation.html`) :

```django
{% if request.cookie_consent and request.cookie_consent.marketing %}
<script>
  fbq('track', 'Purchase', {
    value: {{ order.total|floatformat:2 }},
    currency: 'EUR',
    content_ids: [{{ order.id }}],
    content_type: 'product'
  });
</script>
{% endif %}
```

### Événement d'ajout au panier (AddToCart)
Dans le template du panier ou après ajout d'un produit :

```django
{% if request.cookie_consent and request.cookie_consent.marketing %}
<script>
  fbq('track', 'AddToCart', {
    value: {{ product.price|floatformat:2 }},
    currency: 'EUR',
    content_ids: [{{ product.id }}],
    content_type: 'product'
  });
</script>
{% endif %}
```

### Événement d'inscription (CompleteRegistration)
Dans le template de confirmation d'inscription :

```django
{% if request.cookie_consent and request.cookie_consent.marketing %}
<script>
  fbq('track', 'CompleteRegistration', {
    value: 0,
    currency: 'EUR'
  });
</script>
{% endif %}
```

---

## 4. Événements disponibles

### Événements e-commerce
- `AddToCart` : Ajout au panier
- `InitiateCheckout` : Début de commande
- `AddPaymentInfo` : Ajout d'informations de paiement
- `Purchase` : Achat finalisé
- `ViewContent` : Vue d'un produit
- `Search` : Recherche

### Événements généraux
- `PageView` : Vue de page (automatique)
- `CompleteRegistration` : Inscription
- `Contact` : Contact
- `Subscribe` : Abonnement

---

## 5. Vérification et debug

### Vérifier que le Pixel fonctionne
1. **Accepte les cookies marketing** sur ton site
2. **Ouvre les DevTools** (F12) > onglet Network
3. **Cherche des requêtes** vers `facebook.com` ou `fbevents.js`
4. **Vérifie dans Meta Events Manager** que les événements arrivent

### Debug en console
```javascript
// Vérifier que fbq est défini
typeof fbq

// Tester un événement manuellement
fbq('track', 'TestEvent', { test: true });
```

---

## 6. Utilisation pour la publicité

### Retargeting
1. Dans **Facebook Ads Manager**, crée une audience personnalisée
2. Sélectionne **"Trafic du site web"**
3. Choisis les événements à cibler (ex: "Tous les visiteurs", "Ajouts au panier")

### Mesure des conversions
1. Dans **Facebook Ads Manager**, crée une campagne
2. Sélectionne **"Conversions"** comme objectif
3. Choisis l'événement à optimiser (ex: "Purchase")

---

## 7. Bonnes pratiques RGPD

### Obligations
- **Consentement explicite** avant injection du Pixel ✅
- **Information claire** dans la politique de confidentialité
- **Possibilité de retrait** du consentement

### Implémentation actuelle
- Le Pixel n'est injecté que si `request.cookie_consent.marketing` est `True`
- Aucun tracking sans consentement
- Conforme aux exigences RGPD

---

## 8. Exemple complet d'événement e-commerce

```django
{% if request.cookie_consent and request.cookie_consent.marketing %}
<script>
  fbq('track', 'Purchase', {
    value: {{ order.total|floatformat:2 }},
    currency: 'EUR',
    content_ids: [{% for item in order.items.all %}{{ item.product.id }}{% if not forloop.last %},{% endif %}{% endfor %}],
    content_type: 'product',
    num_items: {{ order.items.count }},
    order_id: '{{ order.id }}'
  });
</script>
{% endif %}
```

---

## 9. Résolution de problèmes

### Le Pixel ne se charge pas
- Vérifie que l'ID est bien configuré dans l'admin
- Vérifie que le consentement marketing est accepté
- Désactive les bloqueurs de pub pour tester

### Les événements n'apparaissent pas
- Vérifie dans Meta Events Manager (délai de quelques minutes)
- Utilise le Testeur d'événements Facebook
- Vérifie la console JS pour les erreurs

---

**Ce guide couvre l'installation, la configuration et l'utilisation du Facebook Pixel dans ton projet Django, avec respect du RGPD et bonnes pratiques.** 