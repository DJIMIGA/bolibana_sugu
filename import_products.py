import os
import django
import json

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
django.setup()

from product.models import Category, Product, Phone, PhoneVariant, Color

def import_products():
    # Charger les données depuis le fichier JSON
    with open('products.json', 'r') as f:
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
                    'supplier_id': item['fields']['supplier'],
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

if __name__ == '__main__':
    print("Début de l'importation des données...")
    import_products()
    print("Importation terminée avec succès!") 