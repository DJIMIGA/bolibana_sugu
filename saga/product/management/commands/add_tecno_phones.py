from django.core.management.base import BaseCommand
from product.models import Product, Category, Phone, PhoneVariant, Color, Supplier
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
import uuid

class Command(BaseCommand):
    help = 'Ajoute les téléphones Tecno et leurs variantes dans la base de données'

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                # Récupérer la catégorie Téléphones
                try:
                    category = Category.objects.get(name='Téléphones')
                except Category.DoesNotExist:
                    self.stdout.write(self.style.ERROR('La catégorie Téléphones n\'existe pas'))
                    return

                # Récupérer le fournisseur Tecno
                try:
                    supplier = Supplier.objects.get(name='Tecno')
                except Supplier.DoesNotExist:
                    self.stdout.write(self.style.ERROR('Le fournisseur Tecno n\'existe pas'))
                    return

                # Données du téléphone
                phone_data = {
                    'model': 'POP 2F',
                    'brand': 'Tecno',
                    'title': 'POP 2F',
                    'description': '''Le POP 2F est un smartphone économique avec un design moderne et des fonctionnalités essentielles.
                    
Caractéristiques principales :
- Écran 5.5" Touchscreen
- Processeur Quad-Core 1.3 GHz
- Caméra beauté 8MP avant
- Batterie 2400mAh
- Déverrouillage facial et par empreinte

Spécifications détaillées :
- Système d'exploitation : HiOS basé sur Android 8.1 (Go Edition)
- Processeur : Quad-Core 1.3 GHz
- Réseaux : WiFi
- Dimensions : 149.76 x 72.8 x 9.35 mm
- Écran : 5.5" Touchscreen
- Résolution : 480 x 960
- Caméra avant : 8MP avec Flash
- Caméra arrière : 5MP avec Flash
- Connectivité : WiFi
- Capteurs : G-Sensor, Capteur d'empreintes
- Batterie : 2400 mAh
- Mémoire : 16GB ROM + 1GB RAM''',
                    'highlight': '''Écran 5.5" Touchscreen
Processeur Quad-Core 1.3 GHz
Caméra beauté 8MP avant
Batterie 2400mAh
Déverrouillage facial et par empreinte''',
                    'operating_system': 'HiOS basé sur Android 8.1 (Go Edition)',
                    'screen_size': 5.5,
                    'resolution': '480 x 960',
                    'processor': 'Quad-Core 1.3 GHz',
                    'battery_capacity': 2400,
                    'camera_main': '5MP avec Flash',
                    'camera_front': '8MP avec Flash',
                    'network': 'WiFi',
                    'warranty': '12 mois',
                    'accessories': 'Chargeur, Câble USB, Manuel d\'utilisation'
                }

                # Couleurs disponibles
                colors = {
                    'Or Champagne': '#F7E7CE',
                    'Noir Minuit': '#000000',
                    'Bleu Ville': '#1E90FF',
                }

                # Créer les couleurs si elles n'existent pas
                color_objects = {}
                for color_name, hex_code in colors.items():
                    color, created = Color.objects.get_or_create(
                        name=color_name,
                        defaults={'code': hex_code}
                    )
                    color_objects[color_name] = color
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Couleur {color_name} créée'))

                # Vérifier si le produit existe déjà
                try:
                    product = Product.objects.get(title=phone_data['title'], category=category)
                    phone = Phone.objects.get(product=product)
                    self.stdout.write(self.style.WARNING(f'Le produit {phone_data["title"]} existe déjà'))
                except (Product.DoesNotExist, Phone.DoesNotExist):
                    # Créer le produit
            product = Product.objects.create(
                title=phone_data['title'],
                category=category,
                        price=0,  # Prix de base, sera remplacé par les variantes
                description=phone_data['description'],
                highlight=phone_data['highlight'],
                supplier=supplier,
                is_active=True
            )

                    # Générer un IMEI unique
                    imei = str(uuid.uuid4().int)[:15]

                    # Créer le téléphone
            phone = Phone.objects.create(
                product=product,
                        model=phone_data['model'],
                        brand=phone_data['brand'],
                        operating_system=phone_data['operating_system'],
                        screen_size=phone_data['screen_size'],
                        resolution=phone_data['resolution'],
                        processor=phone_data['processor'],
                        battery_capacity=phone_data['battery_capacity'],
                        camera_main=phone_data['camera_main'],
                        camera_front=phone_data['camera_front'],
                        network=phone_data['network'],
                        warranty=phone_data['warranty'],
                        imei=imei,
                        is_new=True,
                        box_included=True,
                        accessories=phone_data['accessories']
                    )

                    self.stdout.write(self.style.SUCCESS(f'Le produit {phone_data["title"]} a été créé'))

                # Variantes à ajouter
                variants_to_add = [
                    # Variantes 16GB
                    {
                        'color': 'Or Champagne',
                        'storage': 16,
                        'ram': 1,
                        'price': 39900,
                        'stock': 10,
                        'sku': 'TECNO-POP-2F-Or Champagne-16GB-1GB'
                    },
                    {
                        'color': 'Noir Minuit',
                        'storage': 16,
                        'ram': 1,
                        'price': 39900,
                        'stock': 10,
                        'sku': 'TECNO-POP-2F-Noir Minuit-16GB-1GB'
                    },
                    {
                        'color': 'Bleu Ville',
                        'storage': 16,
                        'ram': 1,
                        'price': 39900,
                        'stock': 10,
                        'sku': 'TECNO-POP-2F-Bleu Ville-16GB-1GB'
                    }
                ]

                # Ajouter les variantes
                for variant_data in variants_to_add:
                    try:
                        color = color_objects[variant_data['color']]
                        
                        variant, created = PhoneVariant.objects.get_or_create(
                    phone=phone,
                    color=color,
                    storage=variant_data['storage'],
                            ram=variant_data['ram'],
                            defaults={
                                'price': variant_data['price'],
                                'stock': variant_data['stock'],
                                'sku': variant_data['sku']
                            }
                        )

                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Variante {variant} créée avec succès'))
                        else:
                            self.stdout.write(self.style.WARNING(f'La variante {variant} existe déjà'))

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Erreur lors de l\'ajout de la variante: {str(e)}'))

                self.stdout.write(self.style.SUCCESS('Importation des variantes Tecno terminée'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Une erreur est survenue: {str(e)}'))
            # Ne pas lever l'exception pour éviter le rollback
            pass 