#!/usr/bin/env python
"""
Test simple des templates d'erreur
"""
import os

def test_template_files():
    """Vérifier que les templates d'erreur existent"""
    print("🔍 Vérification des templates d'erreur...")
    
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
            
            # Vérifier le contenu
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Vérifications de base
                checks = [
                    ('DOCTYPE', 'DOCTYPE html' in content),
                    ('BoliBana', 'BoliBana' in content),
                    ('Tailwind', 'tailwind' in content.lower()),
                    ('CSS', 'css' in content.lower()),
                ]
                
                for check_name, result in checks:
                    status = "✅" if result else "❌"
                    print(f"   {status} Contient {check_name}")
                    
            except Exception as e:
                print(f"   ❌ Erreur lecture: {e}")
        else:
            print(f"❌ {path} n'existe pas")

def test_settings_config():
    """Vérifier la configuration des templates"""
    print("\n🔍 Vérification de la configuration...")
    
    # Vérifier le dossier templates principal
    if os.path.exists('saga/templates'):
        print("✅ Dossier saga/templates existe")
        
        # Lister les fichiers
        files = os.listdir('saga/templates')
        error_files = [f for f in files if f in ['404.html', '500.html', '403.html']]
        
        if error_files:
            print(f"✅ Templates d'erreur trouvés: {', '.join(error_files)}")
        else:
            print("❌ Aucun template d'erreur trouvé")
    else:
        print("❌ Dossier saga/templates n'existe pas")

def test_django_auto_handlers():
    """Expliquer comment Django gère les erreurs automatiquement"""
    print("\n📚 Comment Django gère les pages d'erreur :")
    print("1. Django cherche automatiquement les templates suivants :")
    print("   - 404.html (Page non trouvée)")
    print("   - 500.html (Erreur serveur)")
    print("   - 403.html (Accès interdit)")
    print("   - 400.html (Requête invalide)")
    print("2. Il les cherche dans l'ordre :")
    print("   - Dossier templates principal (saga/templates/)")
    print("   - Dossiers templates des applications")
    print("3. Si DEBUG = False, Django utilise ces templates")
    print("4. Si DEBUG = True, Django affiche les erreurs détaillées")

if __name__ == '__main__':
    print("🚀 Test simple des pages d'erreur BoliBana")
    print("=" * 50)
    
    test_template_files()
    test_settings_config()
    test_django_auto_handlers()
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés !")
    print("\n💡 Pour tester en production :")
    print("1. Déployer sur Heroku")
    print("2. Visiter une URL inexistante (ex: /page-inexistante)")
    print("3. Vérifier que la page 404 s'affiche") 