#!/usr/bin/env python
"""
Script de debug pour Google Analytics
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from core.models import SiteConfiguration, CookieConsent
from django.test import RequestFactory
from core.templatetags.cookie_tags import render_analytics_scripts

def test_ga_configuration():
    """Test de la configuration Google Analytics"""
    print("🔍 Test de la configuration Google Analytics")
    print("=" * 50)
    
    # 1. Vérifier la configuration
    try:
        config = SiteConfiguration.get_config()
        print(f"✅ Configuration trouvée")
        print(f"📊 Google Analytics ID: {config.google_analytics_id}")
        
        if not config.google_analytics_id:
            print("❌ Aucun ID Google Analytics configuré")
            print("💡 Allez dans l'admin Django > Configuration du site")
            return False
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        return False
    
    # 2. Simuler une requête avec consentement
    factory = RequestFactory()
    request = factory.get('/')
    request.session = {}
    
    # Créer un consentement de test
    consent = CookieConsent.objects.create(
        session_id='test_session',
        analytics=True,
        marketing=True
    )
    request.cookie_consent = consent
    
    # 3. Tester le rendu du script
    try:
        from django.template import Context
        context = Context({'request': request})
        
        script = render_analytics_scripts(context)
        
        if script:
            print("✅ Script Google Analytics généré")
            print("📝 Contenu du script:")
            print("-" * 30)
            print(script)
            print("-" * 30)
            
            # Vérifier que l'ID est dans le script
            if config.google_analytics_id in script:
                print("✅ ID Google Analytics trouvé dans le script")
            else:
                print("❌ ID Google Analytics manquant dans le script")
                return False
        else:
            print("❌ Aucun script généré")
            return False
            
    except Exception as e:
        print(f"❌ Erreur génération script: {e}")
        return False
    
    # 4. Nettoyer
    consent.delete()
    
    print("\n🎯 Prochaines étapes:")
    print("1. Ouvrez votre site dans le navigateur")
    print("2. Acceptez les cookies analytics")
    print("3. Ouvrez la console développeur (F12)")
    print("4. Vérifiez les messages de debug")
    print("5. Allez dans Google Analytics > Temps réel")
    
    return True

if __name__ == '__main__':
    test_ga_configuration() 