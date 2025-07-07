#!/usr/bin/env python
"""
Script de test pour vérifier la configuration email
Usage: python test_email.py
"""

import os
import sys
import django
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

def test_email_configuration():
    """Teste la configuration email"""
    print("🧪 === TEST DE CONFIGURATION EMAIL ===")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Non configuré')}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Non configuré')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Non configuré')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Non configuré')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Non configuré')}")
    print(f"EMAIL_HOST_PASSWORD: {'Configuré' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'Non configuré'}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Non configuré')}")
    
    # Test d'envoi d'email simple
    print("\n📧 === TEST D'ENVOI D'EMAIL ===")
    
    try:
        # Email de test
        subject = "Test de configuration email - SagaKore"
        message = """
        Ceci est un email de test pour vérifier la configuration email de SagaKore.
        
        Si vous recevez cet email, la configuration est correcte !
        
        Configuration actuelle:
        - Backend: {backend}
        - Host: {host}
        - Port: {port}
        - TLS: {tls}
        
        Cordialement,
        L'équipe SagaKore
        """.format(
            backend=getattr(settings, 'EMAIL_BACKEND', 'Non configuré'),
            host=getattr(settings, 'EMAIL_HOST', 'Non configuré'),
            port=getattr(settings, 'EMAIL_PORT', 'Non configuré'),
            tls=getattr(settings, 'EMAIL_USE_TLS', 'Non configuré')
        )
        
        # Demander l'email de test
        test_email = input("\n📧 Entrez votre adresse email pour le test: ").strip()
        
        if not test_email:
            print("❌ Aucune adresse email fournie")
            return False
        
        print(f"📤 Envoi de l'email de test à {test_email}...")
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [test_email],
            fail_silently=False
        )
        
        print("✅ Email de test envoyé avec succès !")
        print("📧 Vérifiez votre boîte de réception (et les spams)")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email de test:")
        print(f"   Type d'erreur: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        
        # Conseils selon le type d'erreur
        if "SMTPAuthenticationError" in str(type(e)):
            print("\n🔧 SOLUTIONS POSSIBLES:")
            print("1. Vérifiez que EMAIL_HOST_USER est correct")
            print("2. Vérifiez que EMAIL_HOST_PASSWORD est le mot de passe d'application Gmail")
            print("3. Assurez-vous que l'authentification à 2 facteurs est activée sur Gmail")
            print("4. Générez un nouveau mot de passe d'application dans les paramètres Google")
        elif "SMTPConnectError" in str(type(e)):
            print("\n🔧 SOLUTIONS POSSIBLES:")
            print("1. Vérifiez votre connexion internet")
            print("2. Vérifiez que EMAIL_HOST et EMAIL_PORT sont corrects")
            print("3. Vérifiez que le pare-feu n'empêche pas la connexion")
        elif "SMTPServerDisconnected" in str(type(e)):
            print("\n🔧 SOLUTIONS POSSIBLES:")
            print("1. Vérifiez la configuration SMTP")
            print("2. Essayez de redémarrer l'application")
        elif "SMTPRecipientsRefused" in str(type(e)):
            print("\n🔧 SOLUTIONS POSSIBLES:")
            print("1. Vérifiez que l'adresse email de destination est valide")
            print("2. Vérifiez que l'adresse email n'est pas bloquée")
        
        return False

def show_configuration_help():
    """Affiche l'aide pour la configuration email"""
    print("\n📚 === GUIDE DE CONFIGURATION EMAIL ===")
    print("Pour configurer l'envoi d'emails avec Gmail:")
    print()
    print("1. 🛡️ Activez l'authentification à 2 facteurs sur votre compte Gmail")
    print("2. 🔑 Générez un mot de passe d'application:")
    print("   - Allez dans les paramètres Google")
    print("   - Sécurité > Authentification à 2 facteurs")
    print("   - Mots de passe d'application > Générer")
    print("3. 📝 Créez un fichier .env à la racine du projet avec:")
    print("   EMAIL_HOST_USER=votre-email@gmail.com")
    print("   EMAIL_HOST_PASSWORD=votre-mot-de-passe-app")
    print("4. 🔄 Redémarrez l'application Django")
    print()
    print("⚠️  IMPORTANT: N'utilisez PAS votre mot de passe Gmail normal!")
    print("   Utilisez UNIQUEMENT le mot de passe d'application généré.")

if __name__ == "__main__":
    print("🚀 Test de configuration email SagaKore")
    print("=" * 50)
    
    # Afficher la configuration actuelle
    test_email_configuration()
    
    # Afficher l'aide
    show_configuration_help() 