from django.core.management.base import BaseCommand
from product.models import Category, Product, Phone, PhoneVariant, Color
from suppliers.models import Supplier
import json
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Importe les produits depuis un fichier JSON'

    def find_json_file(self):
        possible_paths = [
            os.path.join(settings.BASE_DIR, 'products.json'),
            os.path.join(settings.BASE_DIR, 'saga', 'product', 'data', 'products.json'),
            os.path.join(settings.BASE_DIR, 'saga', 'products.json'),
            '/app/products.json',
            '/app/saga/product/data/products.json',
        ]

        for path in possible_paths:
            if os.path.exists(path):
                print(f"Fichier JSON trouvé à : {path}")
                print(f"Taille du fichier : {os.path.getsize(path)} octets")
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"Contenu du fichier :")
                        print(content[:500] + "..." if len(content) > 500 else content)
                except Exception as e:
                    print(f"Erreur lors de la lecture du fichier : {e}")
                return path

        print("Recherche du fichier JSON dans le répertoire courant et ses sous-répertoires...")
        for root, dirs, files in os.walk(settings.BASE_DIR):
            for file in files:
                if file == 'products.json':
                    path = os.path.join(root, file)
                    print(f"Fichier JSON trouvé à : {path}")
                    print(f"Taille du fichier : {os.path.getsize(path)} octets")
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            print(f"Contenu du fichier :")
                            print(content[:500] + "..." if len(content) > 500 else content)
                    except Exception as e:
                        print(f"Erreur lors de la lecture du fichier : {e}")
                    return path

        print("Fichier products.json non trouvé. Voici les fichiers .json disponibles :")
        for root, dirs, files in os.walk(settings.BASE_DIR):
            for file in files:
                if file.endswith('.json'):
                    path = os.path.join(root, file)
                    print(f"- {path} ({os.path.getsize(path)} octets)")
        return None

    def handle(self, *args, **options):
        # Rechercher le fichier JSON
        json_path = self.find_json_file()
        if not json_path:
            print("Impossible de trouver le fichier products.json")
            return

        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Créer le fournisseur par défaut s'il n'existe pas
            supplier, created = Supplier.objects.get_or_create(
                id=1,
                defaults={
                    'name': 'Tecno',
                    'email': 'contact@tecno.com',
                    'phone': '+22300000000',
                    'address': 'Adresse par défaut',
                    'is_verified': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Fournisseur par défaut créé avec succès'))
            
            # Importer les catégories
            categories_count = 0
            for item in data:
                if item['model'] == 'product.category':
                    category, created = Category.objects.get_or_create(
                        id=item['pk'],
                        defaults={
                            'name': item['fields']['name'],
                            'slug': item['fields']['slug'],
                            'parent_id': item['fields']['parent']
                        }
                    )
                    if created:
                        categories_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'{categories_count} catégories importées avec succès'))
            
            # Importer les couleurs
            colors_count = 0
            for item in data:
                if item['model'] == 'product.color':
                    color, created = Color.objects.get_or_create(
                        id=item['pk'],
                        defaults={
                            'name': item['fields']['name'],
                            'code': item['fields']['code']
                        }
                    )
                    if created:
                        colors_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'{colors_count} couleurs importées avec succès'))
            
            # Importer les produits
            products_count = 0
            for item in data:
                if item['model'] == 'product.product':
                    product, created = Product.objects.get_or_create(
                        id=item['pk'],
                        defaults={
                            'title': item['fields']['title'],
                            'category_id': item['fields']['category'],
                            'price': item['fields']['price'],
                            'description': item['fields']['description'],
                            'highlight': item['fields']['highlight'],
                            'supplier_id': supplier.id,  # Utiliser le fournisseur par défaut
                            'is_active': item['fields']['is_active']
                        }
                    )
                    if created:
                        products_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'{products_count} produits importés avec succès'))
            
            # Importer les téléphones
            phones_count = 0
            for item in data:
                if item['model'] == 'product.phone':
                    phone, created = Phone.objects.get_or_create(
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
                    if created:
                        phones_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'{phones_count} téléphones importés avec succès'))
            
            # Importer les variantes de téléphones
            variants_count = 0
            for item in data:
                if item['model'] == 'product.phonevariant':
                    variant, created = PhoneVariant.objects.get_or_create(
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
                    if created:
                        variants_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'{variants_count} variantes de téléphones importées avec succès'))
            
            # Afficher un résumé final
            self.stdout.write(self.style.SUCCESS('\nRésumé de l\'importation :'))
            self.stdout.write(f'- {categories_count} catégories')
            self.stdout.write(f'- {colors_count} couleurs')
            self.stdout.write(f'- {products_count} produits')
            self.stdout.write(f'- {phones_count} téléphones')
            self.stdout.write(f'- {variants_count} variantes')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors de l\'importation: {str(e)}')) 