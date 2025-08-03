from django.core.management.base import BaseCommand
from product.models import Product, Phone, Color, Category
from product.utils import normalize_phone_brand
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Ajoute les téléphones TECNO CAMON 30 Pro 5G'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Début de l\'ajout des téléphones TECNO CAMON 30 Pro 5G...')
        
        # Normalisation des marques TECNO
        self.stdout.write('🔧 Normalisation des marques TECNO...')
        normalized_brand = normalize_phone_brand('TECNO')
        self.stdout.write(f'✅ Marque normalisée: {normalized_brand}')
        
        # Récupération de la catégorie
        try:
            category = Category.objects.get(name='Téléphones')
        except Category.DoesNotExist:
            self.stdout.write('❌ Catégorie "Téléphones" non trouvée')
            return
        
        # Données des téléphones TECNO CAMON 30 Pro 5G
        phones_data = [
            {
                'title': 'TECNO CAMON 30 Pro 5G 512GB 24GB Édition Loewe',
                'rom': 512,
                'ram': 24,
                'color_name': 'Édition Loewe',
                'color_hex': '#1a1a1a',
                'price': 230000,
                'stock': 10,
                'sku': 'TECNO-CAMON30PRO-512-24-LOEWE'
            },
            {
                'title': 'TECNO CAMON 30 Pro 5G 512GB 24GB Noir Basaltique Islande',
                'rom': 512,
                'ram': 24,
                'color_name': 'Noir Basaltique Islande',
                'color_hex': '#2d1810',
                'price': 230000,
                'stock': 15,
                'sku': 'TECNO-CAMON30PRO-512-24-BLACK'
            },
            {
                'title': 'TECNO CAMON 30 Pro 5G 512GB 24GB Argent Neigeux Alpes',
                'rom': 512,
                'ram': 24,
                'color_name': 'Argent Neigeux Alpes',
                'color_hex': '#f5f5f5',
                'price': 230000,
                'stock': 12,
                'sku': 'TECNO-CAMON30PRO-512-24-SILVER'
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
                        'brand': normalized_brand,
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
                    product.brand = normalized_brand
                    product.save()
                    self.stdout.write(f'🔄 Produit mis à jour: {product.title}')
                
                # Créer ou mettre à jour le téléphone
                phone, phone_created = Phone.objects.get_or_create(
                    product=product,
                    defaults={
                        'brand': normalized_brand,
                        'model': 'CAMON 30 Pro 5G',
                        'operating_system': 'Android 14',
                        'processor': 'MediaTek Dimensity 8200 Ultimate 5G',
                        'network': '2G, 3G, 4G, 5G',
                        'screen_size': 6.78,
                        'resolution': '1080 x 2436',
                        'camera_front': '50 MP AF',
                        'camera_main': '50 MP 1/1.56" OIS + 50 MP UW + 2 MP Depth, Rear Dual Flash',
                        'battery_capacity': 5000,
                        'storage': phone_data['rom'],
                        'ram': phone_data['ram'],
                        'color': color,
                        'is_new': True,
                        'box_included': True,
                        'accessories': 'Chargeur 70W, Câble Type-C, Coque de protection, Écouteurs'
                    }
                )
                
                if phone_created:
                    self.stdout.write(f'✅ Téléphone créé: {phone.product.title}')
                    created_count += 1
                else:
                    phone.color = color
                    phone.storage = phone_data['rom']
                    phone.ram = phone_data['ram']
                    phone.brand = normalized_brand
                    phone.save()
                    self.stdout.write(f'🔄 Téléphone mis à jour: {phone.product.title}')
                    updated_count += 1
                    
            except Exception as e:
                self.stdout.write(f'❌ Erreur avec {phone_data["title"]}: {str(e)}')
        
        self.stdout.write('')
        self.stdout.write(f'📱 Résumé: {created_count} téléphones créés, {updated_count} mis à jour')
        self.stdout.write('✅ Ajout des téléphones TECNO CAMON 30 Pro 5G terminé !')
        self.stdout.write('')
        self.stdout.write('📋 Spécifications techniques ajoutées :')
        self.stdout.write('• Système d\'exploitation : Android 14')
        self.stdout.write('• Processeur : MediaTek Dimensity 8200 Ultimate 5G')
        self.stdout.write('• Écran : 6.78" FHD+ AMOLED 144Hz')
        self.stdout.write('• Caméra frontale : 50 MP AF')
        self.stdout.write('• Caméra principale : 50 MP 1/1.56" OIS + 50 MP UW + 2 MP Depth, Rear Dual Flash')
        self.stdout.write('• Batterie : 5000 mAh 70W Ultra Charge Type-C')
        self.stdout.write('• Connectivité : GNSS, WiFi, FM, OTG')
        self.stdout.write('• Capteurs : G-Sensor, Flicker sensor, Ambient Light Sensor, Electronic compass, Gyroscope, Infrared Remote Control, Fingerprint Sensor') 