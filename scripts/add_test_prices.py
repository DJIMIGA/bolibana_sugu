#!/usr/bin/env python
"""
Script pour ajouter des prix de test au comparateur de prix
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random

# Ajouter le dossier racine du projet au sys.path
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from price_checker.models import PriceSubmission, PriceEntry
from product.models import Product

def create_test_prices():
    """Créer des prix de test pour différents produits"""
    
    # Récupérer quelques produits existants
    products = Product.objects.all()[:10]  # Prendre les 10 premiers produits
    
    if not products.exists():
        print("❌ Aucun produit trouvé dans la base de données")
        return
    
    # Fournisseurs de test
    suppliers = [
        {
            'name': 'ElectroPlus',
            'phone': '+223 20 12 34 56',
            'address': 'Hamdallaye ACI 2000, Bamako'
        },
        {
            'name': 'TechMall',
            'phone': '+223 20 98 76 54',
            'address': 'Badalabougou, Bamako'
        },
        {
            'name': 'DigitalStore',
            'phone': '+223 20 45 67 89',
            'address': 'Faladié, Bamako'
        },
        {
            'name': 'SmartElectronics',
            'phone': '+223 20 11 22 33',
            'address': 'Sikasso, Mali'
        },
        {
            'name': 'GadgetWorld',
            'phone': '+223 20 44 55 66',
            'address': 'Ségou, Mali'
        }
    ]
    
    # Prix de base pour différents types de produits
    base_prices = {
        'phone': {'min': 50000, 'max': 150000},
        'laptop': {'min': 200000, 'max': 500000},
        'tablet': {'min': 80000, 'max': 200000},
        'accessory': {'min': 5000, 'max': 25000}
    }
    
    created_count = 0
    
    for product in products:
        # Créer 2-4 soumissions par produit
        num_submissions = random.randint(2, 4)
        
        for i in range(num_submissions):
            # Choisir un fournisseur aléatoire
            supplier = random.choice(suppliers)
            
            # Déterminer le type de produit pour le prix
            product_type = 'accessory'  # par défaut
            if 'phone' in product.name.lower() or 'téléphone' in product.name.lower():
                product_type = 'phone'
            elif 'laptop' in product.name.lower() or 'ordinateur' in product.name.lower():
                product_type = 'laptop'
            elif 'tablet' in product.name.lower():
                product_type = 'tablet'
            
            # Générer un prix aléatoire
            price_range = base_prices[product_type]
            price = random.randint(price_range['min'], price_range['max'])
            
            # Créer la soumission
            submission = PriceSubmission.objects.create(
                product=product,
                supplier_name=supplier['name'],
                supplier_phone=supplier['phone'],
                supplier_address=supplier['address'],
                submission_date=datetime.now() - timedelta(days=random.randint(0, 30)),
                is_verified=random.choice([True, True, True, False]),  # 75% vérifiés
                notes=f"Prix soumis par {supplier['name']} - {random.choice(['Prix compétitif', 'Promotion en cours', 'Prix normal', 'Remise disponible'])}"
            )
            
            # Créer l'entrée de prix
            PriceEntry.objects.create(
                submission=submission,
                price=Decimal(price),
                currency='XOF',
                is_available=random.choice([True, True, True, False]),  # 75% disponibles
                notes=f"Prix {price:,} FCFA - {random.choice(['En stock', 'Livraison rapide', 'Garantie incluse', 'Service après-vente'])}"
            )
            
            created_count += 1
            print(f"✅ Prix ajouté: {product.name} - {supplier['name']} - {price:,} FCFA")
    
    print(f"\n🎉 {created_count} prix de test ont été créés avec succès!")
    print(f"📊 Répartition:")
    print(f"   - Produits: {products.count()}")
    print(f"   - Fournisseurs: {len(suppliers)}")
    print(f"   - Prix créés: {created_count}")

def show_statistics():
    """Afficher les statistiques des prix"""
    total_submissions = PriceSubmission.objects.count()
    verified_submissions = PriceSubmission.objects.filter(is_verified=True).count()
    total_entries = PriceEntry.objects.count()
    available_entries = PriceEntry.objects.filter(is_available=True).count()
    
    print(f"\n📈 Statistiques actuelles:")
    print(f"   - Total soumissions: {total_submissions}")
    print(f"   - Soumissions vérifiées: {verified_submissions} ({verified_submissions/total_submissions*100:.1f}%)")
    print(f"   - Total entrées de prix: {total_entries}")
    print(f"   - Prix disponibles: {available_entries} ({available_entries/total_entries*100:.1f}%)")
    
    # Top 5 des fournisseurs
    from django.db.models import Count
    top_suppliers = PriceSubmission.objects.values('supplier_name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    print(f"\n🏆 Top 5 des fournisseurs:")
    for i, supplier in enumerate(top_suppliers, 1):
        print(f"   {i}. {supplier['supplier_name']}: {supplier['count']} prix")

if __name__ == '__main__':
    print("🚀 Ajout de prix de test au comparateur de prix")
    print("=" * 50)
    
    # Afficher les statistiques avant
    show_statistics()
    
    # Demander confirmation
    response = input("\n❓ Voulez-vous ajouter des prix de test? (o/n): ")
    if response.lower() in ['o', 'oui', 'y', 'yes']:
        create_test_prices()
        print("\n" + "=" * 50)
        show_statistics()
    else:
        print("❌ Opération annulée") 