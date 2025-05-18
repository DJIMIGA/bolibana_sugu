from django.core.management.base import BaseCommand
from django.core import serializers
from product.models import Product, Phone, ImageProduct
import json
from datetime import datetime
import os
import requests
from django.conf import settings

class Command(BaseCommand):
    help = 'Déploie les données des produits sur Heroku'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force le déploiement même si des données existent déjà',
        )
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Crée une sauvegarde des données existantes avant le déploiement',
        )

    def handle(self, *args, **options):
        # Vérifier si nous sommes sur Heroku
        if not settings.DEBUG:
            self.stdout.write(self.style.WARNING('Vérification de l\'environnement Heroku...'))
            
            # Vérifier si des données existent déjà
            existing_products = Product.objects.count()
            existing_phones = Phone.objects.count()
            
            if existing_products > 0 or existing_phones > 0:
                if not options['force']:
                    self.stdout.write(self.style.ERROR(
                        f'Des données existent déjà ({existing_products} produits, {existing_phones} téléphones). '
                        'Utilisez --force pour forcer le déploiement ou --backup pour créer une sauvegarde.'
                    ))
                    return
                
                if options['backup']:
                    # Créer une sauvegarde
                    self.create_backup()
            
            # Procéder au déploiement
            self.deploy_data()
        else:
            self.stdout.write(self.style.ERROR('Cette commande doit être exécutée sur Heroku'))

    def create_backup(self):
        """Crée une sauvegarde des données existantes"""
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        backup_dir = os.path.join(current_dir, 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{backup_dir}/heroku_backup_{timestamp}.json'

        data = {
            'products': [],
            'phones': [],
            'images': []
        }

        # Sauvegarder les produits
        for product in Product.objects.all():
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

        # Sauvegarder les téléphones
        for phone in Phone.objects.all():
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

        # Sauvegarder les images
        for image in ImageProduct.objects.all():
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

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.stdout.write(
            self.style.SUCCESS(f'Sauvegarde créée avec succès dans {filename}')
        )

    def deploy_data(self):
        """Déploie les données sur Heroku"""
        try:
            # Vérifier si le fichier de dump existe
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            dump_dir = os.path.join(current_dir, 'dumps')
            if not os.path.exists(dump_dir):
                self.stdout.write(self.style.ERROR('Aucun fichier de dump trouvé. Exécutez d\'abord dump_products.'))
                return

            # Trouver le dernier fichier de dump
            dump_files = [f for f in os.listdir(dump_dir) if f.startswith('products_dump_')]
            if not dump_files:
                self.stdout.write(self.style.ERROR('Aucun fichier de dump trouvé.'))
                return

            latest_dump = sorted(dump_files)[-1]
            dump_path = os.path.join(dump_dir, latest_dump)

            # Lire les données du dump
            with open(dump_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Déployer les données
            self.stdout.write(self.style.SUCCESS('Déploiement des données en cours...'))

            # Déployer les produits
            for product_data in data['products']:
                Product.objects.update_or_create(
                    pk=product_data['pk'],
                    defaults=product_data['fields']
                )

            # Déployer les téléphones
            for phone_data in data['phones']:
                Phone.objects.update_or_create(
                    pk=phone_data['pk'],
                    defaults=phone_data['fields']
                )

            # Déployer les images
            for image_data in data['images']:
                ImageProduct.objects.update_or_create(
                    pk=image_data['pk'],
                    defaults=image_data['fields']
                )

            self.stdout.write(
                self.style.SUCCESS('Déploiement terminé avec succès!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors du déploiement: {str(e)}')
            ) 