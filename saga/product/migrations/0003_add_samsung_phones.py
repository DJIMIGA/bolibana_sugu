from django.db import migrations
from django.core.files import File
import os
from django.conf import settings
from product.models import Category, Product, Phone, Color, PhoneVariant, PhoneVariantImage

def add_samsung_phones(apps, schema_editor):
    # Récupérer la catégorie Samsung la plus récente
    samsung_category = Category.objects.filter(name='Samsung').order_by('-id').first()
    if not samsung_category:
        # Si aucune catégorie Samsung n'existe, en créer une
        phone_category = Category.objects.filter(name='Téléphones').order_by('-id').first()
        if phone_category:
            samsung_category = Category.objects.create(
                name='Samsung',
                parent=phone_category
            )
    
    # Couleurs disponibles
    colors = {
        'noir': Color.objects.create(name='Noir', code='#000000'),
        'violet': Color.objects.create(name='Violet', code='#8A2BE2'),
        'bleu': Color.objects.create(name='Bleu', code='#1E90FF')
    }
    
    # Liste des téléphones Samsung
    samsung_phones = [
        {
            'model': 'Galaxy S24 Ultra',
            'operating_system': 'Android 14',
            'screen_size': 6.8,
            'resolution': '3120 x 1440 pixels',
            'processor': 'Snapdragon 8 Gen 3',
            'ram': 12,
            'battery_capacity': 5000,
            'camera_main': '200 MP + 12 MP + 50 MP + 10 MP',
            'camera_front': '12 MP',
            'network': '5G, 4G LTE, 3G, 2G',
            'warranty': '2 ans',
            'variants': [
                {
                    'color': 'noir',
                    'storage': 256,
                    'price': 800000
                },
                {
                    'color': 'noir',
                    'storage': 512,
                    'price': 900000
                },
                {
                    'color': 'violet',
                    'storage': 256,
                    'price': 800000
                },
                {
                    'color': 'violet',
                    'storage': 512,
                    'price': 900000
                }
            ]
        },
        {
            'model': 'Galaxy S24 Plus',
            'operating_system': 'Android 14',
            'screen_size': 6.7,
            'resolution': '3120 x 1440 pixels',
            'processor': 'Snapdragon 8 Gen 3',
            'ram': 12,
            'battery_capacity': 4900,
            'camera_main': '50 MP + 12 MP + 10 MP',
            'camera_front': '12 MP',
            'network': '5G, 4G LTE, 3G, 2G',
            'warranty': '2 ans',
            'variants': [
                {
                    'color': 'noir',
                    'storage': 256,
                    'price': 700000
                },
                {
                    'color': 'noir',
                    'storage': 512,
                    'price': 800000
                },
                {
                    'color': 'bleu',
                    'storage': 256,
                    'price': 700000
                },
                {
                    'color': 'bleu',
                    'storage': 512,
                    'price': 800000
                }
            ]
        }
    ]
    
    for phone_data in samsung_phones:
        # Créer le produit
        product = Product.objects.create(
            title=f"Samsung {phone_data['model']}",
            category=samsung_category,
            price=phone_data['variants'][0]['price'],  # Prix de la première variante
            description=f"Le Samsung {phone_data['model']} est un smartphone haut de gamme avec un écran {phone_data['screen_size']} pouces, un processeur {phone_data['processor']} et une batterie de {phone_data['battery_capacity']} mAh."
        )
        
        # Créer le téléphone
        phone = Phone.objects.create(
            product=product,
            model=phone_data['model'],
            operating_system=phone_data['operating_system'],
            screen_size=phone_data['screen_size'],
            resolution=phone_data['resolution'],
            processor=phone_data['processor'],
            ram=phone_data['ram'],
            battery_capacity=phone_data['battery_capacity'],
            camera_main=phone_data['camera_main'],
            camera_front=phone_data['camera_front'],
            network=phone_data['network'],
            warranty=phone_data['warranty']
        )
        
        # Créer les variantes
        for variant_data in phone_data['variants']:
            variant = PhoneVariant.objects.create(
                phone=phone,
                color=colors[variant_data['color']],
                storage=variant_data['storage'],
                price=variant_data['price'],
                stock=10  # Stock initial
            )

def remove_samsung_phones(apps, schema_editor):
    # Supprimer les téléphones Samsung
    Phone.objects.filter(product__category__name='Samsung').delete()
    # Supprimer les produits Samsung
    Product.objects.filter(category__name='Samsung').delete()
    # Supprimer les couleurs
    Color.objects.filter(name__in=['Noir', 'Violet', 'Bleu']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('product', '0002_clean_duplicates'),
    ]

    operations = [
        migrations.RunPython(add_samsung_phones, remove_samsung_phones),
    ] 