from django.core.management.base import BaseCommand
from product.models import Phone, Color, Category, Product
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Ajoute les téléphones TECNO CAMON 40 (version standard)'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Début de l\'ajout des téléphones TECNO CAMON 40...')
        
        # Récupérer la catégorie Téléphones
        try:
            category = Category.objects.get(name='Téléphones')
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Catégorie "Téléphones" non trouvée'))
            return
        
        # Données des téléphones TECNO CAMON 40
        phones_data = [
            # Variantes 256GB
            {
                'title': 'TECNO CAMON 40 256GB 16GB Noir Galaxy',
                'rom': 256,
                'ram': 16,
                'color_name': 'Noir Galaxy',
                'color_hex': '#000000',
                'price': 175000,
                'stock': 20,
                'sku': 'TECNO-CAMON40-256-16-BLACK'
            },
            {
                'title': 'TECNO CAMON 40 256GB 16GB Vert Émeraude',
                'rom': 256,
                'ram': 16,
                'color_name': 'Vert Émeraude',
                'color_hex': '#00a86b',
                'price': 175000,
                'stock': 18,
                'sku': 'TECNO-CAMON40-256-16-GREEN'
            },
            {
                'title': 'TECNO CAMON 40 256GB 16GB Blanc Glacier',
                'rom': 256,
                'ram': 16,
                'color_name': 'Blanc Glacier',
                'color_hex': '#f8f8ff',
                'price': 175000,
                'stock': 15,
                'sku': 'TECNO-CAMON40-256-16-WHITE'
            },
            {
                'title': 'TECNO CAMON 40 256GB 16GB Titanium Sable',
                'rom': 256,
                'ram': 16,
                'color_name': 'Titanium Sable',
                'color_hex': '#c0c0c0',
                'price': 175000,
                'stock': 12,
                'sku': 'TECNO-CAMON40-256-16-TITANIUM'
            },
            {
                'title': 'TECNO CAMON 40 256GB 16GB Vert Lueur Émeraude',
                'rom': 256,
                'ram': 16,
                'color_name': 'Vert Lueur Émeraude',
                'color_hex': '#00ff7f',
                'price': 175000,
                'stock': 10,
                'sku': 'TECNO-CAMON40-256-16-GLOW'
            },
            # Variantes 128GB
            {
                'title': 'TECNO CAMON 40 128GB 16GB Noir Galaxy',
                'rom': 128,
                'ram': 16,
                'color_name': 'Noir Galaxy',
                'color_hex': '#000000',
                'price': 155000,
                'stock': 25,
                'sku': 'TECNO-CAMON40-128-16-BLACK'
            },
            {
                'title': 'TECNO CAMON 40 128GB 16GB Vert Émeraude',
                'rom': 128,
                'ram': 16,
                'color_name': 'Vert Émeraude',
                'color_hex': '#00a86b',
                'price': 155000,
                'stock': 22,
                'sku': 'TECNO-CAMON40-128-16-GREEN'
            },
            {
                'title': 'TECNO CAMON 40 128GB 16GB Blanc Glacier',
                'rom': 128,
                'ram': 16,
                'color_name': 'Blanc Glacier',
                'color_hex': '#f8f8ff',
                'price': 155000,
                'stock': 20,
                'sku': 'TECNO-CAMON40-128-16-WHITE'
            },
            {
                'title': 'TECNO CAMON 40 128GB 16GB Titanium Sable',
                'rom': 128,
                'ram': 16,
                'color_name': 'Titanium Sable',
                'color_hex': '#c0c0c0',
                'price': 155000,
                'stock': 18,
                'sku': 'TECNO-CAMON40-128-16-TITANIUM'
            },
            {
                'title': 'TECNO CAMON 40 128GB 16GB Vert Lueur Émeraude',
                'rom': 128,
                'ram': 16,
                'color_name': 'Vert Lueur Émeraude',
                'color_hex': '#00ff7f',
                'price': 155000,
                'stock': 15,
                'sku': 'TECNO-CAMON40-128-16-GLOW'
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for phone_data in phones_data:
            try:
                # Créer ou récupérer la couleur
                color, color_created = Color.objects.get_or_create(
                    name=phone_data['color_name'],
                    defaults={'code': phone_data['color_hex']}
                )
                
                if color_created:
                    self.stdout.write(f'✅ Couleur créée: {color.name} ({color.code})')
                
                # Créer ou mettre à jour le produit
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
                    # Mettre à jour les informations existantes
                    product.price = phone_data['price']
                    product.stock = phone_data['stock']
                    product.sku = phone_data['sku']
                    product.save()
                    self.stdout.write(f'🔄 Produit mis à jour: {product.title}')
                
                # Créer ou mettre à jour le téléphone
                phone, phone_created = Phone.objects.get_or_create(
                    product=product,
                    defaults={
                        'brand': 'TECNO',
                        'model': 'CAMON 40',
                        'operating_system': 'Android 15',
                        'processor': 'MediaTek Helio G100 Ultimate',
                        'network': '2G, 3G, 4G',
                        'screen_size': 6.78,
                        'resolution': '1080 x 2436',
                        'camera_front': '32 MP',
                        'camera_main': '50 MP 1/1.56" OIS + 8 MP Wide-angle, Dual Flash, Flicker Sensor',
                        'battery_capacity': 5200,
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
                    # Mettre à jour les informations existantes
                    phone.color = color
                    phone.storage = phone_data['rom']
                    phone.ram = phone_data['ram']
                    phone.save()
                    self.stdout.write(f'🔄 Téléphone mis à jour: {phone.product.title}')
                    updated_count += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erreur avec {phone_data["title"]}: {str(e)}'))
        
        self.stdout.write(f'\n📱 Résumé: {created_count} téléphones créés, {updated_count} mis à jour')
        self.stdout.write(self.style.SUCCESS('✅ Ajout des téléphones TECNO CAMON 40 terminé !')) 