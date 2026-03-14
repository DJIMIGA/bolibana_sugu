#!/usr/bin/env python
"""
Script de debug pour Orange Money
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
    
    print("🔍 DEBUG Orange Money - Analyse détaillée...")
    print("=" * 60)
    
    # 1. Vérifier les variables d'environnement directement
    print("📋 Variables d'environnement directes:")
    env_vars = [
        'ORANGE_MONEY_ENABLED',
        'ORANGE_MONEY_ENV', 
        'ORANGE_MONEY_MERCHANT_KEY',
        'ORANGE_MONEY_CLIENT_ID',
        'ORANGE_MONEY_CLIENT_SECRET'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'SECRET' in var or 'KEY' in var:
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: Non défini")
    
    # 2. Vérifier la configuration Django
    print(f"\n📋 Configuration Django (settings.ORANGE_MONEY_CONFIG):")
    config = settings.ORANGE_MONEY_CONFIG
    print(f"  - enabled: {config.get('enabled')} (type: {type(config.get('enabled'))})")
    print(f"  - environment: {config.get('environment')}")
    print(f"  - merchant_key: {'✅ Configuré' if config.get('merchant_key') else '❌ Manquant'}")
    print(f"  - client_id: {'✅ Configuré' if config.get('client_id') else '❌ Manquant'}")
    print(f"  - client_secret: {'✅ Configuré' if config.get('client_secret') else '❌ Manquant'}")
    
    # 3. Test détaillé de is_enabled()
    print(f"\n🧪 Test détaillé de is_enabled():")
    print(f"  - config['enabled']: {config.get('enabled')}")
    print(f"  - config['merchant_key']: {bool(config.get('merchant_key'))}")
    print(f"  - config['client_id']: {bool(config.get('client_id'))}")
    print(f"  - config['client_secret']: {bool(config.get('client_secret'))}")
    
    # Test de la logique all()
    all_conditions = [
        config.get('merchant_key'),
        config.get('client_id'),
        config.get('client_secret')
    ]
    print(f"  - all(credentials): {all(all_conditions)}")
    
    # Test final
    final_result = config.get('enabled') and all(all_conditions)
    print(f"  - Résultat final: {final_result}")
    
    # 4. Test du service
    print(f"\n🎯 Test du service Orange Money:")
    is_enabled = orange_money_service.is_enabled()
    print(f"  - orange_money_service.is_enabled(): {is_enabled}")
    
    # 5. Diagnostic
    print(f"\n🔧 Diagnostic:")
    if not config.get('enabled'):
        print("  ❌ Le service n'est pas activé (enabled=False)")
    if not config.get('merchant_key'):
        print("  ❌ Merchant Key manquant")
    if not config.get('client_id'):
        print("  ❌ Client ID manquant")
    if not config.get('client_secret'):
        print("  ❌ Client Secret manquant")
    
    if is_enabled:
        print("✅ Orange Money est correctement configuré !")
    else:
        print("❌ Orange Money n'est pas configuré correctement.")
    
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

