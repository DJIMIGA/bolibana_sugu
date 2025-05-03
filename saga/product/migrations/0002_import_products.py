from django.db import migrations
import json
import os

def import_products(apps, schema_editor):
    Category = apps.get_model('product', 'Category')
    Product = apps.get_model('product', 'Product')
    Phone = apps.get_model('product', 'Phone')
    PhoneVariant = apps.get_model('product', 'PhoneVariant')
    Color = apps.get_model('product', 'Color')
    Supplier = apps.get_model('suppliers', 'Supplier')

    # Récupérer le fournisseur Tecno
    try:
        supplier = Supplier.objects.get(name='Tecno')
    except Supplier.DoesNotExist:
        # Si Tecno n'existe pas, le créer
        supplier = Supplier.objects.create(
            name='Tecno',
            email='contact@tecno.com',
            phone='+223 20 22 23 24',
            address='Siège social : Shenzhen, Chine',
            description='''TECNO est une marque de smartphones haut de gamme qui se concentre sur l'innovation technologique et le design.
            La marque propose des appareils avec des fonctionnalités avancées, des performances exceptionnelles et des designs élégants.''',
            specialty='Fournisseur de TELEPHONE'
        )

    # Chemin vers le fichier products.json
    file_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'products.json')
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Importer les catégories
    for item in data:
        if item['model'] == 'product.category':
            Category.objects.get_or_create(
                id=item['pk'],
                defaults={
                    'name': item['fields']['name'],
                    'slug': item['fields']['slug'],
                    'parent_id': item['fields']['parent']
                }
            )
    
    # Importer les couleurs
    for item in data:
        if item['model'] == 'product.color':
            Color.objects.get_or_create(
                id=item['pk'],
                defaults={
                    'name': item['fields']['name'],
                    'code': item['fields']['code']
                }
            )
    
    # Importer les produits
    for item in data:
        if item['model'] == 'product.product':
            Product.objects.get_or_create(
                id=item['pk'],
                defaults={
                    'title': item['fields']['title'],
                    'category_id': item['fields']['category'],
                    'price': item['fields']['price'],
                    'description': item['fields']['description'],
                    'highlight': item['fields']['highlight'],
                    'supplier_id': supplier.id,
                    'is_active': item['fields']['is_active']
                }
            )
    
    # Importer les téléphones
    for item in data:
        if item['model'] == 'product.phone':
            Phone.objects.get_or_create(
                id=item['pk'],
                defaults={
                    'product_id': item['fields']['product'],
                    'model': item['fields']['model'],
                    'brand': item['fields']['brand'],
                    'operating_system': item['fields']['operating_system'],
                    'screen_size': item['fields']['screen_size'],
                    'resolution': item['fields']['resolution'],
                    'processor': item['fields']['processor'],
                    'battery_capacity': item['fields']['battery_capacity'],
                    'camera_main': item['fields']['camera_main'],
                    'camera_front': item['fields']['camera_front'],
                    'network': item['fields']['network'],
                    'warranty': item['fields']['warranty'],
                    'imei': item['fields']['imei'],
                    'is_new': item['fields']['is_new'],
                    'box_included': item['fields']['box_included'],
                    'accessories': item['fields']['accessories']
                }
            )
    
    # Importer les variantes de téléphones
    for item in data:
        if item['model'] == 'product.phonevariant':
            PhoneVariant.objects.get_or_create(
                id=item['pk'],
                defaults={
                    'phone_id': item['fields']['phone'],
                    'color_id': item['fields']['color'],
                    'storage': item['fields']['storage'],
                    'ram': item['fields']['ram'],
                    'price': item['fields']['price'],
                    'stock': item['fields']['stock'],
                    'sku': item['fields']['sku'],
                    'disponible_salam': item['fields']['disponible_salam']
                }
            )

class Migration(migrations.Migration):
    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(import_products),
    ] 