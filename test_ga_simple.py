#!/usr/bin/env python
"""
Test simple pour Google Analytics
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

def test_ga():
    """Test simple de Google Analytics"""
    print("🔍 Test Google Analytics")
    print("=" * 30)
    
    try:
        from core.models import SiteConfiguration
        config = SiteConfiguration.get_config()
        
        print(f"✅ Configuration trouvée")
        print(f"📊 ID Google Analytics: {config.google_analytics_id}")
        
        if config.google_analytics_id:
            print("✅ Google Analytics configuré")
            print("\n🎯 Prochaines étapes:")
            print("1. Ouvrez http://127.0.0.1:8000")
            print("2. Acceptez les cookies analytics")
            print("3. Ouvrez la console (F12)")
            print("4. Vérifiez les messages de debug")
            print("5. Testez: gtag('event', 'test', {event_category: 'debug'})")
            print("6. Allez dans GA > Temps réel")
        else:
            print("❌ Aucun ID Google Analytics")
            print("💡 Configurez l'ID dans l'admin Django")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    test_ga() 