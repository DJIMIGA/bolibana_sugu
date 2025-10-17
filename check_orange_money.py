#!/usr/bin/env python
"""
Script simple pour vérifier la configuration Orange Money
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
    
    print("🔍 Vérification de la configuration Orange Money...")
    print("=" * 60)
    
    # Vérifier si la configuration existe
    if hasattr(settings, 'ORANGE_MONEY_CONFIG'):
        config = settings.ORANGE_MONEY_CONFIG
        print(f"📋 Configuration Orange Money trouvée:")
        print(f"  - Activé: {config.get('enabled', 'Non défini')}")
        print(f"  - Environnement: {config.get('environment', 'Non défini')}")
        print(f"  - Merchant Key: {'✅ Configuré' if config.get('merchant_key') else '❌ Manquant'}")
        print(f"  - Client ID: {'✅ Configuré' if config.get('client_id') else '❌ Manquant'}")
        print(f"  - Client Secret: {'✅ Configuré' if config.get('client_secret') else '❌ Manquant'}")
        print(f"  - Devise: {config.get('currency', 'Non défini')}")
        print(f"  - Langue: {config.get('language', 'Non défini')}")
        
        # Vérifier si le service est activé
        is_enabled = config.get('enabled', False) and all([
            config.get('merchant_key'),
            config.get('client_id'),
            config.get('client_secret')
        ])
        
        print(f"\n🎯 Statut du service:")
        if is_enabled:
            print("✅ Orange Money est correctement configuré et activé")
        else:
            print("❌ Orange Money n'est pas configuré correctement")
            
            # Diagnostiquer le problème
            print(f"\n🔧 Diagnostic:")
            if not config.get('enabled', False):
                print("  - Le service n'est pas activé")
            if not config.get('merchant_key'):
                print("  - Merchant Key manquant")
            if not config.get('client_id'):
                print("  - Client ID manquant")
            if not config.get('client_secret'):
                print("  - Client Secret manquant")
        
        print(f"\n🌐 URLs configurées:")
        print(f"  - Token URL: {config.get('token_url', 'Non défini')}")
        print(f"  - WebPayment URL: {config.get('webpayment_url', 'Non défini')}")
        print(f"  - Status URL: {config.get('status_url', 'Non défini')}")
        print(f"  - Payment URL: {config.get('payment_url', 'Non défini')}")
        
    else:
        print("❌ Configuration Orange Money non trouvée dans settings.py")
    
    print("\n" + "=" * 60)
    print("✅ Test terminé")
    
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Assurez-vous que Django est installé")
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
