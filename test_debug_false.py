#!/usr/bin/env python
"""
Test simple avec DEBUG=False
"""
import os

# Forcer DEBUG = False
os.environ['DEBUG'] = 'False'

print("🔍 Configuration DEBUG = False")
print("Pour tester les pages d'erreur personnalisées :")
print("1. Redémarrer le serveur Django")
print("2. Visiter http://127.0.0.1:8000/core/test/404/")
print("3. Vous devriez voir la page 404 personnalisée BoliBana")
print("4. Pas de page de debug technique")

print("\n💡 En production (Heroku) :")
print("- DEBUG est automatiquement False")
print("- Les pages d'erreur personnalisées s'affichent")
print("- Visiter une URL inexistante pour tester") 