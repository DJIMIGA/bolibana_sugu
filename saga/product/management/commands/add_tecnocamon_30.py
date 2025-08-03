from django.core.management.base import BaseCommand
from product.models import Product, Phone, Color, Category
from product.utils import normalize_phone_brand
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Ajoute les téléphones TECNO CAMON 30 5G'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Début de l\'ajout des téléphones TECNO CAMON 30 5G...')
        
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
        
        # Couleurs disponibles
        colors = [
            'Édition Loewe',
            'Noir Basaltique Islande',
            'Blanc Sel Uyuni',
            'Vert Lac Émeraude'
        ]
        
        # Variantes de mémoire
        memory_variants = [
            {'rom': 256, 'ram': 16, 'price': 180000, 'stock': 15},
            {'rom': 512, 'ram': 16, 'price': 200000, 'stock': 12},
            {'rom': 512, 'ram': 24, 'price': 220000, 'stock': 10}
        ]
        
        created_count = 0
        updated_count = 0
        
        for color_name in colors:
            for memory in memory_variants:
                try:
                    # Récupérer la couleur
                    color = Color.objects.get(name=color_name)
                except Color.DoesNotExist:
                    self.stdout.write(f'❌ Couleur non trouvée: {color_name}')
                    continue
                
                # Générer le titre unique
                title = f"TECNO CAMON 30 5G {memory['rom']}GB {memory['ram']}GB {color_name}"
                sku = f"TECNO-CAMON30-{memory['rom']}-{memory['ram']}-{color_name.replace(' ', '').upper()}"
                
                try:
                    # Créer ou mettre à jour le produit
                    product, product_created = Product.objects.get_or_create(
                        title=title,
                        defaults={
                            'category': category,
                            'price': memory['price'],
                            'stock': memory['stock'],
                            'sku': sku,
                            'slug': slugify(title),
                            'brand': normalized_brand,
                            'is_available': True,
                            'condition': 'new'
                        }
                    )
                    
                    if product_created:
                        self.stdout.write(f'✅ Produit créé: {product.title}')
                    else:
                        product.price = memory['price']
                        product.stock = memory['stock']
                        product.sku = sku
                        product.brand = normalized_brand
                        product.save()
                        self.stdout.write(f'🔄 Produit mis à jour: {product.title}')
                    
                    # Créer ou mettre à jour le téléphone
                    phone, phone_created = Phone.objects.get_or_create(
                        product=product,
                        defaults={
                            'brand': normalized_brand,
                            'model': 'CAMON 30 5G',
                            'operating_system': 'Android 14',
                            'processor': 'MediaTek Dimensity 7020 5G',
                            'network': '2G, 3G, 4G, 5G',
                            'screen_size': 6.78,
                            'resolution': '1080 x 2436',
                            'camera_front': '50 MP AF, Dual Colour Temperature Flash',
                            'camera_main': '50 MP 1/1.57" OIS + 2 MP Depth + Light Sensor, Dual Flash',
                            'battery_capacity': 5000,
                            'storage': memory['rom'],
                            'ram': memory['ram'],
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
                        phone.storage = memory['rom']
                        phone.ram = memory['ram']
                        phone.brand = normalized_brand
                        phone.save()
                        self.stdout.write(f'🔄 Téléphone mis à jour: {phone.product.title}')
                        updated_count += 1
                        
                except Exception as e:
                    self.stdout.write(f'❌ Erreur avec {title}: {str(e)}')
        
        self.stdout.write('')
        self.stdout.write(f'📱 Résumé: {created_count} téléphones créés, {updated_count} mis à jour')
        self.stdout.write('✅ Ajout des téléphones TECNO CAMON 30 5G terminé !')
        self.stdout.write('')
        self.stdout.write('📋 Spécifications techniques ajoutées :')
        self.stdout.write('• Système d\'exploitation : Android 14')
        self.stdout.write('• Processeur : MediaTek Dimensity 7020 5G')
        self.stdout.write('• Écran : 6.78" FHD+ AMOLED 120Hz')
        self.stdout.write('• Caméra frontale : 50 MP AF, Dual Colour Temperature Flash')
        self.stdout.write('• Caméra principale : 50 MP 1/1.57" OIS + 2 MP Depth + Light Sensor, Dual Flash')
        self.stdout.write('• Batterie : 5000 mAh 70W Ultra Charge Type-C')
        self.stdout.write('• Connectivité : GNSS, WiFi, FM, OTG, GPS')
        self.stdout.write('• Capteurs : G-Sensor, Ambient Light Sensor, Proximity Sensor, Electronic Compass, Gyroscope, Infrared Remote Control, Fingerprint Sensor')
        self.stdout.write('')
        self.stdout.write('💾 Variantes de mémoire ajoutées :')
        self.stdout.write('• 256GB ROM + 16GB RAM (8GB + 8GB Extended) - 180,000 FCFA')
        self.stdout.write('• 512GB ROM + 16GB RAM (8GB + 8GB Extended) - 200,000 FCFA')
        self.stdout.write('• 512GB ROM + 24GB RAM (12GB + 12GB Extended) - 220,000 FCFA') 