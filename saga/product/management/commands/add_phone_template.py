from django.core.management.base import BaseCommand
from product.models import Phone, Color, Category, Product
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Template pour ajouter des téléphones (exemple avec TECNO CAMON 40 Pro)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--brand',
            type=str,
            default='TECNO',
            help='Marque du téléphone'
        )
        parser.add_argument(
            '--model',
            type=str,
            default='CAMON 40 Pro',
            help='Modèle du téléphone'
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Template pour ajouter des téléphones...')
        
        # Récupérer la catégorie Téléphones
        try:
            category = Category.objects.get(name='Téléphones')
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Catégorie "Téléphones" non trouvée'))
            return
        
        # EXEMPLE : Données des téléphones TECNO CAMON 40 Pro
        # Modifiez cette section selon vos besoins
        phones_data = [
            {
                'title': f'{options["brand"]} {options["model"]} 256GB 16GB Noir Galaxy',
                'rom': 256,
                'ram': 16,
                'color_name': 'Noir Galaxy',
                'color_hex': '#000000',
                'price': 185000,
                'stock': 15,
                'sku': f'{options["brand"].upper()}-{options["model"].replace(" ", "")}-256-16-BLACK'
            },
            {
                'title': f'{options["brand"]} {options["model"]} 256GB 16GB Vert Émeraude',
                'rom': 256,
                'ram': 16,
                'color_name': 'Vert Émeraude',
                'color_hex': '#00a86b',
                'price': 185000,
                'stock': 12,
                'sku': f'{options["brand"].upper()}-{options["model"].replace(" ", "")}-256-16-GREEN'
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
                        'brand': options['brand'],
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
                        'brand': options['brand'],
                        'model': options['model'],
                        'operating_system': 'Android 15',
                        'processor': 'MediaTek Helio G100 Ultimate Processor',
                        'network': '2G, 3G, 4G',
                        'screen_size': 6.78,
                        'resolution': '1080 x 2436',
                        'camera_front': '50 MP AF',
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
        self.stdout.write(self.style.SUCCESS('✅ Template d\'ajout de téléphones terminé !'))
        
        # Instructions d'utilisation
        self.stdout.write('\n📝 INSTRUCTIONS D\'UTILISATION :')
        self.stdout.write('1. Modifiez la section "phones_data" selon vos besoins')
        self.stdout.write('2. Ajustez les spécifications techniques dans les "defaults" du Phone')
        self.stdout.write('3. Utilisez : python manage.py add_phone_template --brand "MARQUE" --model "MODELE"')
        self.stdout.write('4. Ou copiez cette commande et renommez-la pour votre modèle spécifique') 