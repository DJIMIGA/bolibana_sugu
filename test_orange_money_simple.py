#!/usr/bin/env python
"""
Script simple pour tester Orange Money sans dépendances externes
"""

import os
import sys

# Ajouter le répertoire du projet au path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
sys.path.insert(0, os.path.join(project_dir, 'saga'))

# Charger les variables d'environnement manuellement
from dotenv import load_dotenv

# Charger .env
env_path = os.path.join(project_dir, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print("✓ Fichier .env chargé")

# Charger .env.secrets
env_secrets_path = os.path.join(project_dir, 'saga', '.env.secrets')
if os.path.exists(env_secrets_path):
    load_dotenv(env_secrets_path)
    print("✓ Fichier .env.secrets chargé")

print("\n🔍 Vérification des variables Orange Money...")
print("=" * 60)

# Vérifier les variables Orange Money
orange_money_vars = {
    'ORANGE_MONEY_ENABLED': os.getenv('ORANGE_MONEY_ENABLED'),
    'ORANGE_MONEY_ENV': os.getenv('ORANGE_MONEY_ENV'),
    'ORANGE_MONEY_MERCHANT_KEY': os.getenv('ORANGE_MONEY_MERCHANT_KEY'),
    'ORANGE_MONEY_CLIENT_ID': os.getenv('ORANGE_MONEY_CLIENT_ID'),
    'ORANGE_MONEY_CLIENT_SECRET': os.getenv('ORANGE_MONEY_CLIENT_SECRET'),
    'ORANGE_MONEY_CURRENCY': os.getenv('ORANGE_MONEY_CURRENCY'),
    'ORANGE_MONEY_LANGUAGE': os.getenv('ORANGE_MONEY_LANGUAGE'),
}

print("📋 Variables Orange Money:")
for var_name, var_value in orange_money_vars.items():
    if var_value:
        if 'SECRET' in var_name or 'KEY' in var_name:
            # Masquer les valeurs sensibles
            display_value = f"{var_value[:8]}..." if len(var_value) > 8 else "***"
        else:
            display_value = var_value
        print(f"  ✅ {var_name}: {display_value}")
    else:
        print(f"  ❌ {var_name}: Non défini")

# Vérifier la configuration
enabled = orange_money_vars['ORANGE_MONEY_ENABLED'] and orange_money_vars['ORANGE_MONEY_ENABLED'].lower() == 'true'
has_credentials = all([
    orange_money_vars['ORANGE_MONEY_MERCHANT_KEY'],
    orange_money_vars['ORANGE_MONEY_CLIENT_ID'],
    orange_money_vars['ORANGE_MONEY_CLIENT_SECRET']
])

print(f"\n🎯 Statut de la configuration:")
if enabled and has_credentials:
    print("✅ Orange Money est correctement configuré et activé")
    print(f"🌍 Environnement: {orange_money_vars['ORANGE_MONEY_ENV'] or 'dev'}")
    print(f"💰 Devise: {orange_money_vars['ORANGE_MONEY_CURRENCY'] or 'OUV'}")
    print(f"🌐 Langue: {orange_money_vars['ORANGE_MONEY_LANGUAGE'] or 'fr'}")
else:
    print("❌ Orange Money n'est pas correctement configuré")
    
    print(f"\n🔧 Diagnostic:")
    if not enabled:
        print("  - ORANGE_MONEY_ENABLED n'est pas défini ou n'est pas 'true'")
    if not orange_money_vars['ORANGE_MONEY_MERCHANT_KEY']:
        print("  - ORANGE_MONEY_MERCHANT_KEY manquant")
    if not orange_money_vars['ORANGE_MONEY_CLIENT_ID']:
        print("  - ORANGE_MONEY_CLIENT_ID manquant")
    if not orange_money_vars['ORANGE_MONEY_CLIENT_SECRET']:
        print("  - ORANGE_MONEY_CLIENT_SECRET manquant")

print("\n" + "=" * 60)
print("✅ Vérification terminée")

if enabled and has_credentials:
    print("\n🚀 Orange Money est prêt à être utilisé !")
    print("Vous pouvez maintenant tester le paiement Orange Money dans votre application.")
else:
    print("\n⚠️ Veuillez configurer les variables manquantes dans .env.secrets")

