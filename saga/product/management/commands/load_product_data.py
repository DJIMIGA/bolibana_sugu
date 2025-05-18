from django.core.management.base import BaseCommand
from django.core import serializers
from product.models import Product, Phone, Category, Color, ImageProduct
import json
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Charge les données des produits avec vérification d\'existence'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Chemin vers le fichier JSON')

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors de la lecture du fichier: {str(e)}'))
            return

        # Compteurs pour les statistiques
        stats = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }

        # Traitement des catégories
        for item in data:
            if item['model'] == 'product.category':
                try:
                    category, created = Category.objects.get_or_create(
                        id=item['pk'],
                        defaults=item['fields']
                    )
                    if created:
                        stats['created'] += 1
                    else:
                        stats['updated'] += 1
                except Exception as e:
                    logger.error(f"Erreur lors du traitement de la catégorie {item['pk']}: {str(e)}")
                    stats['errors'] += 1

        # Traitement des couleurs
        for item in data:
            if item['model'] == 'product.color':
                try:
                    color, created = Color.objects.get_or_create(
                        id=item['pk'],
                        defaults=item['fields']
                    )
                    if created:
                        stats['created'] += 1
                    else:
                        stats['updated'] += 1
                except Exception as e:
                    logger.error(f"Erreur lors du traitement de la couleur {item['pk']}: {str(e)}")
                    stats['errors'] += 1

        # Traitement des produits
        for item in data:
            if item['model'] == 'product.product':
                try:
                    product, created = Product.objects.get_or_create(
                        id=item['pk'],
                        defaults=item['fields']
                    )
                    if created:
                        stats['created'] += 1
                    else:
                        # Mise à jour des champs si le produit existe
                        for field, value in item['fields'].items():
                            setattr(product, field, value)
                        product.save()
                        stats['updated'] += 1
                except Exception as e:
                    logger.error(f"Erreur lors du traitement du produit {item['pk']}: {str(e)}")
                    stats['errors'] += 1

        # Traitement des téléphones
        for item in data:
            if item['model'] == 'product.phone':
                try:
                    phone, created = Phone.objects.get_or_create(
                        id=item['pk'],
                        defaults=item['fields']
                    )
                    if created:
                        stats['created'] += 1
                    else:
                        # Mise à jour des champs si le téléphone existe
                        for field, value in item['fields'].items():
                            setattr(phone, field, value)
                        phone.save()
                        stats['updated'] += 1
                except Exception as e:
                    logger.error(f"Erreur lors du traitement du téléphone {item['pk']}: {str(e)}")
                    stats['errors'] += 1

        # Traitement des images
        for item in data:
            if item['model'] == 'product.imageproduct':
                try:
                    image, created = ImageProduct.objects.get_or_create(
                        id=item['pk'],
                        defaults=item['fields']
                    )
                    if created:
                        stats['created'] += 1
                    else:
                        # Mise à jour des champs si l'image existe
                        for field, value in item['fields'].items():
                            setattr(image, field, value)
                        image.save()
                        stats['updated'] += 1
                except Exception as e:
                    logger.error(f"Erreur lors du traitement de l'image {item['pk']}: {str(e)}")
                    stats['errors'] += 1

        # Affichage des statistiques
        self.stdout.write(self.style.SUCCESS(f'''
Chargement terminé :
- {stats['created']} objets créés
- {stats['updated']} objets mis à jour
- {stats['skipped']} objets ignorés
- {stats['errors']} erreurs
''')) 