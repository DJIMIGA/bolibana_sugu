#!/usr/bin/env python
"""
Script pour exécuter tous les tests des commandes mixtes
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

def run_tests():
    """Exécute tous les tests des commandes mixtes"""
    
    # Configuration Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
    django.setup()
    
    # Obtenir le runner de tests
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Tests à exécuter
    test_modules = [
        'cart.tests.test_mixed_orders',
        'cart.tests.test_mixed_orders_functional',
        'cart.tests.test_mixed_orders_models',
    ]
    
    print("🚀 Démarrage des tests des commandes mixtes...")
    print("=" * 50)
    
    # Exécuter les tests
    failures = test_runner.run_tests(test_modules)
    
    print("=" * 50)
    if failures:
        print(f"❌ {failures} test(s) ont échoué")
        return 1
    else:
        print("✅ Tous les tests ont réussi !")
        return 0

if __name__ == '__main__':
    sys.exit(run_tests()) 