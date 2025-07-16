#!/usr/bin/env python
import os
import sys
import django
import requests

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

def test_cookie_api():
    """Test de l'API de consentement cookies"""
    try:
        # Test de l'API
        response = requests.post('http://127.0.0.1:8000/core/api/cookie-consent/', data={
            'analytics': 'true',
            'marketing': 'false'
        })
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ API fonctionne")
            return True
        else:
            print("❌ API ne fonctionne pas")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_cookie_api() 