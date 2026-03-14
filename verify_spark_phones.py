#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from product.models import Phone, Product, Color
from suppliers.models import Supplier

def verify_spark_phones():
    print("=" * 60)
    print("VERIFICATION DES TELEPHONES TECNO SPARK")
    print("=" * 60)
    
    # Vérifier le fournisseur TECNO
    try:
        tecno_supplier = Supplier.objects.get(company_name="TECNO")
        print(f"✅ Fournisseur TECNO trouvé: {tecno_supplier.company_name}")
    except Supplier.DoesNotExist:
        print("❌ Fournisseur TECNO non trouvé")
        return
    
    # Compter les téléphones TECNO
    tecno_phones = Phone.objects.filter(brand="TECNO")
    total_tecno = tecno_phones.count()
    print(f"📱 Total téléphones TECNO: {total_tecno}")
    
    # Compter les téléphones SPARK
    spark_phones = Phone.objects.filter(brand="TECNO", product__title__icontains="SPARK")
    total_spark = spark_phones.count()
    print(f"📱 Total téléphones SPARK: {total_spark}")
    
    # Lister les modèles SPARK uniques
    spark_models = spark_phones.values_list('product__title', flat=True).distinct()
    print(f"\n🏷️ Modèles SPARK créés ({len(spark_models)} modèles):")
    for model in sorted(spark_models):
        count = spark_phones.filter(product__title=model).count()
        print(f"  ✅ {model} ({count} variantes)")
    
    # Vérifier les couleurs utilisées
    spark_colors = Color.objects.filter(phone__in=spark_phones).distinct()
    print(f"\n🎨 Couleurs utilisées ({spark_colors.count()} couleurs):")
    for color in sorted(spark_colors, key=lambda x: x.name):
        count = spark_phones.filter(color=color).count()
        print(f"  🎨 {color.name} ({count} téléphones)")
    
    # Vérifier les variantes de stockage et RAM
    print(f"\n💾 Variantes de stockage et RAM:")
    storage_ram_variants = spark_phones.values_list('storage', 'ram').distinct()
    for storage, ram in sorted(storage_ram_variants):
        count = spark_phones.filter(storage=storage, ram=ram).count()
        print(f"  💾 {storage}GB/{ram}GB ({count} téléphones)")
    
    print("\n" + "=" * 60)
    print("VERIFICATION TERMINEE")
    print("=" * 60)

if __name__ == "__main__":
    verify_spark_phones() 