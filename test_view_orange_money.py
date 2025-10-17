#!/usr/bin/env python
"""
Test spécifique pour la vue Orange Money
"""

import os
import sys

# Ajouter le répertoire du projet au path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
sys.path.insert(0, os.path.join(project_dir, 'saga'))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')

try:
    import django
    django.setup()
    
    from django.conf import settings
    from cart.orange_money_service import orange_money_service
    from cart import views
    
    print("🔍 Test spécifique de la vue Orange Money...")
    print("=" * 60)
    
    # 1. Vérifier l'import du service dans views
    print("📋 Vérification des imports:")
    print(f"  - orange_money_service importé: {'✅' if hasattr(views, 'orange_money_service') else '❌'}")
    
    # 2. Vérifier la configuration
    print(f"\n📋 Configuration:")
    config = settings.ORANGE_MONEY_CONFIG
    print(f"  - enabled: {config.get('enabled')}")
    print(f"  - merchant_key: {'✅' if config.get('merchant_key') else '❌'}")
    print(f"  - client_id: {'✅' if config.get('client_id') else '❌'}")
    print(f"  - client_secret: {'✅' if config.get('client_secret') else '❌'}")
    
    # 3. Test direct du service
    print(f"\n🧪 Test direct du service:")
    is_enabled = orange_money_service.is_enabled()
    print(f"  - orange_money_service.is_enabled(): {is_enabled}")
    
    # 4. Test de l'instance du service
    print(f"\n🔍 Test de l'instance du service:")
    print(f"  - Type du service: {type(orange_money_service)}")
    print(f"  - Config du service: {orange_money_service.config}")
    print(f"  - Service enabled: {orange_money_service.config.get('enabled')}")
    
    # 5. Test de la logique is_enabled
    print(f"\n🧪 Test de la logique is_enabled:")
    enabled = orange_money_service.config.get('enabled')
    has_credentials = all([
        orange_money_service.config.get('merchant_key'),
        orange_money_service.config.get('client_id'),
        orange_money_service.config.get('client_secret')
    ])
    print(f"  - enabled: {enabled}")
    print(f"  - has_credentials: {has_credentials}")
    print(f"  - Résultat final: {enabled and has_credentials}")
    
    # 6. Vérifier si c'est le même objet
    print(f"\n🔍 Vérification de l'instance:")
    print(f"  - orange_money_service dans views: {views.orange_money_service}")
    print(f"  - orange_money_service importé: {orange_money_service}")
    print(f"  - Même instance: {views.orange_money_service is orange_money_service}")
    
    if is_enabled:
        print("\n✅ Le service Orange Money devrait être disponible !")
    else:
        print("\n❌ Le service Orange Money n'est pas disponible.")
        print("🔧 Vérifiez la configuration dans .env.secrets")
    
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

