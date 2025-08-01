from django.core.management.base import BaseCommand
from product.models import Phone, Color, Category, Product
from django.utils.text import slugify
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Ajoute les téléphones TECNO CAMON 30S Pro avec normalisation des marques'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Début de l\'ajout des téléphones TECNO CAMON 30S Pro...')
        
        # Normalisation des marques TECNO
        self.stdout.write('🔧 Normalisation des marques TECNO...')
        phones_to_update = Phone.objects.filter(
            Q(brand__icontains='TECNO') | 
            Q(brand__icontains='Tecno') | 
            Q(brand__icontains='tecnocamon')
        )
        
        updated_count = 0
        for phone in phones_to_update:
            if phone.brand != 'TECNO':
                old_brand = phone.brand
                phone.brand = 'TECNO'
                phone.save()
                self.stdout.write(f'✅ Marque normalisée: {old_brand} → TECNO')
                updated_count += 1
        
        self.stdout.write(f'🔧 {updated_count} marques TECNO normalisées')
        
        try:
            category = Category.objects.get(name='Téléphones')
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Catégorie "Téléphones" non trouvée'))
            return
        
        # Données des téléphones TECNO CAMON 30S Pro
        phones_data = [
            {
                'title': 'TECNO CAMON 30S Pro 256GB 16GB Gris Interstellaire',
                'rom': 256,
                'ram': 16,
                'color_name': 'Gris Interstellaire',
                'color_hex': '#2c3e50',
                'price': 185000,
                'stock': 15,
                'sku': 'TECNO-CAMON30SPRO-256-16-GREY'
            },
            {
                'title': 'TECNO CAMON 30S Pro 256GB 16GB Or Perle',
                'rom': 256,
                'ram': 16,
                'color_name': 'Or Perle',
                'color_hex': '#f4e4bc',
                'price': 185000,
                'stock': 12,
                'sku': 'TECNO-CAMON30SPRO-256-16-GOLD'
            },
            {
                'title': 'TECNO CAMON 30S Pro 256GB 16GB Vert Argent Shim',
                'rom': 256,
                'ram': 16,
                'color_name': 'Vert Argent Shim',
                'color_hex': '#90ee90',
                'price': 185000,
                'stock': 10,
                'sku': 'TECNO-CAMON30SPRO-256-16-GREEN'
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for phone_data in phones_data:
            try:
                color, color_created = Color.objects.get_or_create(
                    name=phone_data['color_name'],
                    defaults={'code': phone_data['color_hex']}
                )
                
                if color_created:
                    self.stdout.write(f'✅ Couleur créée: {color.name} ({color.code})')
                
                product, product_created = Product.objects.get_or_create(
                    title=phone_data['title'],
                    defaults={
                        'category': category,
                        'price': phone_data['price'],
                        'stock': phone_data['stock'],
                        'sku': phone_data['sku'],
                        'slug': slugify(phone_data['title']),
                        'brand': 'TECNO',
                        'is_available': True,
                        'condition': 'new'
                    }
                )
                
                if product_created:
                    self.stdout.write(f'✅ Produit créé: {product.title}')
                else:
                    product.price = phone_data['price']
                    product.stock = phone_data['stock']
                    product.sku = phone_data['sku']
                    product.save()
                    self.stdout.write(f'🔄 Produit mis à jour: {product.title}')
                
                phone, phone_created = Phone.objects.get_or_create(
                    product=product,
                    defaults={
                        'brand': 'TECNO',
                        'model': 'CAMON 30S Pro',
                        'operating_system': 'Android 14',
                        'processor': 'Helio G100 Octa-Core',
                        'network': '2G, 3G, 4G',
                        'screen_size': 6.78,
                        'resolution': '1080 x 2436',
                        'camera_front': '50 MP AF, Front Dual Flash',
                        'camera_main': '50 MP 1/1.56" OIS + 2 MP Depth + Light Sensor, Dual Flash',
                        'battery_capacity': 5000,
                        'storage': phone_data['rom'],
                        'ram': phone_data['ram'],
                        'color': color,
                        'is_new': True,
                        'box_included': True,
                        'accessories': 'Chargeur 45W, Câble Type-C, Coque de protection, Écouteurs'
                    }
                )
                
                if phone_created:
                    self.stdout.write(f'✅ Téléphone créé: {phone.product.title}')
                    created_count += 1
                else:
                    phone.color = color
                    phone.storage = phone_data['rom']
                    phone.ram = phone_data['ram']
                    phone.save()
                    self.stdout.write(f'🔄 Téléphone mis à jour: {phone.product.title}')
                    updated_count += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erreur avec {phone_data["title"]}: {str(e)}'))
        
        self.stdout.write(f'\n📱 Résumé: {created_count} téléphones créés, {updated_count} mis à jour')
        self.stdout.write(self.style.SUCCESS('✅ Ajout des téléphones TECNO CAMON 30S Pro terminé !'))
        
        self.stdout.write('\n📋 Spécifications techniques ajoutées :')
        self.stdout.write('• Système d\'exploitation : Android 14')
        self.stdout.write('• Processeur : Helio G100 Octa-Core')
        self.stdout.write('• Écran : 6.78" FHD+ AMOLED 120Hz')
        self.stdout.write('• Caméra frontale : 50 MP AF avec Flash Double')
        self.stdout.write('• Caméra principale : 50 MP OIS + 2 MP Depth + Light Sensor')
        self.stdout.write('• Batterie : 5000 mAh avec charge 45W')
        self.stdout.write('• Connectivité : GNSS, WiFi, FM, BT, OTG, GPS, NFC')
        self.stdout.write('• Capteurs : G-sensor, Ambient Light, Proximity, Compass, Gyroscope, Infrared') 