#!/usr/bin/env python3
"""
Script de test pour les alertes de sécurité SagaKore
Génère des logs de test pour vérifier le fonctionnement de Papertrail
"""

import os
import sys
import django
import logging
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

# Configuration des loggers
security_logger = logging.getLogger('security')
admin_logger = logging.getLogger('admin_access')
payment_logger = logging.getLogger('payment_security')
suspicious_logger = logging.getLogger('suspicious_activity')

def test_security_logs():
    """Test des différents types de logs de sécurité"""
    
    print("🔒 Test des alertes de sécurité SagaKore")
    print("=" * 50)
    
    # Test 1: Tentative d'accès non autorisé
    print("1. Test: Tentative d'accès non autorisé")
    admin_logger.warning("Tentative d'accès non autorisé depuis l'IP: 192.168.1.100")
    
    # Test 2: Requête suspecte
    print("2. Test: Requête suspecte détectée")
    security_logger.warning("Requête suspecte détectée: /admin/ depuis 10.0.0.50")
    
    # Test 3: Rate limiting
    print("3. Test: Rate limit dépassé")
    security_logger.warning("Rate limit dépassé pour l'IP: 172.16.0.25")
    
    # Test 4: Action sensible
    print("4. Test: Action sensible")
    security_logger.info("Action sensible 'modification_profil_admin' initiée par admin@bolibana.com depuis 192.168.1.100")
    
    # Test 5: Erreur de paiement
    print("5. Test: Erreur de paiement")
    payment_logger.error("Erreur de paiement: Tentative de fraude détectée pour la commande #12345")
    
    # Test 6: Activité suspecte
    print("6. Test: Activité suspecte")
    suspicious_logger.warning("Activité suspecte détectée: Tentative de brute force sur /accounts/login/")
    
    # Test 7: IP non autorisée
    print("7. Test: IP non autorisée")
    admin_logger.warning("IP 203.0.113.0 non autorisée pour l'accès admin")
    
    print("\n✅ Tests terminés !")
    print("📧 Vérifiez votre email pour les alertes Papertrail")
    print("🔍 Consultez l'interface Papertrail pour voir les logs")

if __name__ == "__main__":
    test_security_logs() 