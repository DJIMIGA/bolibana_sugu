from django.core.management.base import BaseCommand
from product.models import Phone, Color, Category
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Ajoute les téléphones TECNO CAMON 40 Pro (version standard)'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Début de l\'ajout des téléphones TECNO CAMON 40 Pro...')
        
        # Récupérer la catégorie Téléphones
        try:
            category = Category.objects.get(name='Téléphones')
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Catégorie "Téléphones" non trouvée'))
            return
        
        # Données des téléphones TECNO CAMON 40 Pro
        phones_data = [
            {
                'title': 'TECNO CAMON 40 Pro 256GB 16GB Noir Galaxy',
                'rom': 256,
                'ram': 16,
                'color_name': 'Noir Galaxy',
                'color_hex': '#000000',
                'price': 185000,
                'stock': 15,
                'sku': 'TECNO-CAMON40PRO-256-16-BLACK'
            },
            {
                'title': 'TECNO CAMON 40 Pro 256GB 16GB Vert Émeraude',
                'rom': 256,
                'ram': 16,
                'color_name': 'Vert Émeraude',
                'color_hex': '#00a86b',
                'price': 185000,
                'stock': 12,
                'sku': 'TECNO-CAMON40PRO-256-16-GREEN'
            },
            {
                'title': 'TECNO CAMON 40 Pro 256GB 16GB Blanc Glacier',
                'rom': 256,
                'ram': 16,
                'color_name': 'Blanc Glacier',
                'color_hex': '#f8f8ff',
                'price': 185000,
                'stock': 10,
                'sku': 'TECNO-CAMON40PRO-256-16-WHITE'
            },
            {
                'title': 'TECNO CAMON 40 Pro 256GB 16GB Titanium Sable',
                'rom': 256,
                'ram': 16,
                'color_name': 'Titanium Sable',
                'color_hex': '#c0c0c0',
                'price': 185000,
                'stock': 8,
                'sku': 'TECNO-CAMON40PRO-256-16-TITANIUM'
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for phone_data in phones_data:
            try:
                # Créer ou récupérer la couleur
                color, color_created = Color.objects.get_or_create(
                    name=phone_data['color_name'],
                    defaults={'hex_code': phone_data['color_hex']}
                )
                
                if color_created:
                    self.stdout.write(f'✅ Couleur créée: {color.name} ({color.hex_code})')
                
                # Créer ou mettre à jour le téléphone
                phone, created = Phone.objects.get_or_create(
                    title=phone_data['title'],
                    defaults={
                        'category': category,
                        'color': color,
                        'rom': phone_data['rom'],
                        'ram': phone_data['ram'],
                        'price': phone_data['price'],
                        'stock': phone_data['stock'],
                        'sku': phone_data['sku'],
                        'slug': slugify(phone_data['title']),
                        'brand': 'TECNO',
                        'model': 'CAMON 40 Pro',
                        'operating_system': 'Android 15',
                        'processor': 'MediaTek Helio G100 Ultimate Processor',
                        'network': '2G, 3G, 4G',
                        'dimensions': '164.44 x 74.32 x 7.31 mm',
                        'display': '6.78" AMOLED 120 Hz',
                        'resolution': '1080 x 2436',
                        'camera_front': '50 MP AF',
                        'camera_rear': '50 MP 1/1.56" OIS + 8 MP Wide-angle, Dual Flash, Flicker Sensor',
                        'connectivity': 'Wi-Fi, BT, FM, GPS, NFC, Type-C Port, OTG',
                        'sensors': 'Geomagnetic Sensor, A+G Sensor, Ambient light and distance sensor, Infrared Remote Control, Electronic compass',
                        'battery': '5200 mAh, 45W Super Charge',
                        'loudspeaker': 'Dual Speakers, Dolby Atmos',
                        'is_available': True,
                        'condition': 'new'
                    }
                )
                
                if created:
                    self.stdout.write(f'✅ Téléphone créé: {phone.title}')
                    created_count += 1
                else:
                    # Mettre à jour les informations existantes
                    phone.color = color
                    phone.rom = phone_data['rom']
                    phone.ram = phone_data['ram']
                    phone.price = phone_data['price']
                    phone.stock = phone_data['stock']
                    phone.sku = phone_data['sku']
                    phone.save()
                    self.stdout.write(f'🔄 Téléphone mis à jour: {phone.title}')
                    updated_count += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erreur avec {phone_data["title"]}: {str(e)}'))
        
        self.stdout.write(f'\n📱 Résumé: {created_count} téléphones créés, {updated_count} mis à jour')
        self.stdout.write(self.style.SUCCESS('✅ Ajout des téléphones TECNO CAMON 40 Pro terminé !')) 