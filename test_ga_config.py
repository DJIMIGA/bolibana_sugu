#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from core.models import SiteConfiguration

def test_ga_config():
    """Test de la configuration Google Analytics"""
    try:
        config = SiteConfiguration.get_config()
        print(f"✅ Configuration trouvée")
        print(f"📊 Google Analytics ID: {config.google_analytics_id}")
        print(f"🌐 Site: {config.site_name}")
        
        if config.google_analytics_id:
            print("✅ Google Analytics est configuré")
            return True
        else:
            print("❌ Google Analytics ID manquant")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_ga_config() 