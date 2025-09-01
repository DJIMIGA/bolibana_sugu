#!/usr/bin/env python3
"""
Script pour mettre tous les produits is_available=False dans la base de données SagaKore

Ce script peut être exécuté directement ou importé dans un autre script.
"""

import os
import sys
import django
from pathlib import Path

# Ajouter le répertoire racine du projet au chemin Python
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from django.db import transaction
from product.models import Product


def get_product_statistics():
    """Retourne les statistiques actuelles des produits"""
    total = Product.objects.count()
    available = Product.objects.filter(is_available=True).count()
    unavailable = Product.objects.filter(is_available=False).count()
    
    return {
        'total': total,
        'available': available,
        'unavailable': unavailable
    }


def set_all_products_unavailable(dry_run=False, confirm=False):
    """
    Met tous les produits is_available=False
    
    Args:
        dry_run (bool): Si True, affiche seulement ce qui serait fait
        confirm (bool): Si True, exécute sans demander de confirmation
    
    Returns:
        bool: True si l'opération a réussi, False sinon
    """
    
    # Obtenir les statistiques
    stats = get_product_statistics()
    
    print("📊 Statistiques actuelles des produits:")
    print(f"   • Total des produits: {stats['total']}")
    print(f"   • Produits disponibles: {stats['available']}")
    print(f"   • Produits non disponibles: {stats['unavailable']}")
    print()
    
    if dry_run:
        print("🔍 MODE DRY-RUN - Aucune modification ne sera effectuée")
        print(f"   • {stats['available']} produits seraient mis is_available=False")
        print(f"   • {stats['unavailable']} produits resteraient is_available=False")
        return True
    
    if not confirm:
        print("⚠️  ATTENTION: Cette action va mettre TOUS les produits is_available=False!")
        print()
        print("Pour confirmer, appelez la fonction avec confirm=True")
        print("Exemple: set_all_products_unavailable(confirm=True)")
        return False
    
    # Confirmation finale
    print("🚨 CONFIRMATION FINALE:")
    print(f"   • {stats['available']} produits vont être mis is_available=False")
    print("   • Cette action est IRREVERSIBLE!")
    print()
    
    if not confirm:
        user_input = input('Tapez "CONFIRM" pour continuer: ')
        if user_input != 'CONFIRM':
            print("❌ Opération annulée par l'utilisateur")
            return False
    
    try:
        with transaction.atomic():
            # Mettre à jour tous les produits
            updated_count = Product.objects.filter(
                is_available=True
            ).update(is_available=False)
            
            print()
            print(f"✅ SUCCÈS: {updated_count} produits ont été mis is_available=False")
            
            # Vérifier le résultat
            new_stats = get_product_statistics()
            
            print()
            print("📊 Nouvelles statistiques:")
            print(f"   • Produits disponibles: {new_stats['available']}")
            print(f"   • Produits non disponibles: {new_stats['unavailable']}")
            
            return True
            
    except Exception as e:
        print()
        print(f"❌ ERREUR lors de la mise à jour: {str(e)}")
        return False


def main():
    """Fonction principale pour l'exécution en ligne de commande"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Met tous les produits is_available=False dans la base de données'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Affiche ce qui serait fait sans effectuer les modifications'
    )
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Exécute sans demander de confirmation'
    )
    
    args = parser.parse_args()
    
    success = set_all_products_unavailable(
        dry_run=args.dry_run,
        confirm=args.confirm
    )
    
    if success:
        print()
        print("🎉 Opération terminée avec succès!")
        sys.exit(0)
    else:
        print()
        print("❌ Opération échouée ou annulée")
        sys.exit(1)


if __name__ == '__main__':
    main()
