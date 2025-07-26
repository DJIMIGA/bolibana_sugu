#!/usr/bin/env python
"""
Script de test pour vérifier le rendu des pages d'erreur
"""
import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse
from django.http import Http404, HttpResponseServerError, HttpResponseForbidden
from django.template.loader import render_to_string

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

def test_error_pages():
    """Test le rendu des pages d'erreur"""
    print("🔍 Test du rendu des pages d'erreur...")
    
    # Test 404
    try:
        html_404 = render_to_string('404.html')
        print("✅ Template 404.html se rend correctement")
        print(f"   Taille: {len(html_404)} caractères")
        print(f"   Contient '404': {'Oui' if '404' in html_404 else 'Non'}")
        print(f"   Contient 'BoliBana': {'Oui' if 'BoliBana' in html_404 else 'Non'}")
    except Exception as e:
        print(f"❌ Erreur avec 404.html: {e}")
    
    # Test 500
    try:
        html_500 = render_to_string('500.html')
        print("✅ Template 500.html se rend correctement")
        print(f"   Taille: {len(html_500)} caractères")
        print(f"   Contient '500': {'Oui' if '500' in html_500 else 'Non'}")
        print(f"   Contient 'BoliBana': {'Oui' if 'BoliBana' in html_500 else 'Non'}")
    except Exception as e:
        print(f"❌ Erreur avec 500.html: {e}")
    
    # Test 403
    try:
        html_403 = render_to_string('403.html')
        print("✅ Template 403.html se rend correctement")
        print(f"   Taille: {len(html_403)} caractères")
        print(f"   Contient '403': {'Oui' if '403' in html_403 else 'Non'}")
        print(f"   Contient 'BoliBana': {'Oui' if 'BoliBana' in html_403 else 'Non'}")
    except Exception as e:
        print(f"❌ Erreur avec 403.html: {e}")

def test_error_handlers():
    """Test les gestionnaires d'erreur Django"""
    print("\n🔍 Test des gestionnaires d'erreur...")
    
    # Vérifier si les handlers sont définis dans urls.py
    try:
        with open('saga/urls.py', 'r', encoding='utf-8') as f:
            urls_content = f.read()
            
        if 'handler404' in urls_content:
            print("✅ handler404 défini dans urls.py")
        else:
            print("⚠️  handler404 non défini - Django utilisera les templates par défaut")
            
        if 'handler500' in urls_content:
            print("✅ handler500 défini dans urls.py")
        else:
            print("⚠️  handler500 non défini - Django utilisera les templates par défaut")
            
        if 'handler403' in urls_content:
            print("✅ handler403 défini dans urls.py")
        else:
            print("⚠️  handler403 non défini - Django utilisera les templates par défaut")
            
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de urls.py: {e}")

def test_template_paths():
    """Vérifier que les templates existent aux bons endroits"""
    print("\n🔍 Vérification des chemins des templates...")
    
    template_paths = [
        'saga/templates/404.html',
        'saga/templates/500.html', 
        'saga/templates/403.html'
    ]
    
    for path in template_paths:
        if os.path.exists(path):
            print(f"✅ {path} existe")
            size = os.path.getsize(path)
            print(f"   Taille: {size} octets")
        else:
            print(f"❌ {path} n'existe pas")

if __name__ == '__main__':
    print("🚀 Test des pages d'erreur BoliBana")
    print("=" * 50)
    
    test_template_paths()
    test_error_pages()
    test_error_handlers()
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés !") 