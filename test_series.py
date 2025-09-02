#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from product.context_processors import dropdown_categories_processor
from django.test import RequestFactory

def test_series():
    print("=== Test des séries de téléphones ===")
    
    # Créer une requête factice
    rf = RequestFactory()
    request = rf.get('/')
    
    # Récupérer le contexte
    context = dropdown_categories_processor(request)
    
    # Trouver la catégorie Téléphones
    telephones_cat = None
    for cat in context['dropdown_categories']:
        if cat.slug == 'telephones':
            telephones_cat = cat
            break
    
    if not telephones_cat:
        print("❌ Catégorie Téléphones non trouvée")
        return
    
    print(f"✅ Catégorie Téléphones trouvée: {telephones_cat.name}")
    
    # Récupérer les données des séries
    telephones_hierarchy = context['dropdown_categories_hierarchy']
    series_data = telephones_hierarchy[telephones_cat.id]['subcategories']
    
    print(f"\n📱 Séries de téléphones trouvées ({len(series_data)} séries):")
    
    for series in series_data:
        series_name = series['subcategory'].name
        total_models = series['total_models']
        is_series = series.get('is_series', False)
        
        print(f"\n🔹 {series_name} ({total_models} modèles) {'[SÉRIE]' if is_series else '[MARQUE]'}")
        
        # Afficher les premiers modèles
        models = series['subsubcategories']
        for i, model in enumerate(models[:3]):
            print(f"   • {model.name} ({model.product_count} produits)")
        
        if len(models) > 3:
            print(f"   ... et {len(models) - 3} autres modèles")

if __name__ == '__main__':
    test_series() 