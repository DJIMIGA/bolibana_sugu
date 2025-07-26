#!/usr/bin/env python
"""
Test des pages d'erreur en mode production (DEBUG=False)
"""
import os
import sys
import django
from django.test import TestCase, Client
from django.conf import settings

# Forcer DEBUG = False pour le test
os.environ['DEBUG'] = 'False'

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

def test_error_pages_production():
    """Test les pages d'erreur en mode production"""
    print("🔍 Test des pages d'erreur en mode production (DEBUG=False)...")
    
    # Vérifier que DEBUG est bien False
    print(f"DEBUG = {settings.DEBUG}")
    
    client = Client()
    
    # Test 404
    print("\n🧪 Test 404...")
    try:
        response = client.get('/core/test/404/')
        print(f"Status: {response.status_code}")
        print(f"Template utilisé: {response.template_name}")
        print(f"Contient 'BoliBana': {'Oui' if 'BoliBana' in str(response.content) else 'Non'}")
        print(f"Contient '404': {'Oui' if '404' in str(response.content) else 'Non'}")
    except Exception as e:
        print(f"Erreur: {e}")
    
    # Test 500
    print("\n🧪 Test 500...")
    try:
        response = client.get('/core/test/500/')
        print(f"Status: {response.status_code}")
        print(f"Template utilisé: {response.template_name}")
        print(f"Contient 'BoliBana': {'Oui' if 'BoliBana' in str(response.content) else 'Non'}")
        print(f"Contient '500': {'Oui' if '500' in str(response.content) else 'Non'}")
    except Exception as e:
        print(f"Erreur: {e}")
    
    # Test 403
    print("\n🧪 Test 403...")
    try:
        response = client.get('/core/test/403/')
        print(f"Status: {response.status_code}")
        print(f"Template utilisé: {response.template_name}")
        print(f"Contient 'BoliBana': {'Oui' if 'BoliBana' in str(response.content) else 'Non'}")
        print(f"Contient '403': {'Oui' if '403' in str(response.content) else 'Non'}")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == '__main__':
    print("🚀 Test des pages d'erreur en mode production")
    print("=" * 50)
    
    test_error_pages_production()
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés !") 