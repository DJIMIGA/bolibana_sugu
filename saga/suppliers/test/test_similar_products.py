#!/usr/bin/env python
"""
Script de test pour vérifier le système de priorité des produits similaires
Usage: python test_similar_products.py <product_id>
"""

import os
import sys
import django

# Ajouter le répertoire parent au path Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db.models import Q
from product.models import Product, Category


def test_similar_products(product_id):
    """Test du système de priorité des produits similaires"""
    try:
        product = Product.objects.get(id=product_id)
        print(f"Produit testé: {product.title} (ID: {product.id})")
        print(f"Catégorie: {product.category.name} (ID: {product.category.id})")
        
        # Récupérer toutes les catégories liées
        category_ids = [product.category.id]
        
        # Ajouter les sous-catégories directes
        direct_children = product.category.children.all()
        category_ids.extend(direct_children.values_list('id', flat=True))
        
        # Ajouter les sous-sous-catégories
        for child in direct_children:
            grand_children = child.children.all()
            category_ids.extend(grand_children.values_list('id', flat=True))
        
        print(f"\nCatégories liées: {category_ids}")
        print(f"Sous-catégories directes: {list(direct_children.values_list('id', flat=True))}")
        
        # Construire les conditions de base selon le type de produit
        if hasattr(product, 'clothing_product'):
            print("\n=== PRODUIT VÊTEMENT ===")
            similar_conditions = Q(clothing_product__isnull=False)
            
            # Ajouter les conditions de caractéristiques
            characteristic_conditions = Q()
            clothing = product.clothing_product
            if clothing.material:
                characteristic_conditions |= Q(clothing_product__material=clothing.material)
            if clothing.style:
                characteristic_conditions |= Q(clothing_product__style=clothing.style)
            if clothing.gender:
                characteristic_conditions |= Q(clothing_product__gender=clothing.gender)
            
            print(f"Caractéristiques: material={clothing.material}, style={clothing.style}, gender={clothing.gender}")
            
        elif hasattr(product, 'fabric_product'):
            print("\n=== PRODUIT TISSU ===")
            similar_conditions = Q(fabric_product__isnull=False)
            
            # Ajouter les conditions de caractéristiques
            characteristic_conditions = Q()
            fabric = product.fabric_product
            if fabric.fabric_type:
                characteristic_conditions |= Q(fabric_product__fabric_type=fabric.fabric_type)
            if fabric.quality:
                characteristic_conditions |= Q(fabric_product__quality=fabric.quality)
            
            print(f"Caractéristiques: fabric_type={fabric.fabric_type}, quality={fabric.quality}")
            
        elif hasattr(product, 'phone'):
            print("\n=== PRODUIT TÉLÉPHONE ===")
            similar_conditions = Q(phone__isnull=False)
            
            # Ajouter les conditions de caractéristiques
            characteristic_conditions = Q()
            phone = product.phone
            if phone.brand:
                characteristic_conditions |= Q(phone__brand=phone.brand)
            if phone.model:
                characteristic_conditions |= Q(phone__model=phone.model)
            if phone.storage:
                characteristic_conditions |= Q(phone__storage=phone.storage)
            if phone.ram:
                characteristic_conditions |= Q(phone__ram=phone.ram)
            
            print(f"Caractéristiques: brand={phone.brand}, model={phone.model}, storage={phone.storage}, ram={phone.ram}")
            
        elif hasattr(product, 'cultural_product'):
            print("\n=== PRODUIT CULTUREL ===")
            similar_conditions = Q(cultural_product__isnull=False)
            
            # Ajouter les conditions de caractéristiques
            characteristic_conditions = Q()
            cultural = product.cultural_product
            if cultural.author:
                characteristic_conditions |= Q(cultural_product__author=cultural.author)
            
            print(f"Caractéristiques: author={cultural.author}")
            
        else:
            print("\n=== PRODUIT GÉNÉRIQUE ===")
            similar_conditions = Q()
            characteristic_conditions = Q()
        
        # Construire la requête avec priorité
        # Priorité 1: Même catégorie exacte + caractéristiques similaires
        priority_1 = Q(category=product.category)
        if characteristic_conditions:
            priority_1 &= characteristic_conditions
        
        # Priorité 2: Même catégorie exacte
        priority_2 = Q(category=product.category)
        
        # Priorité 3: Sous-catégories + caractéristiques similaires
        priority_3 = Q(category__in=direct_children)
        if characteristic_conditions:
            priority_3 &= characteristic_conditions
        
        # Priorité 4: Sous-catégories
        priority_4 = Q(category__in=direct_children)
        
        # Priorité 5: Sous-sous-catégories + caractéristiques similaires
        grand_children_ids = []
        for child in direct_children:
            grand_children_ids.extend(child.children.values_list('id', flat=True))
        priority_5 = Q(category__id__in=grand_children_ids)
        if characteristic_conditions:
            priority_5 &= characteristic_conditions
        
        # Priorité 6: Sous-sous-catégories
        priority_6 = Q(category__id__in=grand_children_ids)
        
        # Combiner toutes les priorités
        similar_conditions = (
            priority_1 | priority_2 | priority_3 | priority_4 | priority_5 | priority_6
        )
        
        # Récupérer les produits similaires
        similar_products = Product.objects.filter(
            similar_conditions,
            is_available=True
        ).exclude(
            id=product.id
        ).order_by(
            'category__id',
            '-created_at'
        )[:10]
        
        print(f"\nProduits similaires trouvés: {similar_products.count()}")
        
        # Afficher les résultats par priorité
        for i, similar in enumerate(similar_products, 1):
            priority = "Inconnue"
            if similar.category == product.category:
                if characteristic_conditions and any([
                    hasattr(similar, 'clothing_product') and similar.clothing_product and (
                        (hasattr(product, 'clothing_product') and product.clothing_product and 
                         similar.clothing_product.material == product.clothing_product.material) or
                        (hasattr(product, 'clothing_product') and product.clothing_product and 
                         similar.clothing_product.style == product.clothing_product.style) or
                        (hasattr(product, 'clothing_product') and product.clothing_product and 
                         similar.clothing_product.gender == product.clothing_product.gender)
                    )
                ]):
                    priority = "Priorité 1: Même catégorie + caractéristiques"
                else:
                    priority = "Priorité 2: Même catégorie"
            elif similar.category in direct_children:
                if characteristic_conditions:
                    priority = "Priorité 3: Sous-catégorie + caractéristiques"
                else:
                    priority = "Priorité 4: Sous-catégorie"
            elif similar.category.id in grand_children_ids:
                if characteristic_conditions:
                    priority = "Priorité 5: Sous-sous-catégorie + caractéristiques"
                else:
                    priority = "Priorité 6: Sous-sous-catégorie"
            
            print(f"{i}. {similar.title} (ID: {similar.id}) - {similar.category.name} - {priority}")
        
    except Product.DoesNotExist:
        print(f'Erreur: Produit avec ID {product_id} non trouvé')
    except Exception as e:
        print(f'Erreur: {e}')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_similar_products.py <product_id>")
        sys.exit(1)
    
    try:
        product_id = int(sys.argv[1])
        test_similar_products(product_id)
    except ValueError:
        print("Erreur: L'ID du produit doit être un nombre entier")
        sys.exit(1) 