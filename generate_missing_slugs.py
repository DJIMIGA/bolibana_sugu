#!/usr/bin/env python3
"""
Script pour générer automatiquement les slugs manquants
pour tous les produits existants dans la base de données.
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from saga.product.models import Product
from django.utils.text import slugify

def generate_missing_slugs():
    """Génère les slugs manquants pour tous les produits"""
    print("🚀 Génération des slugs manquants pour les produits...\n")
    
    # Récupérer tous les produits sans slug
    products_without_slug = Product.objects.filter(slug__isnull=True).exclude(slug='')
    products_with_empty_slug = Product.objects.filter(slug='')
    
    total_products_to_fix = products_without_slug.count() + products_with_empty_slug.count()
    
    if total_products_to_fix == 0:
        print("✅ Tous les produits ont déjà un slug valide !")
        return
    
    print(f"📊 Produits à traiter : {total_products_to_fix}")
    print(f"   - Produits sans slug : {products_without_slug.count()}")
    print(f"   - Produits avec slug vide : {products_with_empty_slug.count()}")
    print()
    
    # Traiter les produits sans slug
    fixed_count = 0
    for product in products_without_slug:
        try:
            old_slug = product.slug
            product.slug = product.generate_unique_slug()
            product.save(update_fields=['slug'])
            print(f"✅ Produit '{product.title}' : slug généré '{product.slug}'")
            fixed_count += 1
        except Exception as e:
            print(f"❌ Erreur pour '{product.title}' : {e}")
    
    # Traiter les produits avec slug vide
    for product in products_with_empty_slug:
        try:
            old_slug = product.slug
            product.slug = product.generate_unique_slug()
            product.save(update_fields=['slug'])
            print(f"✅ Produit '{product.title}' : slug généré '{product.slug}'")
            fixed_count += 1
        except Exception as e:
            print(f"❌ Erreur pour '{product.title}' : {e}")
    
    print(f"\n🎉 Génération terminée ! {fixed_count} produits traités.")
    
    # Vérification finale
    remaining_products = Product.objects.filter(slug__isnull=True).exclude(slug='').count()
    if remaining_products == 0:
        print("✅ Tous les produits ont maintenant un slug valide !")
    else:
        print(f"⚠️  {remaining_products} produits n'ont toujours pas de slug.")

def verify_all_slugs():
    """Vérifie que tous les produits ont un slug valide"""
    print("\n🔍 Vérification des slugs...")
    
    total_products = Product.objects.count()
    products_with_slug = Product.objects.exclude(slug__isnull=True).exclude(slug='').count()
    products_without_slug = total_products - products_with_slug
    
    print(f"📊 Total des produits : {total_products}")
    print(f"✅ Produits avec slug : {products_with_slug}")
    print(f"❌ Produits sans slug : {products_without_slug}")
    
    if products_without_slug == 0:
        print("🎉 Tous les produits ont un slug valide !")
    else:
        print(f"⚠️  {products_without_slug} produits n'ont pas de slug.")
        
        # Afficher quelques exemples de produits sans slug
        products_to_show = Product.objects.filter(slug__isnull=True).exclude(slug='')[:5]
        print("\nExemples de produits sans slug :")
        for product in products_to_show:
            print(f"   - {product.title} (ID: {product.id})")

def show_slug_examples():
    """Affiche quelques exemples de slugs générés"""
    print("\n📝 Exemples de slugs générés :")
    
    products_with_slugs = Product.objects.exclude(slug__isnull=True).exclude(slug='')[:10]
    
    for product in products_with_slugs:
        print(f"   - '{product.title}' → '{product.slug}'")

if __name__ == "__main__":
    print("🔧 Outil de génération des slugs manquants pour SagaKore\n")
    
    try:
        # Vérification initiale
        verify_all_slugs()
        
        # Génération des slugs manquants
        generate_missing_slugs()
        
        # Vérification finale
        verify_all_slugs()
        
        # Exemples de slugs
        show_slug_examples()
        
        print("\n🎯 Prochaines étapes :")
        print("1. Tester la page d'accueil")
        print("2. Vérifier que les produits pilotes s'affichent")
        print("3. Tester la navigation vers les détails des produits")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution : {e}")
        import traceback
        traceback.print_exc()
