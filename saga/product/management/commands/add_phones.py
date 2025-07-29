from django.core.management.base import BaseCommand
from django.core.management import call_command
from product.models import Product, Phone, Category, Color, Supplier
from django.utils.text import slugify
from decimal import Decimal
import json
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Ajoute de nouveaux téléphones au système'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Chemin vers le fichier JSON contenant les données des téléphones',
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Mode interactif pour ajouter un téléphone manuellement',
        )
        parser.add_argument(
            '--category',
            type=int,
            default=1,
            help='ID de la catégorie pour les téléphones (défaut: 1)',
        )
        parser.add_argument(
            '--supplier',
            type=int,
            default=1,
            help='ID du fournisseur (défaut: 1)',
        )

    def handle(self, *args, **options):
        if options['file']:
            self.add_phones_from_file(options['file'], options['category'], options['supplier'])
        elif options['interactive']:
            self.add_phone_interactive(options['category'], options['supplier'])
        else:
            self.stdout.write(self.style.ERROR(
                'Veuillez spécifier --file pour un fichier JSON ou --interactive pour le mode manuel'
            ))

    def generate_unique_title(self, brand, model, storage, ram, color_name):
        """Génère un titre unique pour le téléphone"""
        return f"{brand} {model} {storage}GB {ram}GB {color_name}"

    def add_phones_from_file(self, file_path, category_id, supplier_id):
        """Ajoute des téléphones à partir d'un fichier JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                phones_data = json.load(f)

            category = Category.objects.get(id=category_id)
            supplier = Supplier.objects.get(id=supplier_id)

            phones_created = 0
            phones_updated = 0

            for phone_data in phones_data:
                try:
                    # Extraire les données pour le titre unique
                    storage = phone_data.get('storage', 64)
                    ram = phone_data.get('ram', 4)
                    color_name = phone_data.get('color', 'Noir')
                    brand = phone_data['brand']
                    model = phone_data['model']
                    
                    # Générer un titre unique avec ROM, RAM et couleur
                    unique_title = self.generate_unique_title(brand, model, storage, ram, color_name)
                    
                    # Créer ou mettre à jour le produit
                    product, product_created = Product.objects.update_or_create(
                        title=unique_title,
                        defaults={
                            'description': phone_data.get('description', ''),
                            'price': phone_data['price'],
                            'category': category,
                            'supplier': supplier,
                            'brand': brand,
                            'is_available': phone_data.get('is_available', True),
                            'stock': phone_data.get('stock', 0),
                            'sku': phone_data.get('sku', ''),
                            'condition': phone_data.get('condition', 'new'),
                            'has_warranty': phone_data.get('has_warranty', True),
                            'discount_price': phone_data.get('discount_price'),
                            'is_trending': phone_data.get('is_trending', False),
                        }
                    )

                    # Obtenir ou créer la couleur
                    color, _ = Color.objects.get_or_create(
                        name=color_name,
                        defaults={'code': '#000000'}
                    )

                    # Créer ou mettre à jour le téléphone
                    phone, phone_created = Phone.objects.update_or_create(
                        product=product,
                        defaults={
                            'brand': brand,
                            'model': model,
                            'operating_system': phone_data.get('operating_system', 'Android'),
                            'screen_size': phone_data.get('screen_size', 6.0),
                            'resolution': phone_data.get('resolution', '1920x1080'),
                            'processor': phone_data.get('processor', 'Inconnu'),
                            'battery_capacity': phone_data.get('battery_capacity', 3000),
                            'camera_main': phone_data.get('camera_main', 'Inconnue'),
                            'camera_front': phone_data.get('camera_front', 'Inconnue'),
                            'network': phone_data.get('network', '4G'),
                            'imei': phone_data.get('imei'),
                            'is_new': phone_data.get('is_new', True),
                            'box_included': phone_data.get('box_included', True),
                            'accessories': phone_data.get('accessories', ''),
                            'storage': storage,
                            'ram': ram,
                            'color': color,
                        }
                    )

                    if phone_created:
                        phones_created += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Téléphone créé: {unique_title}')
                        )
                    else:
                        phones_updated += 1
                        self.stdout.write(
                            self.style.WARNING(f'🔄 Téléphone mis à jour: {unique_title}')
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Erreur avec {phone_data.get("title", "Téléphone inconnu")}: {str(e)}')
                    )

            self.stdout.write(self.style.SUCCESS(
                f'\n📱 Résumé: {phones_created} téléphones créés, {phones_updated} mis à jour'
            ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ Fichier non trouvé: {file_path}'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'❌ Erreur de format JSON dans: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur générale: {str(e)}'))

    def add_phone_interactive(self, category_id, supplier_id):
        """Ajoute un téléphone en mode interactif"""
        try:
            category = Category.objects.get(id=category_id)
            supplier = Supplier.objects.get(id=supplier_id)

            self.stdout.write(self.style.SUCCESS('📱 Ajout d\'un nouveau téléphone\n'))

            # Informations du produit
            brand = input('🏭 Marque: ')
            model = input('📱 Modèle: ')
            storage = int(input('💾 Stockage en GB (défaut: 64): ') or '64')
            ram = int(input('🧠 RAM en GB (défaut: 4): ') or '4')
            color_name = input('🎨 Couleur (défaut: Noir): ') or 'Noir'
            
            # Générer le titre unique
            unique_title = self.generate_unique_title(brand, model, storage, ram, color_name)
            self.stdout.write(f'📝 Titre généré: {unique_title}')
            
            description = input('📄 Description (optionnel): ')
            price = int(input('💰 Prix (FCFA): '))
            stock = int(input('📦 Stock disponible: '))
            sku = input('🏷️ SKU (optionnel): ')

            # Informations techniques
            operating_system = input('💻 Système d\'exploitation (défaut: Android): ') or 'Android'
            screen_size = float(input('📺 Taille d\'écran en pouces (défaut: 6.0): ') or '6.0')
            resolution = input('🖥️ Résolution (défaut: 1920x1080): ') or '1920x1080'
            processor = input('⚡ Processeur (défaut: Inconnu): ') or 'Inconnu'
            battery_capacity = int(input('🔋 Capacité batterie en mAh (défaut: 3000): ') or '3000')
            camera_main = input('📷 Caméra principale (défaut: Inconnue): ') or 'Inconnue'
            camera_front = input('📸 Caméra frontale (défaut: Inconnue): ') or 'Inconnue'
            network = input('📡 Réseau (défaut: 4G): ') or '4G'

            # Options
            is_new = input('🆕 Neuf? (y/n, défaut: y): ').lower() != 'n'
            box_included = input('📦 Boîte incluse? (y/n, défaut: y): ').lower() != 'n'
            accessories = input('🔧 Accessoires (optionnel): ')
            imei = input('🔢 IMEI (optionnel): ')

            # Créer la couleur
            color, _ = Color.objects.get_or_create(
                name=color_name,
                defaults={'code': '#000000'}
            )

            # Créer le produit
            product = Product.objects.create(
                title=unique_title,
                description=description,
                price=price,
                category=category,
                supplier=supplier,
                brand=brand,
                stock=stock,
                sku=sku,
                condition='new' if is_new else 'used',
                has_warranty=True,
            )

            # Créer le téléphone
            phone = Phone.objects.create(
                product=product,
                brand=brand,
                model=model,
                operating_system=operating_system,
                screen_size=screen_size,
                resolution=resolution,
                processor=processor,
                battery_capacity=battery_capacity,
                camera_main=camera_main,
                camera_front=camera_front,
                network=network,
                storage=storage,
                ram=ram,
                color=color,
                is_new=is_new,
                box_included=box_included,
                accessories=accessories,
                imei=imei if imei else None,
            )

            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Téléphone créé avec succès!\n'
                f'📱 {product.title}\n'
                f'💰 {product.price} FCFA\n'
                f'📦 Stock: {product.stock}\n'
                f'🏷️ SKU: {product.sku}\n'
                f'🔗 URL: {product.get_absolute_url()}'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur: {str(e)}'))

    def create_sample_file(self):
        """Crée un fichier d'exemple pour l'ajout de téléphones"""
        sample_data = [
            {
                "title": "Samsung Galaxy A15 4G",
                "description": "Le Samsung Galaxy A15 4G offre une expérience utilisateur fluide avec son écran de 6.5 pouces et sa batterie de 5000mAh.",
                "price": 85000,
                "brand": "Samsung",
                "model": "Galaxy A15 4G",
                "operating_system": "Android 14",
                "screen_size": 6.5,
                "resolution": "2400x1080",
                "processor": "MediaTek Helio G99",
                "battery_capacity": 5000,
                "camera_main": "50MP + 5MP + 2MP",
                "camera_front": "13MP",
                "network": "4G LTE",
                "storage": 128,
                "ram": 6,
                "color": "Noir",
                "stock": 15,
                "sku": "SAM-A15-128-6-BK",
                "is_new": True,
                "box_included": True,
                "accessories": "Téléphone, Chargeur, Câble USB-C, Écouteurs",
                "condition": "new",
                "has_warranty": True,
                "is_trending": True
            },
            {
                "title": "iPhone 13 128GB",
                "description": "L'iPhone 13 avec son système A15 Bionic et sa caméra double 12MP offre des performances exceptionnelles.",
                "price": 450000,
                "brand": "Apple",
                "model": "iPhone 13",
                "operating_system": "iOS 17",
                "screen_size": 6.1,
                "resolution": "2532x1170",
                "processor": "A15 Bionic",
                "battery_capacity": 3240,
                "camera_main": "12MP + 12MP",
                "camera_front": "12MP",
                "network": "5G",
                "storage": 128,
                "ram": 4,
                "color": "Bleu",
                "stock": 8,
                "sku": "APP-IP13-128-4-BL",
                "is_new": True,
                "box_included": True,
                "accessories": "iPhone, Câble Lightning, Chargeur 20W",
                "condition": "new",
                "has_warranty": True,
                "is_trending": True
            }
        ]

        filename = f'phones_sample_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f'📄 Fichier d\'exemple créé: {filename}'))
        return filename 