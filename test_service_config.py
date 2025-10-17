#!/usr/bin/env python
"""
Test pour vérifier que le service Orange Money lit bien les variables
"""

import os
import sys

# Ajouter le répertoire du projet au path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
sys.path.insert(0, os.path.join(project_dir, 'saga'))

# Charger les variables d'environnement
from dotenv import load_dotenv

# Charger .env.secrets
env_secrets_path = os.path.join(project_dir, 'saga', '.env.secrets')
if os.path.exists(env_secrets_path):
    load_dotenv(env_secrets_path)
    print("✓ Fichier .env.secrets chargé")
else:
    print("❌ Fichier .env.secrets non trouvé")

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')

try:
    import django
    django.setup()
    
    from django.conf import settings
    from cart.orange_money_service import orange_money_service
    
    print("\n🔍 Test du service Orange Money...")
    print("=" * 60)
    
    # Vérifier la configuration
    config = settings.ORANGE_MONEY_CONFIG
    print(f"📋 Configuration lue par Django:")
    print(f"  - Activé: {config.get('enabled', 'Non défini')}")
    print(f"  - Environnement: {config.get('environment', 'Non défini')}")
    print(f"  - Merchant Key: {'✅ Configuré' if config.get('merchant_key') else '❌ Manquant'}")
    print(f"  - Client ID: {'✅ Configuré' if config.get('client_id') else '❌ Manquant'}")
    print(f"  - Client Secret: {'✅ Configuré' if config.get('client_secret') else '❌ Manquant'}")
    
    # Tester le service
    print(f"\n🧪 Test du service Orange Money:")
    is_enabled = orange_money_service.is_enabled()
    print(f"  - Service activé: {'✅ Oui' if is_enabled else '❌ Non'}")
    
    if is_enabled:
        print("✅ Le service Orange Money est correctement configuré !")
        print("🚀 Prêt à être utilisé dans votre application.")
    else:
        print("❌ Le service Orange Money n'est pas configuré.")
        print("📝 Veuillez ajouter vos credentials dans saga/.env.secrets")
    
    print("\n" + "=" * 60)
    
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
