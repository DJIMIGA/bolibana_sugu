from django.core.management.base import BaseCommand
from django.db import transaction
from product.models import Product, Phone, Color, Category, Supplier
from product.utils import normalize_phone_brand
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Ajoute tous les modèles TECNO SPARK avec leurs spécifications complètes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les téléphones qui seraient créés sans les ajouter',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write('📋 Mode DRY-RUN activé - Aucun téléphone ne sera créé')
        
        self.stdout.write('📱 Début de l\'ajout des téléphones TECNO SPARK...')
        
        # Normaliser automatiquement la marque
        brand = 'TECNO'
        normalized_brand = normalize_phone_brand(brand)
        
        self.stdout.write(f'🏷️  Marque originale: {brand}')
        self.stdout.write(f'✅ Marque normalisée: {normalized_brand}')
        
        # Récupérer ou créer la catégorie Téléphones
        try:
            phone_category = Category.objects.get(slug='telephones')
        except Category.DoesNotExist:
            phone_category, created = Category.objects.get_or_create(
                slug='telephones',
                defaults={
                    'name': 'Téléphones',
                    'is_main': True,
                    'order': 1
                }
            )
        
        # Récupérer ou créer le fournisseur TECNO
        try:
            tecno_supplier = Supplier.objects.get(company_name=normalized_brand)
            self.stdout.write(f'✅ Fournisseur existant trouvé: {tecno_supplier.company_name}')
        except Supplier.DoesNotExist:
            # Créer un nouveau fournisseur avec un slug unique
            tecno_supplier = Supplier.objects.create(
                company_name=normalized_brand,
                description='Fabricant de téléphones mobiles',
                email='contact@tecno-mobile.com',
                is_verified=True,
                slug=f'{normalized_brand.lower()}-mobile'  # Slug unique
            )
            self.stdout.write(f'✅ Nouveau fournisseur créé: {tecno_supplier.company_name}')
        
        # Spécifications de tous les modèles SPARK (mise à jour avec données exactes)
        spark_models = [
            # SPARK Go 1 - Spécifications exactes fournies
            {
                'model': 'SPARK Go 1',
                'title': 'TECNO SPARK Go 1',
                'description': 'Téléphone d\'entrée de gamme avec écran 6.67" 120Hz et batterie 5000mAh',
                'price': 45000,
                'specifications': {
                    'operating_system': 'Android 14 Go',
                    'processor': 'T615',
                    'network': ['2G', '3G', '4G', '4.5G (LTE Advanced)'],
                    'dimension': '165.62x77.01x8.35 mm',
                    'display': '120Hz 6.67" Hole Screen',
                    'resolution': '720*1600',
                    'camera_front': '8MP, Front Dual Flash',
                    'camera_main': '13MP, Rear Dual Flash',
                    'water_resistance': 'IP54 Rating',
                    'touch_control': 'Wet & Oily Touch Control',
                    'sensor': 'Side Fingerprint Sensor, Infrared Remote Control',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '15W Fast Charge',
                    'charging_port': 'Type-C',
                    'loudspeaker': 'Dual Speakers, DTS Sound',
                    'memory_options': [
                        '64GB ROM+6GB RAM*(3GB+3GB Extended)',
                        '64GB ROM+8GB RAM*(4GB+4GB Extended)',
                        '128GB ROM+6GB RAM*(3GB+3GB Extended)',
                        '128GB ROM+8GB RAM*(4GB+4GB Extended)'
                    ]
                },
                'colors': ['Noir Startrail', 'Blanc Scintillant'],
                'storage_options': [64, 128],
                'ram_options': [6, 8]
            },
            # SPARK Go 1S - Spécifications exactes fournies
            {
                'model': 'SPARK Go 1S',
                'title': 'TECNO SPARK Go 1S',
                'description': 'Successeur du SPARK Go 1 avec processeur G50 et écran 90Hz',
                'price': 48000,
                'specifications': {
                    'operating_system': 'Android 14 Go',
                    'processor': 'G50',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '165.62x77.01x8.35 mm',
                    'display': '90Hz 6.67" Hole Screen',
                    'resolution': '720*1600',
                    'camera_front': '8MP, Front Dual Flash',
                    'camera_main': '13MP, Rear Dual Flash',
                    'sensor': 'Software Gyroscope, Side Fingerprint Sensor, Infrared Remote Control',
                    'connectivity': ['GPS', 'WiFi', 'BT', 'FM', 'OTG'],
                    'memory_options': [
                        '64GB ROM+6GB RAM*(3GB+3GB Extended)'
                    ]
                },
                'colors': ['Noir Startrail', 'Blanc Scintillant'],
                'storage_options': [64],
                'ram_options': [6]
            },
            # SPARK 30 - Spécifications exactes fournies
            {
                'model': 'SPARK 30',
                'title': 'TECNO SPARK 30',
                'description': 'Smartphone premium avec écran 6.78" FHD+, caméra SONY IMX682 64MP et Dolby Atmos',
                'price': 95000,
                'specifications': {
                    'operating_system': 'Android 14',
                    'processor': 'MediaTek Helio G91',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '168.6x76.6x8.4 mm',
                    'display': '90Hz 6.78" FHD+ Hole Screen',
                    'resolution': '1080*2460',
                    'camera_front': '13MP, Front Dual Colour Temperature Flash',
                    'camera_main': 'SONY IMX682 64MP, Rear Four Flash',
                    'fingerprint': 'Side-mounted',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '18W Fast Charge',
                    'charging_port': 'Type-C',
                    'loudspeaker': 'Stereo Dual Speakers, Dolby Atmos',
                    'infrared_remote': 'Supported',
                    'nfc': 'Supported',
                    'water_resistance': 'IP64 Rating',
                    'touch_control': 'Wet & Oily Touch Control',
                    'memory_options': [
                        '128GB ROM+16GB RAM*(8GB+8GB Extended)',
                        '256GB ROM+16GB RAM*(8GB+8GB Extended)'
                    ]
                },
                'colors': ['Glace Astrale', 'Ombre Stellaire'],
                'storage_options': [128, 256],
                'ram_options': [16]
            },
            # SPARK 30 Pro - Spécifications exactes fournies
            {
                'model': 'SPARK 30 Pro',
                'title': 'TECNO SPARK 30 Pro',
                'description': 'Smartphone ultra-premium avec écran AMOLED 6.78" 120Hz, caméra 108MP et charge 33W',
                'price': 120000,
                'specifications': {
                    'operating_system': 'Android 14',
                    'processor': 'MediaTek Helio G100',
                    'network': ['2G', '3G', '4G', '4.5G (LTE Advanced)'],
                    'dimension': '168.6x76.6x8.4 mm',
                    'display': '120Hz 6.78" AMOLED Hole Screen',
                    'resolution': '1080*2436',
                    'camera_front': '13MP, Front Dual Colour Temperature Flash',
                    'camera_main': '108MP, Rear Four Flash',
                    'fingerprint': 'Under-display',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '33W Super Charge',
                    'charging_port': 'Type-C',
                    'loudspeaker': 'Stereo Dual Speakers, Dolby Atmos, Hi-Res Audio',
                    'infrared_remote': 'Supported',
                    'nfc': 'Supported',
                    'water_resistance': 'IP54 Rating',
                    'touch_control': 'Wet Touch Control',
                    'memory_options': [
                        '128GB ROM+16GB RAM*(8GB+8GB Extended)',
                        '256GB ROM+16GB RAM*(8GB+8GB Extended)'
                    ]
                },
                'colors': ['Lueur Arctique', 'Bordure Obsidienne'],
                'storage_options': [128, 256],
                'ram_options': [16]
            },
            # SPARK 30 5G - Spécifications exactes fournies
            {
                'model': 'SPARK 30 5G',
                'title': 'TECNO SPARK 30 5G',
                'description': 'Smartphone 5G avec processeur Dimensity 6300, caméra 108MP et connectivité ultra-rapide',
                'price': 110000,
                'specifications': {
                    'operating_system': 'Android 14',
                    'processor': 'MediaTek Dimensity 6300 5G',
                    'network': ['2G', '3G', '4G', '5G'],
                    'dimension': '165.62x77.01x8.35 mm',
                    'display': '120Hz 6.67" HD+ Hole Screen',
                    'resolution': '720*1600',
                    'camera_front': '8MP, Front Dual Colour Temperature Flash',
                    'camera_main': '108MP, Rear Triple Flash',
                    'fingerprint': 'Side-mounted',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '18W Fast Charge',
                    'charging_port': 'Type-C',
                    'loudspeaker': 'Stereo Dual Speakers, Dolby Atmos, Hi-Res Audio',
                    'infrared_remote': 'Supported',
                    'nfc': 'Supported',
                    'water_resistance': 'IP54 Rating',
                    'touch_control': 'Wet & Oily Touch Control',
                    'memory_options': [
                        '128GB ROM+12GB RAM*(6GB+6GB Extended)',
                        '256GB ROM+16GB RAM*(8GB+8GB Extended)'
                    ]
                },
                'colors': ['Ombre de Minuit', 'Nuage d\'Aurore', 'Ciel Azur'],
                'storage_options': [128, 256],
                'ram_options': [12, 16]
            },
            # SPARK 30C - Spécifications exactes fournies
            {
                'model': 'SPARK 30C',
                'title': 'TECNO SPARK 30C',
                'description': 'Smartphone avec écran 6.67" 120Hz, caméra 50MP et processeur G81',
                'price': 85000,
                'specifications': {
                    'operating_system': 'Android 14',
                    'processor': 'G81',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '165.62x77.01x8.35 mm',
                    'display': '120Hz 6.67" Hole Screen',
                    'resolution': '720*1600',
                    'camera_front': '8MP, Front Dual Flash',
                    'camera_main': '50MP, Rear Dual Flash',
                    'fingerprint': 'Side-mounted',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '18W Fast Charge',
                    'charging_port': 'Type-C',
                    'loudspeaker': 'Dual Symmetrical Speakers, DTS Sound',
                    'infrared_remote': 'Supported',
                    'water_resistance': 'IP54 Rating',
                    'touch_control': 'Wet & Oily Touch Control',
                    'memory_options': [
                        '128GB ROM+8GB RAM*(4GB+4GB Extended)',
                        '128GB ROM+12GB RAM*(6GB+6GB Extended)',
                        '256GB ROM+8GB RAM*(4GB+4GB Extended)',
                        '256GB ROM+16GB RAM*(8GB+8GB Extended)'
                    ]
                },
                'colors': ['Noir Orbite', 'Blanc Orbite', 'Peau Magique 3.0'],
                'storage_options': [128, 256],
                'ram_options': [8, 12, 16]
            },
            # SPARK 30C 5G - Spécifications exactes fournies
            {
                'model': 'SPARK 30C 5G',
                'title': 'TECNO SPARK 30C 5G',
                'description': 'Smartphone 5G économique avec processeur Dimensity 6300, caméra 48MP et connectivité ultra-rapide',
                'price': 95000,
                'specifications': {
                    'operating_system': 'Android 14',
                    'processor': 'MediaTek Dimensity 6300 5G',
                    'network': ['2G', '3G', '4G', '5G'],
                    'dimension': '165.62x77.01x8.35 mm',
                    'display': '120Hz 6.67" HD+ Hole Screen',
                    'resolution': '720*1600',
                    'camera_front': '8MP, Front Dual Flash',
                    'camera_main': '48MP, Rear Triple Flash',
                    'fingerprint': 'Side-mounted',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '18W Fast Charge',
                    'charging_port': 'Type-C',
                    'loudspeaker': 'Stereo Dual Speakers, Dolby Atmos, Hi-Res Audio',
                    'infrared_remote': 'Supported',
                    'nfc': 'Supported',
                    'water_resistance': 'IP54 Rating',
                    'touch_control': 'Wet & Oily Touch Control',
                    'memory_options': [
                        '64GB ROM+8GB RAM*(4GB+4GB Extended)',
                        '128GB ROM+8GB RAM*(4GB+4GB Extended)'
                    ]
                },
                'colors': ['Ombre de Minuit', 'Nuage d\'Aurore', 'Ciel Azur'],
                'storage_options': [64, 128],
                'ram_options': [8]
            },
            # SPARK 40 - Spécifications exactes fournies
            {
                'model': 'SPARK 40',
                'title': 'TECNO SPARK 40',
                'description': 'Smartphone premium avec Android 15, processeur Helio G81 et charge ultra-rapide 45W',
                'price': 130000,
                'specifications': {
                    'operating_system': 'Android 15',
                    'processor': 'Helio G81',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '165.6x77x7.67mm',
                    'display': '120Hz 6.67" Hole Screen',
                    'resolution': '720*1600',
                    'camera_front': '8MP, Front Dual Flash',
                    'camera_main': '50MP, Rear Dual Flash',
                    'sensor': 'Software Gyroscope, Side Fingerprint Sensor, Infrared Remote Control',
                    'connectivity': ['GPS', 'WiFi', 'BT', 'FM', 'OTG'],
                    'battery_capacity': '5200mAh',
                    'fast_charge': '45W Super Charging',
                    'charging_port': 'Type-C',
                    'loudspeaker': 'Dual Speakers, DTS Sound',
                    'memory_options': [
                        '128GB+8GB*(4GB Extended RAM)',
                        '128GB+12GB*(6GB Extended RAM)',
                        '256GB+8GB*(4GB Extended RAM)',
                        '256GB+16GB*(8GB Extended RAM)'
                    ]
                },
                'colors': ['Noir Encre', 'Gris Titane', 'Blanc Voile', 'Bleu Mirage'],
                'storage_options': [128, 256],
                'ram_options': [8, 12, 16]
            },
            # SPARK 40 Pro - Spécifications exactes fournies
            {
                'model': 'SPARK 40 Pro',
                'title': 'TECNO SPARK 40 Pro',
                'description': 'Smartphone ultra-premium avec écran AMOLED 6.78" 144Hz, processeur Helio 100 Ultimate et Dolby Atmos',
                'price': 160000,
                'specifications': {
                    'operating_system': 'Android 15',
                    'processor': 'MediaTek Helio 100 Ultimate',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '163.67x75.87x6.69mm',
                    'display': '144Hz 6.78" AMOLED Flexible Display',
                    'resolution': '1224*2720',
                    'camera_front': '13MP, Front Dual Flash',
                    'camera_main': '50MP, Rear Dual Flash',
                    'sensor': 'Software Gyroscope, Infrared Remote Control',
                    'connectivity': ['GPS', 'WiFi', 'BT', 'FM', 'OTG', 'NFC'],
                    'battery_capacity': '5200mAh',
                    'fast_charge': '45W Super Charging',
                    'charging_port': 'Type-C',
                    'loudspeaker': 'Dual Speakers, Dolby Atmos',
                    'memory_options': [
                        '128GB+16GB*(8GB Extended RAM)',
                        '256GB+16GB*(8GB Extended RAM)'
                    ]
                },
                'colors': ['Noir Encre', 'Titane Lunaire', 'Bleu Lac', 'Vert Bambou'],
                'storage_options': [128, 256],
                'ram_options': [16]
            },
            # SPARK 40 Pro+ - Spécifications exactes fournies
            {
                'model': 'SPARK 40 Pro+',
                'title': 'TECNO SPARK 40 Pro+',
                'description': 'Smartphone ultra-premium avec écran 3D AMOLED 6.78" 144Hz, processeur Helio G200 et charge sans fil',
                'price': 180000,
                'specifications': {
                    'operating_system': 'Android 15',
                    'processor': 'MediaTek Helio G200',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '163.9x75.8x6.49mm',
                    'display': '6.78" 144Hz&1.5K 3D AMOLED Display',
                    'resolution': '1224*2720',
                    'camera_front': '13MP, Front Dual Flash',
                    'camera_main': '50MP, Rear Dual Flash',
                    'sensor': 'Physical Gyroscope, Infrared Remote Control',
                    'connectivity': ['GPS', 'WiFi', 'BT', 'FM', 'OTG', 'NFC'],
                    'battery_capacity': '5200mAh',
                    'fast_charge': '45W Super Charging',
                    'wireless_charge': '30W Wireless Charging',
                    'reverse_wireless': '5W Reverse Wireless Charging',
                    'charging_port': 'Type-C',
                    'loudspeaker': 'Dual Speakers, Dolby Atmos',
                    'memory_options': [
                        '128GB+16GB*(8GB Extended RAM)',
                        '256GB+16GB*(8GB Extended RAM)'
                    ]
                },
                'colors': ['Noir Nébuleuse', 'Blanc Aurore', 'Titane Lunaire', 'Vert Toundra'],
                'storage_options': [128, 256],
                'ram_options': [16]
            },
            # SPARK 40C - Spécifications exactes fournies
            {
                'model': 'SPARK 40C',
                'title': 'TECNO SPARK 40C',
                'description': 'Smartphone économique avec Android 15, processeur Helio G81 et batterie 6000mAh',
                'price': 110000,
                'specifications': {
                    'operating_system': 'Android 15',
                    'processor': 'Helio G81',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '165.6x77x8.37mm',
                    'display': '120Hz 6.67" Hole Screen',
                    'resolution': '720*1600',
                    'camera_front': '8MP, Front Dual Flash',
                    'camera_main': '13MP, Rear Dual Flash',
                    'sensor': 'Software Gyroscope, Side Fingerprint Sensor, Infrared Remote Control',
                    'connectivity': ['GPS', 'WiFi', 'BT', 'FM', 'OTG'],
                    'battery_capacity': '6000mAh',
                    'fast_charge': '18W Fast Charging',
                    'charging_port': 'Type-C',
                    'loudspeaker': 'Dual Speakers, DTS Sound',
                    'memory_options': [
                        '128GB+8GB*(4GB Extended RAM)',
                        '128GB+16GB*(8GB Extended RAM)',
                        '256GB+16GB*(8GB Extended RAM)'
                    ]
                },
                'colors': ['Blanc Voile', 'Bleu Ondulation', 'Gris Titane', 'Noir Encre'],
                'storage_options': [128, 256],
                'ram_options': [8, 16]
            },
            # SPARK Go 2 - Spécifications exactes fournies
            {
                'model': 'SPARK Go 2',
                'title': 'TECNO SPARK Go 2',
                'description': 'Smartphone d\'entrée de gamme avec Android 15, processeur T7250 et écran 120Hz',
                'price': 52000,
                'specifications': {
                    'operating_system': 'Android 15',
                    'processor': 'T7250',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '165.6x77x8.25mm',
                    'display': '120Hz 6.67" Hole Screen',
                    'resolution': '720*1600',
                    'camera_front': '8MP, Front Dual Flash',
                    'camera_main': '13MP, Rear Dual Flash',
                    'sensor': 'Software Gyroscope, Side Fingerprint Sensor, Infrared Remote Control',
                    'connectivity': ['GPS', 'WiFi', 'BT', 'FM', 'OTG'],
                    'battery_capacity': '5000mAh',
                    'fast_charge': '15W Fast Charging',
                    'charging_port': 'Type-C',
                    'loudspeaker': 'Dual Speakers, DTS Sound',
                    'memory_options': [
                        '64GB ROM+6GB RAM*(3GB+3GB Extended)',
                        '64GB ROM+8GB RAM*(4GB+4GB Extended)',
                        '128GB ROM+6GB RAM*(3GB+3GB Extended)',
                        '128GB ROM+8GB RAM*(4GB+4GB Extended)',
                        '256GB ROM+8GB RAM*(4GB+4GB Extended)'
                    ]
                },
                'colors': ['Noir Encre', 'Gris Titane', 'Blanc Voile', 'Vert Turquoise'],
                'storage_options': [64, 128, 256],
                'ram_options': [6, 8]
            },
            # SPARK 10 Series
            {
                'model': 'SPARK 10',
                'title': 'TECNO SPARK 10',
                'description': 'Smartphone avec écran 6.6" et caméra 50MP',
                'price': 65000,
                'specifications': {
                    'operating_system': 'Android 13',
                    'processor': 'Helio G37',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '163.1x75.6x8.4 mm',
                    'display': '6.6" HD+ Dot-in Display',
                    'resolution': '1612x720',
                    'camera_front': '8MP',
                    'camera_main': '50MP + 2MP + AI Lens',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '18W Fast Charge',
                    'charging_port': 'Type-C',
                    'memory_options': [
                        '64GB ROM+4GB RAM',
                        '128GB ROM+8GB RAM'
                    ]
                },
                'colors': ['Noir', 'Blanc', 'Bleu'],
                'storage_options': [64, 128],
                'ram_options': [4, 8]
            },
            {
                'model': 'SPARK 10C',
                'title': 'TECNO SPARK 10C',
                'description': 'Version économique du SPARK 10 avec écran 6.6"',
                'price': 55000,
                'specifications': {
                    'operating_system': 'Android 13',
                    'processor': 'Helio G37',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '163.1x75.6x8.4 mm',
                    'display': '6.6" HD+ Dot-in Display',
                    'resolution': '1612x720',
                    'camera_front': '8MP',
                    'camera_main': '50MP + 2MP + AI Lens',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '18W Fast Charge',
                    'charging_port': 'Type-C',
                    'memory_options': [
                        '64GB ROM+4GB RAM',
                        '128GB ROM+8GB RAM'
                    ]
                },
                'colors': ['Noir', 'Blanc', 'Vert'],
                'storage_options': [64, 128],
                'ram_options': [4, 8]
            },
            {
                'model': 'SPARK 10 Pro',
                'title': 'TECNO SPARK 10 Pro',
                'description': 'Version Pro avec écran 6.8" et caméra 108MP',
                'price': 85000,
                'specifications': {
                    'operating_system': 'Android 13',
                    'processor': 'Helio G99',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '168.6x76.6x8.4 mm',
                    'display': '6.8" FHD+ AMOLED Display',
                    'resolution': '2400x1080',
                    'camera_front': '32MP',
                    'camera_main': '108MP + 2MP + 2MP',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '33W Fast Charge',
                    'charging_port': 'Type-C',
                    'memory_options': [
                        '128GB ROM+8GB RAM',
                        '256GB ROM+8GB RAM'
                    ]
                },
                'colors': ['Noir', 'Blanc', 'Bleu'],
                'storage_options': [128, 256],
                'ram_options': [8]
            },
            # SPARK 20 Series
            {
                'model': 'SPARK 20',
                'title': 'TECNO SPARK 20',
                'description': 'Nouvelle génération avec écran 6.6" et caméra 50MP',
                'price': 75000,
                'specifications': {
                    'operating_system': 'Android 14',
                    'processor': 'Helio G85',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '163.7x75.6x8.5 mm',
                    'display': '6.6" HD+ Dot-in Display',
                    'resolution': '1612x720',
                    'camera_front': '32MP',
                    'camera_main': '50MP + 2MP + AI Lens',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '18W Fast Charge',
                    'charging_port': 'Type-C',
                    'memory_options': [
                        '128GB ROM+8GB RAM',
                        '256GB ROM+8GB RAM'
                    ]
                },
                'colors': ['Noir', 'Blanc', 'Bleu', 'Vert'],
                'storage_options': [128, 256],
                'ram_options': [8]
            },
            {
                'model': 'SPARK 20C',
                'title': 'TECNO SPARK 20C',
                'description': 'Version économique du SPARK 20',
                'price': 65000,
                'specifications': {
                    'operating_system': 'Android 14',
                    'processor': 'Helio G85',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '163.7x75.6x8.5 mm',
                    'display': '6.6" HD+ Dot-in Display',
                    'resolution': '1612x720',
                    'camera_front': '32MP',
                    'camera_main': '50MP + 2MP + AI Lens',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '18W Fast Charge',
                    'charging_port': 'Type-C',
                    'memory_options': [
                        '128GB ROM+8GB RAM'
                    ]
                },
                'colors': ['Noir', 'Blanc', 'Bleu'],
                'storage_options': [128],
                'ram_options': [8]
            },
            {
                'model': 'SPARK 20 Pro',
                'title': 'TECNO SPARK 20 Pro',
                'description': 'Version Pro avec écran 6.78" et caméra 108MP',
                'price': 95000,
                'specifications': {
                    'operating_system': 'Android 14',
                    'processor': 'Helio G99',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '168.6x76.6x8.4 mm',
                    'display': '6.78" FHD+ AMOLED Display',
                    'resolution': '2436x1080',
                    'camera_front': '32MP',
                    'camera_main': '108MP + 2MP + 2MP',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '33W Fast Charge',
                    'charging_port': 'Type-C',
                    'memory_options': [
                        '256GB ROM+8GB RAM'
                    ]
                },
                'colors': ['Noir', 'Blanc', 'Bleu', 'Vert'],
                'storage_options': [256],
                'ram_options': [8]
            },
            {
                'model': 'SPARK 20C+',
                'title': 'TECNO SPARK 20C+',
                'description': 'Version améliorée du SPARK 20C',
                'price': 70000,
                'specifications': {
                    'operating_system': 'Android 14',
                    'processor': 'Helio G85',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '163.7x75.6x8.5 mm',
                    'display': '6.6" HD+ Dot-in Display',
                    'resolution': '1612x720',
                    'camera_front': '32MP',
                    'camera_main': '50MP + 2MP + AI Lens',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '18W Fast Charge',
                    'charging_port': 'Type-C',
                    'memory_options': [
                        '128GB ROM+8GB RAM',
                        '256GB ROM+8GB RAM'
                    ]
                },
                'colors': ['Noir', 'Blanc', 'Bleu'],
                'storage_options': [128, 256],
                'ram_options': [8]
            },
            {
                'model': 'SPARK 20C Pro',
                'title': 'TECNO SPARK 20C Pro',
                'description': 'Version Pro du SPARK 20C',
                'price': 80000,
                'specifications': {
                    'operating_system': 'Android 14',
                    'processor': 'Helio G99',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '168.6x76.6x8.4 mm',
                    'display': '6.78" FHD+ AMOLED Display',
                    'resolution': '2436x1080',
                    'camera_front': '32MP',
                    'camera_main': '108MP + 2MP + 2MP',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '33W Fast Charge',
                    'charging_port': 'Type-C',
                    'memory_options': [
                        '256GB ROM+8GB RAM'
                    ]
                },
                'colors': ['Noir', 'Blanc', 'Bleu'],
                'storage_options': [256],
                'ram_options': [8]
            },
            {
                'model': 'SPARK 20C+ Pro',
                'title': 'TECNO SPARK 20C+ Pro',
                'description': 'Version Pro du SPARK 20C+',
                'price': 85000,
                'specifications': {
                    'operating_system': 'Android 14',
                    'processor': 'Helio G99',
                    'network': ['2G', '3G', '4G'],
                    'dimension': '168.6x76.6x8.4 mm',
                    'display': '6.78" FHD+ AMOLED Display',
                    'resolution': '2436x1080',
                    'camera_front': '32MP',
                    'camera_main': '108MP + 2MP + 2MP',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '33W Fast Charge',
                    'charging_port': 'Type-C',
                    'memory_options': [
                        '256GB ROM+8GB RAM'
                    ]
                },
                'colors': ['Noir', 'Blanc', 'Bleu'],
                'storage_options': [256],
                'ram_options': [8]
            },
            # SPARK 20 5G Series
            {
                'model': 'SPARK 20C+ 5G',
                'title': 'TECNO SPARK 20C+ 5G',
                'description': 'Version 5G du SPARK 20C+',
                'price': 90000,
                'specifications': {
                    'operating_system': 'Android 14',
                    'processor': 'Dimensity 6100+',
                    'network': ['2G', '3G', '4G', '5G'],
                    'dimension': '163.7x75.6x8.5 mm',
                    'display': '6.6" HD+ Dot-in Display',
                    'resolution': '1612x720',
                    'camera_front': '32MP',
                    'camera_main': '50MP + 2MP + AI Lens',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '18W Fast Charge',
                    'charging_port': 'Type-C',
                    'memory_options': [
                        '128GB ROM+8GB RAM',
                        '256GB ROM+8GB RAM'
                    ]
                },
                'colors': ['Noir', 'Blanc', 'Bleu'],
                'storage_options': [128, 256],
                'ram_options': [8]
            },
            {
                'model': 'SPARK 20C Pro 5G',
                'title': 'TECNO SPARK 20C Pro 5G',
                'description': 'Version 5G Pro du SPARK 20C',
                'price': 100000,
                'specifications': {
                    'operating_system': 'Android 14',
                    'processor': 'Dimensity 6100+',
                    'network': ['2G', '3G', '4G', '5G'],
                    'dimension': '168.6x76.6x8.4 mm',
                    'display': '6.78" FHD+ AMOLED Display',
                    'resolution': '2436x1080',
                    'camera_front': '32MP',
                    'camera_main': '108MP + 2MP + 2MP',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '33W Fast Charge',
                    'charging_port': 'Type-C',
                    'memory_options': [
                        '256GB ROM+8GB RAM'
                    ]
                },
                'colors': ['Noir', 'Blanc', 'Bleu'],
                'storage_options': [256],
                'ram_options': [8]
            },
            {
                'model': 'SPARK 20C+ Pro 5G',
                'title': 'TECNO SPARK 20C+ Pro 5G',
                'description': 'Version 5G Pro du SPARK 20C+',
                'price': 105000,
                'specifications': {
                    'operating_system': 'Android 14',
                    'processor': 'Dimensity 6100+',
                    'network': ['2G', '3G', '4G', '5G'],
                    'dimension': '168.6x76.6x8.4 mm',
                    'display': '6.78" FHD+ AMOLED Display',
                    'resolution': '2436x1080',
                    'camera_front': '32MP',
                    'camera_main': '108MP + 2MP + 2MP',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '33W Fast Charge',
                    'charging_port': 'Type-C',
                    'memory_options': [
                        '256GB ROM+8GB RAM'
                    ]
                },
                'colors': ['Noir', 'Blanc', 'Bleu'],
                'storage_options': [256],
                'ram_options': [8]
            },
            {
                'model': 'SPARK 20C+ 5G Pro',
                'title': 'TECNO SPARK 20C+ 5G Pro',
                'description': 'Version 5G Pro alternative du SPARK 20C+',
                'price': 110000,
                'specifications': {
                    'operating_system': 'Android 14',
                    'processor': 'Dimensity 6100+',
                    'network': ['2G', '3G', '4G', '5G'],
                    'dimension': '168.6x76.6x8.4 mm',
                    'display': '6.78" FHD+ AMOLED Display',
                    'resolution': '2436x1080',
                    'camera_front': '32MP',
                    'camera_main': '108MP + 2MP + 2MP',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '33W Fast Charge',
                    'charging_port': 'Type-C',
                    'memory_options': [
                        '256GB ROM+8GB RAM'
                    ]
                },
                'colors': ['Noir', 'Blanc', 'Bleu'],
                'storage_options': [256],
                'ram_options': [8]
            },
            {
                'model': 'SPARK 20C+ 5G Pro Max',
                'title': 'TECNO SPARK 20C+ 5G Pro Max',
                'description': 'Version ultime 5G Pro Max du SPARK 20C+',
                'price': 120000,
                'specifications': {
                    'operating_system': 'Android 14',
                    'processor': 'Dimensity 6100+',
                    'network': ['2G', '3G', '4G', '5G'],
                    'dimension': '168.6x76.6x8.4 mm',
                    'display': '6.78" FHD+ AMOLED Display',
                    'resolution': '2436x1080',
                    'camera_front': '32MP',
                    'camera_main': '108MP + 2MP + 2MP',
                    'battery_capacity': '5000mAh',
                    'fast_charge': '33W Fast Charge',
                    'charging_port': 'Type-C',
                    'memory_options': [
                        '256GB ROM+8GB RAM'
                    ]
                },
                'colors': ['Noir', 'Blanc', 'Bleu'],
                'storage_options': [256],
                'ram_options': [8]
            }
        ]
        
        total_created = 0
        total_existing = 0
        
        with transaction.atomic():
            for model_data in spark_models:
                self.stdout.write(f'\n📱 {model_data["model"]}:')
                
                for storage in model_data['storage_options']:
                    for ram in model_data['ram_options']:
                        for color_name in model_data['colors']:
                            try:
                                # Récupérer la couleur
                                try:
                                    color = Color.objects.get(name__iexact=color_name)
                                except Color.DoesNotExist:
                                    self.stdout.write(f'  ⚠️ Couleur "{color_name}" non trouvée, utilisation de la couleur par défaut')
                                    color = Color.objects.first()  # Couleur par défaut
                                
                                # Créer le titre avec les spécifications
                                title = f"{model_data['title']} {storage}GB/{ram}GB {color_name}"
                                slug = f"tecno-spark-{model_data['model'].lower().replace(' ', '-')}-{storage}gb-{ram}gb-{color_name.lower().replace(' ', '-')}"
                                
                                # Vérifier si le produit existe déjà
                                existing_product = Product.objects.filter(slug=slug).first()
                                
                                if existing_product:
                                    self.stdout.write(f'  ℹ️ Produit déjà existant: {title}')
                                    total_existing += 1
                                    continue
                                
                                if not dry_run:
                                    # Créer le produit
                                    product = Product.objects.create(
                                        title=title,
                                        slug=slug,
                                        description=model_data['description'],
                                        price=Decimal(model_data['price']),
                                        category=phone_category,
                                        supplier=tecno_supplier,
                                        brand=normalized_brand,
                                        is_available=True,
                                        stock=10,
                                        specifications=model_data['specifications'],
                                        weight=Decimal('0.18'),  # 180g approximatif
                                        dimensions='165x75x8.5mm'
                                    )
                                    
                                    # Créer le téléphone
                                    phone = Phone.objects.create(
                                        product=product,
                                        brand=normalized_brand,
                                        model=model_data['model'],
                                        operating_system=model_data['specifications']['operating_system'],
                                        screen_size=Decimal('6.6'),
                                        resolution=model_data['specifications']['resolution'],
                                        processor=model_data['specifications']['processor'],
                                        battery_capacity=5000,
                                        camera_main=model_data['specifications']['camera_main'],
                                        camera_front=model_data['specifications']['camera_front'],
                                        network=model_data['specifications']['network'][-1],  # Prendre le plus récent
                                        storage=storage,
                                        ram=ram,
                                        color=color,
                                        is_new=True,
                                        box_included=True,
                                        accessories='Chargeur Type-C, Câble USB, Coque de protection, Écouteurs'
                                    )
                                    
                                    self.stdout.write(f'  ✅ Créé: {title} ({color_name})')
                                    total_created += 1
                                else:
                                    self.stdout.write(f'  📋 [DRY-RUN] Serait créé: {title} ({color_name})')
                                    total_created += 1
                                    
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f'  ❌ Erreur avec {title}: {str(e)}'))
                                logger.error(f'Erreur lors de la création du téléphone {title}: {str(e)}')
                                continue
        
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(f'📊 Résumé DRY-RUN: {total_created} téléphones seraient créés')
        else:
            self.stdout.write(f'✅ Résumé: {total_created} téléphones créés, {total_existing} déjà existants')
        self.stdout.write('📱 Ajout des téléphones TECNO SPARK terminé !') 