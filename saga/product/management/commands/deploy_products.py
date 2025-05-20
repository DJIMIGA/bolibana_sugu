from django.core.management.base import BaseCommand
from django.core import serializers
from product.models import Product, Phone, ImageProduct
import json
from datetime import datetime
import os
import requests
from django.conf import settings
import glob

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
        if not os.environ.get('DYNO'):
            self.stdout.write(self.style.ERROR('Cette commande doit être exécutée sur Heroku'))
            return

        # Vérifier si des données existent déjà
        product_count = Product.objects.count()
        phone_count = Phone.objects.count()
        
        if product_count > 0 or phone_count > 0:
            if not options['force'] and not options['backup']:
                self.stdout.write(self.style.WARNING(
                    f'Des données existent déjà ({product_count} produits, {phone_count} téléphones). '
                    'Utilisez --force pour forcer le déploiement ou --backup pour créer une sauvegarde.'
                ))
                return
            else:
                self.stdout.write(self.style.WARNING(
                    f'Des données existent déjà ({product_count} produits, {phone_count} téléphones). '
                    'Les données seront mises à jour.'
                ))

        # Créer une sauvegarde si demandé
        if options['backup']:
            self.create_backup()

        self.stdout.write('Déploiement des données en cours...')

        # Compteurs pour le rapport
        products_created = 0
        products_updated = 0
        phones_created = 0
        phones_updated = 0
        images_created = 0
        images_updated = 0

        try:
            # Trouver le fichier JSON le plus récent
            dumps_dir = os.path.join(settings.BASE_DIR, 'product', 'dumps')
            json_files = glob.glob(os.path.join(dumps_dir, 'products_dump_*.json'))
            
            if not json_files:
                self.stdout.write(self.style.ERROR('Aucun fichier de dump trouvé dans le dossier dumps'))
                return
                
            latest_json = max(json_files, key=os.path.getctime)
            self.stdout.write(f'Utilisation du fichier : {latest_json}')
            
            # Lire le fichier JSON
            with open(latest_json, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Traiter les produits
            for product_data in data['products']:
                product, created = Product.objects.update_or_create(
                    id=product_data['id'],
                    defaults={
                        'name': product_data['name'],
                        'description': product_data['description'],
                        'price': product_data['price'],
                        'image': product_data.get('image', ''),
                        'image_urls': product_data.get('image_urls', []),
                        'created_at': product_data['created_at'],
                        'updated_at': product_data['updated_at']
                    }
                )
                if created:
                    products_created += 1
                else:
                    products_updated += 1

            # Traiter les téléphones
            for phone_data in data['phones']:
                phone, created = Phone.objects.update_or_create(
                    id=phone_data['id'],
                    defaults={
                        'product_id': phone_data['product'],
                        'brand': phone_data['brand'],
                        'model': phone_data['model'],
                        'color': phone_data['color'],
                        'storage': phone_data['storage'],
                        'condition': phone_data['condition'],
                        'created_at': phone_data['created_at'],
                        'updated_at': phone_data['updated_at']
                    }
                )
                if created:
                    phones_created += 1
                else:
                    phones_updated += 1

            # Traiter les images
            for image_data in data['images']:
                try:
                    image, created = ImageProduct.objects.update_or_create(
                        id=image_data['id'],
                        defaults={
                            'product_id': image_data['product'],
                            'image': image_data['image'],
                            'is_primary': image_data['is_primary'],
                            'created_at': image_data['created_at'],
                            'updated_at': image_data['updated_at']
                        }
                    )
                    if created:
                        images_created += 1
                    else:
                        images_updated += 1
                except ImageProduct.DoesNotExist:
                    # Si l'image n'existe pas, on la crée
                    ImageProduct.objects.create(
                        id=image_data['id'],
                        product_id=image_data['product'],
                        image=image_data['image'],
                        is_primary=image_data['is_primary'],
                        created_at=image_data['created_at'],
                        updated_at=image_data['updated_at']
                    )
                    images_created += 1
                    self.stdout.write(self.style.SUCCESS(f'Image {image_data["id"]} créée avec succès'))

            self.stdout.write(self.style.SUCCESS('Déploiement terminé avec succès!'))
            self.stdout.write(f'Produits : {products_created} créés, {products_updated} mis à jour')
            self.stdout.write(f'Téléphones : {phones_created} créés, {phones_updated} mis à jour')
            self.stdout.write(f'Images : {images_created} créées, {images_updated} mises à jour')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors du déploiement : {str(e)}'))

    def create_backup(self):
        """Crée une sauvegarde des données existantes"""
        try:
            # Créer le dossier de sauvegarde s'il n'existe pas
            backup_dir = os.path.join(settings.BASE_DIR, 'product', 'backups')
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            # Générer le nom du fichier de sauvegarde
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f'backup_{timestamp}.json')

            # Récupérer les données
            data = {
                'products': serializers.serialize('python', Product.objects.all()),
                'phones': serializers.serialize('python', Phone.objects.all()),
                'images': serializers.serialize('python', ImageProduct.objects.all())
            }

            # Sauvegarder les données
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.stdout.write(self.style.SUCCESS(f'Sauvegarde créée : {backup_file}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors de la création de la sauvegarde : {str(e)}')) 