from django.core.management.base import BaseCommand
from product.models import Product, Phone, Color, Category
from product.utils import normalize_phone_brand
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Ajoute tous les téléphones TECNO POP en une seule fois'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Début de l\'ajout de tous les téléphones TECNO POP...')
        
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
        
        # Données de tous les modèles TECNO POP
        pop_models = [
            {
                'model': 'POP 8',
                'colors': ['Noir Mystérieux', 'Bleu Océan', 'Vert Émeraude', 'Or Doré'],
                'specs': {
                    'operating_system': 'Android 13 (Go Edition)',
                    'processor': 'Unisoc T606',
                    'network': '2G, 3G, 4G',
                    'screen_size': 6.6,
                    'resolution': '720 x 1612',
                    'camera_front': '8 MP',
                    'camera_main': '13 MP + 2 MP + 2 MP',
                    'battery_capacity': 5000,
                    'memory_variants': [
                        {'rom': 64, 'ram': 3, 'price': 45000, 'stock': 20},
                        {'rom': 128, 'ram': 4, 'price': 55000, 'stock': 15},
                        {'rom': 128, 'ram': 6, 'price': 65000, 'stock': 10}
                    ]
                }
            },
            {
                'model': 'POP 7',
                'colors': ['Noir Infini', 'Bleu Capri', 'Vert Ice Lake'],
                'specs': {
                    'operating_system': 'Android 13 (Go Edition)',
                    'processor': 'Unisoc T606',
                    'network': '2G, 3G, 4G',
                    'screen_size': 6.6,
                    'resolution': '720 x 1612',
                    'camera_front': '8 MP',
                    'camera_main': '13 MP + 2 MP + 2 MP',
                    'battery_capacity': 5000,
                    'memory_variants': [
                        {'rom': 64, 'ram': 3, 'price': 40000, 'stock': 20},
                        {'rom': 128, 'ram': 4, 'price': 50000, 'stock': 15}
                    ]
                }
            },
            {
                'model': 'POP 6',
                'colors': ['Noir Minuit', 'Bleu Cyan', 'Violet Étoilé'],
                'specs': {
                    'operating_system': 'Android 12 (Go Edition)',
                    'processor': 'Unisoc T606',
                    'network': '2G, 3G, 4G',
                    'screen_size': 6.5,
                    'resolution': '720 x 1600',
                    'camera_front': '8 MP',
                    'camera_main': '13 MP + 2 MP + 2 MP',
                    'battery_capacity': 5000,
                    'memory_variants': [
                        {'rom': 64, 'ram': 3, 'price': 35000, 'stock': 20},
                        {'rom': 128, 'ram': 4, 'price': 45000, 'stock': 15}
                    ]
                }
            },
            {
                'model': 'POP 5',
                'colors': ['Noir Obsidien', 'Bleu Ice', 'Vert Ice'],
                'specs': {
                    'operating_system': 'Android 12 (Go Edition)',
                    'processor': 'Unisoc T606',
                    'network': '2G, 3G, 4G',
                    'screen_size': 6.5,
                    'resolution': '720 x 1600',
                    'camera_front': '8 MP',
                    'camera_main': '13 MP + 2 MP + 2 MP',
                    'battery_capacity': 5000,
                    'memory_variants': [
                        {'rom': 64, 'ram': 3, 'price': 30000, 'stock': 20},
                        {'rom': 128, 'ram': 4, 'price': 40000, 'stock': 15}
                    ]
                }
            },
            {
                'model': 'POP 4',
                'colors': ['Noir Gravité', 'Bleu Ville', 'Magic Skin (Vert)'],
                'specs': {
                    'operating_system': 'Android 11 (Go Edition)',
                    'processor': 'Unisoc T606',
                    'network': '2G, 3G, 4G',
                    'screen_size': 6.52,
                    'resolution': '720 x 1600',
                    'camera_front': '8 MP',
                    'camera_main': '13 MP + 2 MP + 2 MP',
                    'battery_capacity': 5000,
                    'memory_variants': [
                        {'rom': 64, 'ram': 3, 'price': 25000, 'stock': 20},
                        {'rom': 128, 'ram': 4, 'price': 35000, 'stock': 15}
                    ]
                }
            },
            {
                'model': 'POP 3',
                'colors': ['Or Alpenglow', 'Blanc Mystère', 'Violet Étoilé'],
                'specs': {
                    'operating_system': 'Android 11 (Go Edition)',
                    'processor': 'Unisoc T606',
                    'network': '2G, 3G, 4G',
                    'screen_size': 6.52,
                    'resolution': '720 x 1600',
                    'camera_front': '8 MP',
                    'camera_main': '13 MP + 2 MP + 2 MP',
                    'battery_capacity': 5000,
                    'memory_variants': [
                        {'rom': 64, 'ram': 3, 'price': 20000, 'stock': 20},
                        {'rom': 128, 'ram': 4, 'price': 30000, 'stock': 15}
                    ]
                }
            },
            {
                'model': 'POP 2',
                'colors': ['Bleu Océan', 'Noir Brillant', 'Bleu Uyuni'],
                'specs': {
                    'operating_system': 'Android 10 (Go Edition)',
                    'processor': 'Unisoc T606',
                    'network': '2G, 3G, 4G',
                    'screen_size': 6.52,
                    'resolution': '720 x 1600',
                    'camera_front': '8 MP',
                    'camera_main': '13 MP + 2 MP + 2 MP',
                    'battery_capacity': 5000,
                    'memory_variants': [
                        {'rom': 64, 'ram': 3, 'price': 15000, 'stock': 20},
                        {'rom': 128, 'ram': 4, 'price': 25000, 'stock': 15}
                    ]
                }
            },
            {
                'model': 'POP 1',
                'colors': ['Violet Nébuleuse', 'Bleu Capri', 'Gris Argent'],
                'specs': {
                    'operating_system': 'Android 10 (Go Edition)',
                    'processor': 'Unisoc T606',
                    'network': '2G, 3G, 4G',
                    'screen_size': 6.52,
                    'resolution': '720 x 1600',
                    'camera_front': '8 MP',
                    'camera_main': '13 MP + 2 MP + 2 MP',
                    'battery_capacity': 5000,
                    'memory_variants': [
                        {'rom': 64, 'ram': 3, 'price': 12000, 'stock': 20},
                        {'rom': 128, 'ram': 4, 'price': 20000, 'stock': 15}
                    ]
                }
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for pop_model in pop_models:
            self.stdout.write(f'📱 Ajout du modèle {pop_model["model"]}...')
            
            for color_name in pop_model['colors']:
                try:
                    # Récupérer la couleur
                    color = Color.objects.get(name=color_name)
                except Color.DoesNotExist:
                    self.stdout.write(f'❌ Couleur non trouvée: {color_name}')
                    continue
                
                for memory in pop_model['specs']['memory_variants']:
                    # Générer le titre unique
                    title = f"TECNO {pop_model['model']} {memory['rom']}GB {memory['ram']}GB {color_name}"
                    sku = f"TECNO-{pop_model['model'].replace(' ', '')}-{memory['rom']}-{memory['ram']}-{color_name.replace(' ', '').upper()}"
                    
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
                                'model': pop_model['model'],
                                'operating_system': pop_model['specs']['operating_system'],
                                'processor': pop_model['specs']['processor'],
                                'network': pop_model['specs']['network'],
                                'screen_size': pop_model['specs']['screen_size'],
                                'resolution': pop_model['specs']['resolution'],
                                'camera_front': pop_model['specs']['camera_front'],
                                'camera_main': pop_model['specs']['camera_main'],
                                'battery_capacity': pop_model['specs']['battery_capacity'],
                                'storage': memory['rom'],
                                'ram': memory['ram'],
                                'color': color,
                                'is_new': True,
                                'box_included': True,
                                'accessories': 'Chargeur, Câble USB, Coque de protection'
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
        self.stdout.write('✅ Ajout de tous les téléphones TECNO POP terminé !')
        self.stdout.write('')
        self.stdout.write('📋 Modèles ajoutés :')
        for pop_model in pop_models:
            self.stdout.write(f'• {pop_model["model"]} - {len(pop_model["colors"])} couleurs - {len(pop_model["specs"]["memory_variants"])} variantes mémoire')
        self.stdout.write('')
        self.stdout.write('💡 Gamme POP : Smartphones d\'entrée de gamme TECNO avec Android Go Edition') 