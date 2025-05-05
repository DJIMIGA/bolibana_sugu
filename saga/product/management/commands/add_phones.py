from django.core.management.base import BaseCommand
from product.models import Product, Phone, Color, Category
from suppliers.models import Supplier
from decimal import Decimal

class Command(BaseCommand):
    help = 'Ajoute des téléphones à la base de données'

    def handle(self, *args, **options):
        # Créer ou récupérer la catégorie Téléphones
        category, _ = Category.objects.get_or_create(
            name='Téléphones',
            defaults={'slug': 'telephones'}
        )

        # Créer ou récupérer le fournisseur Tecno
        supplier, _ = Supplier.objects.get_or_create(
            name='Tecno Mobile',
            defaults={
                'description': 'Tecno Mobile est une marque de smartphones innovants et abordables',
                'specialty': 'Fournisseur de TELEPHONE',
                'slug': 'tecno-mobile'
            }
        )

        # Liste des téléphones à ajouter
        phones = [
            {
                'title': 'Tecno POP 2F Or Champagne',
                'model': 'POP 2F',
                'description': '''Le Tecno POP 2F en Or Champagne est un smartphone économique avec un design élégant et des fonctionnalités essentielles.

Caractéristiques principales :
- Écran tactile de 5.5 pouces (960x480px)
- 16GB de stockage interne
- 1GB de RAM
- Processeur Quad-Core 1.3 GHz
- Batterie 2400mAh
- Caméra avant 8MP avec Flash
- Caméra arrière 5MP avec Flash
- Déverrouillage facial
- Capteur d'empreintes digitales
- Système d'exploitation HiOS basé sur Android 8.1 (Go edition)

Dimensions :
- Hauteur : 149.76 mm
- Largeur : 72.8 mm
- Épaisseur : 9.35 mm

Connectivité :
- WiFi
- Capteurs : G-Sensor, Capteur d'empreintes digitales

Contenu de la boîte :
- Téléphone
- Câble de chargeur
- Chargeur''',
                'operating_system': 'HiOS basé sur Android 8.1 (Go edition)',
                'processor': 'Processeur Quad-Core 1.3 GHz',
                'screen_size': Decimal('5.5'),
                'resolution': '960x480px',
                'camera_main': 'Caméra arrière 5MP avec Flash',
                'camera_front': 'Caméra avant 8MP avec Flash',
                'battery_capacity': 2400,
                'storage': 16,
                'ram': 1,
                'price': 75000,
                'stock': 20,
                'sku': 'TEC-P2F-16-1-OC',
                'color_name': 'Or Champagne',
                'color_code': '#FFD700',
                'box_contents': 'Téléphone, Câble de chargeur, Chargeur'
            },
            {
                'title': 'Tecno POP 2F Noir Minuit',
                'model': 'POP 2F',
                'description': '''Le Tecno POP 2F en Noir Minuit est un smartphone économique avec un design élégant et des fonctionnalités essentielles.

Caractéristiques principales :
- Écran tactile de 5.5 pouces (960x480px)
- 16GB de stockage interne
- 1GB de RAM
- Processeur Quad-Core 1.3 GHz
- Batterie 2400mAh
- Caméra avant 8MP avec Flash
- Caméra arrière 5MP avec Flash
- Déverrouillage facial
- Capteur d'empreintes digitales
- Système d'exploitation HiOS basé sur Android 8.1 (Go edition)

Dimensions :
- Hauteur : 149.76 mm
- Largeur : 72.8 mm
- Épaisseur : 9.35 mm

Connectivité :
- WiFi
- Capteurs : G-Sensor, Capteur d'empreintes digitales

Contenu de la boîte :
- Téléphone
- Câble de chargeur
- Chargeur''',
                'operating_system': 'HiOS basé sur Android 8.1 (Go edition)',
                'processor': 'Processeur Quad-Core 1.3 GHz',
                'screen_size': Decimal('5.5'),
                'resolution': '960x480px',
                'camera_main': 'Caméra arrière 5MP avec Flash',
                'camera_front': 'Caméra avant 8MP avec Flash',
                'battery_capacity': 2400,
                'storage': 16,
                'ram': 1,
                'price': 75000,
                'stock': 20,
                'sku': 'TEC-P2F-16-1-NM',
                'color_name': 'Noir Minuit',
                'color_code': '#000000',
                'box_contents': 'Téléphone, Câble de chargeur, Chargeur'
            },
            {
                'title': 'Tecno POP 2F Bleu Ville',
                'model': 'POP 2F',
                'description': '''Le Tecno POP 2F en Bleu Ville est un smartphone économique avec un design élégant et des fonctionnalités essentielles.

Caractéristiques principales :
- Écran tactile de 5.5 pouces (960x480px)
- 16GB de stockage interne
- 1GB de RAM
- Processeur Quad-Core 1.3 GHz
- Batterie 2400mAh
- Caméra avant 8MP avec Flash
- Caméra arrière 5MP avec Flash
- Déverrouillage facial
- Capteur d'empreintes digitales
- Système d'exploitation HiOS basé sur Android 8.1 (Go edition)

Dimensions :
- Hauteur : 149.76 mm
- Largeur : 72.8 mm
- Épaisseur : 9.35 mm

Connectivité :
- WiFi
- Capteurs : G-Sensor, Capteur d'empreintes digitales

Contenu de la boîte :
- Téléphone
- Câble de chargeur
- Chargeur''',
                'operating_system': 'HiOS basé sur Android 8.1 (Go edition)',
                'processor': 'Processeur Quad-Core 1.3 GHz',
                'screen_size': Decimal('5.5'),
                'resolution': '960x480px',
                'camera_main': 'Caméra arrière 5MP avec Flash',
                'camera_front': 'Caméra avant 8MP avec Flash',
                'battery_capacity': 2400,
                'storage': 16,
                'ram': 1,
                'price': 75000,
                'stock': 20,
                'sku': 'TEC-P2F-16-1-BV',
                'color_name': 'Bleu Ville',
                'color_code': '#1E90FF',
                'box_contents': 'Téléphone, Câble de chargeur, Chargeur'
            }
        ]

        for phone_data in phones:
            try:
                # Créer ou récupérer la couleur
                color, _ = Color.objects.get_or_create(
                    name=phone_data['color_name'],
                    defaults={'code': phone_data['color_code']}
                )

                # Créer le produit
                product = Product.objects.create(
                    title=phone_data['title'],
                    category=category,
                    price=phone_data['price'],
                    description=phone_data['description'],
                    stock=phone_data['stock'],
                    sku=phone_data['sku'],
                    color=color,
                    supplier=supplier
                )

                # Créer le téléphone
                Phone.objects.create(
                    product=product,
                    brand='Tecno',
                    model=phone_data['model'],
                    operating_system=phone_data['operating_system'],
                    screen_size=phone_data['screen_size'],
                    resolution=phone_data['resolution'],
                    processor=phone_data['processor'],
                    camera_main=phone_data['camera_main'],
                    camera_front=phone_data['camera_front'],
                    battery_capacity=phone_data['battery_capacity'],
                    storage=phone_data['storage'],
                    ram=phone_data['ram'],
                    color=color,
                    accessories=phone_data['box_contents']
                )

                self.stdout.write(self.style.SUCCESS(f"Téléphone {phone_data['title']} ajouté avec succès"))

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Erreur lors de l'ajout du téléphone {phone_data['title']}: {str(e)}")
                ) 