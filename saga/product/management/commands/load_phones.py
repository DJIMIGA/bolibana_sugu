from django.core.management.base import BaseCommand
from django.core.management import call_command
from product.models import Product, Phone, Color
import json
import os

class Command(BaseCommand):
    help = 'Charge les téléphones depuis le fichier fixtures avec des logs détaillés'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("\n" + "="*80))
        self.stdout.write(self.style.SUCCESS("DÉBUT DU CHARGEMENT DES TÉLÉPHONES"))
        self.stdout.write(self.style.SUCCESS("="*80))

        # Chemin vers le fichier fixtures
        fixtures_dir = os.path.join('saga', 'product', 'fixtures')
        fixture_path = os.path.join(fixtures_dir, 'phones.json')
        
        self.stdout.write(f"\n>>> Lecture du fichier : {fixture_path}")
        
        if not os.path.exists(fixture_path):
            self.stdout.write(self.style.ERROR(f"!!! ERREUR: Fichier {fixture_path} non trouvé !!!"))
            return

        # Lire le fichier JSON
        with open(fixture_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Compteurs
        total_objects = len(data)
        colors_created = 0
        products_created = 0
        phones_created = 0
        colors_skipped = 0
        products_skipped = 0
        phones_skipped = 0

        # Traiter d'abord les couleurs
        for item in data:
            if item['model'] == 'product.color':
                color, created = Color.objects.get_or_create(
                    name=item['fields']['name'],
                    defaults={'code': item['fields']['code']}
                )
                if created:
                    colors_created += 1
                    self.stdout.write(self.style.SUCCESS(f">>> Couleur créée : {color.name}"))
                else:
                    colors_skipped += 1
                    self.stdout.write(self.style.WARNING(f">>> Couleur existante ignorée : {color.name}"))

        # Traiter ensuite les produits
        for item in data:
            if item['model'] == 'product.product':
                product, created = Product.objects.get_or_create(
                    title=item['fields']['title'],
                    category_id=item['fields']['category'],
                    defaults={
                        'price': item['fields']['price'],
                        'description': item['fields']['description'],
                        'highlight': item['fields']['highlight'],
                        'supplier_id': item['fields']['supplier'],
                        'is_active': item['fields']['is_active'],
                        'disponible_salam': item['fields']['disponible_salam'],
                        'stock': item['fields']['stock'],
                        'sku': item['fields']['sku'],
                        'color_id': item['fields']['color']
                    }
                )
                if created:
                    products_created += 1
                    self.stdout.write(self.style.SUCCESS(f">>> Produit créé : {product.title}"))
                else:
                    products_skipped += 1
                    self.stdout.write(self.style.WARNING(f">>> Produit existant ignoré : {product.title}"))

        # Traiter enfin les téléphones
        for item in data:
            if item['model'] == 'product.phone':
                phone, created = Phone.objects.get_or_create(
                    product_id=item['fields']['product'],
                    defaults={
                        'brand': item['fields']['brand'],
                        'model': item['fields']['model'],
                        'operating_system': item['fields']['operating_system'],
                        'screen_size': item['fields']['screen_size'],
                        'resolution': item['fields']['resolution'],
                        'processor': item['fields']['processor'],
                        'battery_capacity': item['fields']['battery_capacity'],
                        'camera_main': item['fields']['camera_main'],
                        'camera_front': item['fields']['camera_front'],
                        'network': item['fields']['network'],
                        'warranty': item['fields']['warranty'],
                        'is_new': item['fields']['is_new'],
                        'box_included': item['fields']['box_included'],
                        'accessories': item['fields']['accessories'],
                        'storage': item['fields']['storage'],
                        'ram': item['fields']['ram'],
                        'color_id': item['fields']['color']
                    }
                )
                if created:
                    phones_created += 1
                    self.stdout.write(self.style.SUCCESS(f">>> Téléphone créé : {phone.brand} {phone.model}"))
                else:
                    phones_skipped += 1
                    self.stdout.write(self.style.WARNING(f">>> Téléphone existant ignoré : {phone.brand} {phone.model}"))

        # Afficher le résumé
        self.stdout.write(self.style.SUCCESS("\n" + "="*80))
        self.stdout.write(self.style.SUCCESS("RÉSUMÉ DU CHARGEMENT"))
        self.stdout.write(self.style.SUCCESS("="*80))
        self.stdout.write(f"\n>>> Total des objets dans le fichier : {total_objects}")
        self.stdout.write(f">>> Couleurs créées : {colors_created}")
        self.stdout.write(f">>> Couleurs ignorées : {colors_skipped}")
        self.stdout.write(f">>> Produits créés : {products_created}")
        self.stdout.write(f">>> Produits ignorés : {products_skipped}")
        self.stdout.write(f">>> Téléphones créés : {phones_created}")
        self.stdout.write(f">>> Téléphones ignorés : {phones_skipped}")
        self.stdout.write(self.style.SUCCESS("\n" + "="*80))
        self.stdout.write(self.style.SUCCESS("FIN DU CHARGEMENT"))
        self.stdout.write(self.style.SUCCESS("="*80 + "\n")) 