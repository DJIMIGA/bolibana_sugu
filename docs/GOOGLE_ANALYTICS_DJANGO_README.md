# Intégration Google Analytics 4 (GA4) & Consentement Cookies dans Django

## 1. Objectif
Mettre en place Google Analytics 4 dans un projet Django tout en respectant le RGPD : injection conditionnelle du script selon le consentement utilisateur, gestion des événements différés, et bonnes pratiques de sécurité.

---

## 2. Flux technique

1. **Consentement cookies** : l’utilisateur choisit s’il accepte les cookies analytics/marketing.
2. **Tag Django custom** : `{% render_cookie_conditional_scripts %}` injecte dynamiquement les scripts GA4/Facebook Pixel selon le consentement.
3. **Injection du script** : le script GA4 n’est présent dans le HTML que si le consentement analytics est donné.
4. **Envoi d’événements** : les événements sont envoyés à GA4 uniquement si le script est chargé.

---

## 3. Bonnes pratiques & RGPD
- **Aucun script de tracking sans consentement**.
- **Pas de données sensibles dans le front**.
- **Utilisation du filtre `|safe`** pour que le HTML des scripts soit interprété (et non affiché comme texte).
- **Scripts dans le `<body>`** : placement courant pour le tracking, pas de problème de fonctionnement.

---

## 4. Problèmes rencontrés & solutions

### Problème 1 : Le script GA4 n’est pas exécuté, rien dans Network
- **Symptôme** : le code source HTML contient `&lt;script&gt;` au lieu de `<script>`, aucune requête réseau vers Google, `gtag` non défini.
- **Cause** : le tag Django retourne une chaîne HTML qui est échappée par défaut.
- **Solution** : utiliser le filtre `|safe` dans le template :
  ```django
  {% render_cookie_conditional_scripts as cookie_scripts %}
  {{ cookie_scripts|safe }}
  ```

### Problème 2 : Extensions ou navigateur bloquent le script
- **Symptôme** : même avec le bon HTML, aucune requête réseau.
- **Solution** : tester en navigation privée, désactiver les extensions (adblock, privacy, etc.), essayer un autre navigateur.

### Problème 3 : Ordre des scripts
- **Symptôme** : `gtag` non défini si le script async n’est pas chargé avant l’appel à `gtag()`.
- **Solution** : toujours placer le `<script async src=...>` avant le script d’initialisation.

---

## 5. Guide de debug rapide

1. **Vérifier le HTML rendu** : balises `<script>` réelles, pas de texte encodé.
2. **Onglet Network** : présence d’une requête vers `googletagmanager.com`.
3. **Console JS** : `typeof gtag` doit retourner `function`.
4. **Tester l’envoi d’un événement** :
   ```js
   gtag('event', 'test_event', { test_param: 123 });
   ```
5. **Vérifier dans Google Analytics** : données en temps réel ou DebugView.

---

## 6. Conseils de placement des scripts
- **Dans le `<body>` ou en bas du `<head>`** : les deux sont valides pour GA4.
- **Avant tout code qui dépend de `gtag`**.

---

## 7. Résumé des erreurs courantes
- **HTML échappé** : balises `<script>` non interprétées → utiliser `|safe`.
- **Script bloqué** : extensions/adblockers → tester sans.
- **Ordre des scripts** : toujours charger le JS externe avant d’appeler `gtag()`.
- **Pas de consentement** : script non injecté, comportement normal.

---

## 8. Exemple de code Django

Dans le template principal :
```django
{% render_cookie_conditional_scripts as cookie_scripts %}
{{ cookie_scripts|safe }}
```

Dans le tag custom (extrait) :
```python
return f"""
<script async src=\"https://www.googletagmanager.com/gtag/js?id={ga_id}\"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{ga_id}', {{ ... }});
</script>
"""
```

---

## 9. Pour aller plus loin
- **Documenter le flux de consentement** (cookie banner, stockage du choix, etc.).
- **Ajouter d’autres scripts conditionnels** (Facebook Pixel, etc.) dans le même tag custom.
- **Vérifier la conformité RGPD régulièrement**.

---

**Ce README synthétise l’intégration, les galères rencontrées, et les solutions pour une intégration GA4 propre, sécurisée et conforme dans Django.** 