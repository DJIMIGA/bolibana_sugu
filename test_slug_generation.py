#!/usr/bin/env python
"""
Script pour tester la génération des slugs
"""
from django.utils.text import slugify

def test_slug_generation():
    print("🧪 Test de génération des slugs")
    print("=" * 50)
    
    # Les titres en question
    title1 = "HONOR X5 Plus 64 Go / 4 Go Noir minuit"
    title2 = "HONOR X5b – 64 Go / 4 Go – Noir Minuit"
    
    # Génération des slugs
    slug1 = slugify(title1)
    slug2 = slugify(title2)
    
    print(f"📝 Titre 1: '{title1}'")
    print(f"🔗 Slug 1: '{slug1}'")
    print()
    print(f"📝 Titre 2: '{title2}'")
    print(f"🔗 Slug 2: '{slug2}'")
    print()
    
    # Comparaison
    print("🔍 Comparaison:")
    print(f"   Longueur slug 1: {len(slug1)} caractères")
    print(f"   Longueur slug 2: {len(slug2)} caractères")
    print(f"   Identiques: {slug1 == slug2}")
    
    # Analyse caractère par caractère
    print("\n📊 Analyse caractère par caractère:")
    min_len = min(len(slug1), len(slug2))
    differences = []
    
    for i in range(min_len):
        if slug1[i] != slug2[i]:
            differences.append(f"Position {i}: '{slug1[i]}' vs '{slug2[i]}'")
    
    if differences:
        print("   Différences trouvées:")
        for diff in differences:
            print(f"   - {diff}")
    else:
        print("   Aucune différence dans la partie commune")
    
    # Test avec des variations
    print("\n🧪 Test avec des variations:")
    variations = [
        "HONOR X5 Plus 64 Go / 4 Go Noir minuit",
        "HONOR X5b – 64 Go / 4 Go – Noir Minuit", 
        "HONOR X5b 64 Go 4 Go Noir Minuit",
        "honor x5b 64 go 4 go noir minuit",
        "HONOR-X5b-64-Go-4-Go-Noir-Minuit"
    ]
    
    for i, title in enumerate(variations, 1):
        slug = slugify(title)
        print(f"   {i}. '{title}' → '{slug}'")

if __name__ == "__main__":
    test_slug_generation() 