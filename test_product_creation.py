#!/usr/bin/env python
"""
Script pour tester la création du produit HONOR X5b
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from product.models import Product, Phone, Category
from django.utils.text import slugify

def test_product_creation():
    print("🧪 Test de création du produit HONOR X5b")
    print("=" * 50)
    
    # Trouver la catégorie Téléphones
    try:
        phone_category = Category.objects.get(name__icontains='téléphone')
        print(f"✅ Catégorie trouvée: {phone_category.name}")
    except Category.DoesNotExist:
        print("❌ Catégorie Téléphones non trouvée")
        return
    
    # Test 1: Vérifier si le produit existe déjà
    title = "HONOR X5b – 64 Go / 4 Go – Noir Minuit"
    existing_product = Product.objects.filter(title=title).first()
    if existing_product:
        print(f"❌ Produit déjà existant: {existing_product.title}")
        print(f"   Slug: {existing_product.slug}")
        print(f"   ID: {existing_product.id}")
        return
    
    # Test 2: Vérifier le slug
    slug = slugify(title)
    existing_slug = Product.objects.filter(slug=slug).first()
    if existing_slug:
        print(f"❌ Slug déjà existant: {slug}")
        print(f"   Titre existant: {existing_slug.title}")
        return
    
    # Test 3: Vérifier la contrainte unique_together
    existing_similar = Product.objects.filter(
        title=title,
        category=phone_category
    ).first()
    if existing_similar:
        print(f"❌ Produit similaire trouvé dans la même catégorie")
        print(f"   Titre: {existing_similar.title}")
        print(f"   Catégorie: {existing_similar.category.name}")
        return
    
    # Test 4: Vérifier les produits HONOR existants
    honor_products = Product.objects.filter(
        title__icontains='HONOR',
        category=phone_category
    )
    print(f"📱 Produits HONOR existants dans cette catégorie:")
    for product in honor_products:
        print(f"   - {product.title} (slug: {product.slug})")
    
    # Test 5: Essayer de créer le produit
    print(f"\n🔧 Tentative de création du produit...")
    try:
        product = Product.objects.create(
            title=title,
            category=phone_category,
            brand="HONOR",
            price=0,  # Prix temporaire
            stock=0,   # Stock temporaire
        )
        print(f"✅ Produit créé avec succès!")
        print(f"   ID: {product.id}")
        print(f"   Slug: {product.slug}")
        
        # Nettoyer
        product.delete()
        print(f"🧹 Produit supprimé (test)")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        print(f"   Type d'erreur: {type(e).__name__}")

if __name__ == "__main__":
    test_product_creation() 