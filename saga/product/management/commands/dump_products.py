from django.core.management.base import BaseCommand
from django.core import serializers
from product.models import Product, Phone, ImageProduct
import json
from datetime import datetime
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Exporte les données des produits, téléphones et images en JSON'

    def handle(self, *args, **options):
        # Créer le dossier dumps dans l'application product
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        dump_dir = os.path.join(current_dir, 'dumps')
        if not os.path.exists(dump_dir):
            os.makedirs(dump_dir)

        # Générer le nom du fichier avec la date
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{dump_dir}/products_dump_{timestamp}.json'

        # Récupérer les données
        products = Product.objects.all()
        phones = Phone.objects.all()
        images = ImageProduct.objects.all()

        # Préparer les données pour la sérialisation
        data = {
            'products': [],
            'phones': [],
            'images': []
        }

        # Sérialiser les produits
        for product in products:
            product_data = {
                'model': 'product.product',
                'pk': product.pk,
                'fields': {
                    'title': product.title,
                    'slug': product.slug,
                    'description': product.description,
                    'price': str(product.price),
                    'category_id': product.category_id,
                    'supplier_id': product.supplier_id,
                    'brand': product.brand,
                    'is_available': product.is_available,
                    'created_at': product.created_at.isoformat(),
                    'updated_at': product.updated_at.isoformat(),
                    'image_urls': product.image_urls,
                    'sku': product.sku,
                    'stock': product.stock,
                    'specifications': product.specifications,
                    'weight': str(product.weight) if product.weight else None,
                    'dimensions': product.dimensions
                }
            }
            data['products'].append(product_data)

        # Sérialiser les téléphones
        for phone in phones:
            phone_data = {
                'model': 'product.phone',
                'pk': phone.pk,
                'fields': {
                    'product_id': phone.product_id,
                    'brand': phone.brand,
                    'model': phone.model,
                    'operating_system': phone.operating_system,
                    'screen_size': str(phone.screen_size),
                    'resolution': phone.resolution,
                    'processor': phone.processor,
                    'battery_capacity': phone.battery_capacity,
                    'camera_main': phone.camera_main,
                    'camera_front': phone.camera_front,
                    'network': phone.network,
                    'warranty': phone.warranty,
                    'imei': phone.imei,
                    'is_new': phone.is_new,
                    'box_included': phone.box_included,
                    'accessories': phone.accessories,
                    'storage': phone.storage,
                    'ram': phone.ram,
                    'color_id': phone.color_id
                }
            }
            data['phones'].append(phone_data)

        # Sérialiser les images
        for image in images:
            image_data = {
                'model': 'product.imageproduct',
                'pk': image.pk,
                'fields': {
                    'product_id': image.product_id,
                    'image': image.image.name if image.image else None,
                    'ordre': image.ordre,
                    'created_at': image.created_at.isoformat(),
                    'updated_at': image.updated_at.isoformat()
                }
            }
            data['images'].append(image_data)

        # Écrire les données dans le fichier
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.stdout.write(
            self.style.SUCCESS(f'Données exportées avec succès dans {filename}')
        ) 