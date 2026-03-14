from django.core.management.base import BaseCommand
from product.models import Product, Phone, Color, Category
from product.utils import normalize_phone_brand
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Ajoute uniquement les modèles POVA manquants en utilisant le template'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            help='Modèle spécifique à ajouter (ex: POVA 7 Pro 5G, POVA 7 5G, etc.)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche ce qui serait fait sans effectuer les modifications'
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Début de l\'ajout des modèles POVA manquants...')
        
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
        
        # Vérifier les modèles existants
        existing_models = set(Phone.objects.filter(
            brand__iexact=normalized_brand,
            model__icontains='POVA'
        ).values_list('model', flat=True).distinct())
        
        self.stdout.write(f'📋 Modèles POVA existants: {sorted(existing_models)}')
        
        # Configuration des modèles POVA à ajouter
        # NOTE: Les spécifications seront mises à jour avec les vraies données
        pova_configs = {
                         'POVA 7 Pro 5G': {
                 'colors': ['Noir Geek', 'Gris Dynamique', 'Cyan Néon'],
                 'specs': {
                     'operating_system': 'Android 15',
                     'processor': 'MediaTek Dimensity 7300 Ultimate',
                     'network': 'GSM, GPRS, FULL EDGE, WCDMA, HSPA+, FDD LTE, TDD LTE, 5G NR',
                     'screen_size': 6.78,
                     'resolution': '2720 x 1224',
                     'camera_front': '13 MP',
                     'camera_main': '64 MP + 8 MP avec Dual Flash',
                     'battery_capacity': 6000,
                     'memory_variants': [
                         {'rom': 128, 'ram': 16, 'price': 160000, 'stock': 15},
                         {'rom': 256, 'ram': 16, 'price': 190000, 'stock': 10},
                         {'rom': 256, 'ram': 24, 'price': 230000, 'stock': 8}
                     ]
                 }
             },
                         'POVA 7 5G': {
                 'colors': ['Noir Geek', 'Argent Magique', 'Vert Oasis'],
                 'specs': {
                     'operating_system': 'Android 15',
                     'processor': 'MediaTek Dimensity 7300 Ultimate',
                     'network': 'GSM, GPRS, FULL EDGE, WCDMA, HSPA+, FDD LTE, TDD LTE, 5G NR',
                     'screen_size': 6.78,
                     'resolution': '2460 x 1080',
                     'camera_front': '13 MP',
                     'camera_main': '50 MP + Light Sensor avec Dual Flash',
                     'battery_capacity': 6000,
                     'memory_variants': [
                         {'rom': 128, 'ram': 16, 'price': 140000, 'stock': 15},
                         {'rom': 256, 'ram': 16, 'price': 170000, 'stock': 10}
                     ]
                 }
             },
            'POVA 7 Ultra 5G': {
                'colors': ['Noir Minuit', 'Bleu Cyan', 'Violet Étoilé'],
                'specs': {
                    'operating_system': 'Android 14',
                    'processor': 'MediaTek Dimensity 7200',
                    'network': '2G, 3G, 4G, 5G',
                    'screen_size': 6.78,
                    'resolution': '1080 x 2436',
                    'camera_front': '16 MP',
                    'camera_main': '108 MP + 8 MP + 2 MP + 2 MP',
                    'battery_capacity': 7000,
                    'memory_variants': [
                        {'rom': 256, 'ram': 12, 'price': 200000, 'stock': 12},
                        {'rom': 512, 'ram': 16, 'price': 250000, 'stock': 8}
                    ]
                }
            },
            'POVA 7': {
                'colors': ['Noir Obsidien', 'Bleu Ice', 'Vert Ice'],
                'specs': {
                    'operating_system': 'Android 14',
                    'processor': 'MediaTek Helio G99',
                    'network': '2G, 3G, 4G',
                    'screen_size': 6.78,
                    'resolution': '1080 x 2436',
                    'camera_front': '16 MP',
                    'camera_main': '50 MP + 8 MP + 2 MP + 2 MP',
                    'battery_capacity': 6000,
                    'memory_variants': [
                        {'rom': 128, 'ram': 8, 'price': 120000, 'stock': 15},
                        {'rom': 256, 'ram': 12, 'price': 150000, 'stock': 10}
                    ]
                }
            },
                         'POVA Curve 5G': {
                 'colors': ['Noir Geek', 'Argent Magique', 'Cyan Néon'],
                 'specs': {
                     'operating_system': 'Android 15',
                     'processor': 'MediaTek Dimensity 7300 Ultimate',
                     'network': '2G, 3G, 4G, 5G',
                     'screen_size': 6.78,
                     'resolution': '1080 x 2436',
                     'camera_front': '13 MP',
                     'camera_main': '64 MP 1/1.73" avec Dual Flash',
                     'battery_capacity': 5500,
                     'memory_variants': [
                         {'rom': 128, 'ram': 12, 'price': 160000, 'stock': 15},
                         {'rom': 128, 'ram': 16, 'price': 180000, 'stock': 12},
                         {'rom': 256, 'ram': 16, 'price': 200000, 'stock': 10}
                     ]
                 }
             },
                         'POVA 6 Pro 5G': {
                 'colors': ['Vert Comète', 'Gris Météorite'],
                 'specs': {
                     'operating_system': 'HiOS basé sur Android 14',
                     'processor': 'MediaTek Dimensity 6080 5G Gaming Processor',
                     'network': 'GSM, GPRS, FULL EDGE, WCDMA, HSPA+, FDD LTE, TDD LTE, 5G NR',
                     'screen_size': 6.78,
                     'resolution': '1080 x 2436',
                     'camera_front': '32 MP avec Dual Flash',
                     'camera_main': '108 MP + 2 MP Dual Camera + Light sensor',
                     'battery_capacity': 6000,
                     'memory_variants': [
                         {'rom': 256, 'ram': 24, 'price': 180000, 'stock': 12}
                     ]
                 }
             },
                         'POVA 6 NEO': {
                 'colors': ['Argent Étoilé', 'Noir Vitesse', 'Vert Comète'],
                 'specs': {
                     'operating_system': 'Android 14',
                     'processor': 'MediaTek G99 Ultimate',
                     'network': 'GSM, GPRS, FULL EDGE, WCDMA, HSPA+, FDD LTE',
                     'screen_size': 6.78,
                     'resolution': '1080 x 2460',
                     'camera_front': '8 MP avec Dual Flash',
                     'camera_main': '50 MP + Light sensor',
                     'battery_capacity': 7000,
                     'memory_variants': [
                         {'rom': 128, 'ram': 8, 'price': 110000, 'stock': 15},
                         {'rom': 256, 'ram': 8, 'price': 140000, 'stock': 10}
                     ]
                 }
             },
                         'POVA 6': {
                 'colors': ['Vert Comète', 'Gris Météorite', 'Bleu Interstellaire'],
                 'specs': {
                     'operating_system': 'Android 14',
                     'processor': 'MediaTek G99 Ultimate',
                     'network': 'GSM, GPRS, FULL EDGE, WCDMA, HSPA+, FDD LTE',
                     'screen_size': 6.78,
                     'resolution': '1080 x 2436',
                     'camera_front': '32 MP avec Dual Flash',
                     'camera_main': '108 MP + Light sensor',
                     'battery_capacity': 6000,
                     'memory_variants': [
                         {'rom': 256, 'ram': 8, 'price': 120000, 'stock': 15},
                         {'rom': 256, 'ram': 12, 'price': 150000, 'stock': 10}
                     ]
                 }
             },
             'POVA 7': {
                 'colors': ['Titanium Hyper', 'Argent Magique', 'Noir Geek'],
                 'specs': {
                     'operating_system': 'Android 15',
                     'processor': 'MediaTek Helio G100 Ultimate',
                     'network': 'GSM, GPRS, FULL EDGE, WCDMA, HSPA+, FDD LTE',
                     'screen_size': 6.78,
                     'resolution': '2460 x 1080',
                     'camera_front': '8 MP',
                     'camera_main': '108 MP + 2 MP avec Dual Flash',
                     'battery_capacity': 7000,
                     'memory_variants': [
                         {'rom': 128, 'ram': 16, 'price': 130000, 'stock': 15},
                         {'rom': 256, 'ram': 16, 'price': 160000, 'stock': 10}
                     ]
                 }
             },
             'POVA 7 Ultra 5G': {
                 'colors': ['Blanc Geek', 'Noir Geek'],
                 'specs': {
                     'operating_system': 'Android 15',
                     'processor': 'MediaTek Dimensity 8350 Ultimate',
                     'network': 'GSM, GPRS, FULL EDGE, WCDMA, HSPA+, FDD LTE, TDD LTE, 5G NR',
                     'screen_size': 6.67,
                     'resolution': '2800 x 1260',
                     'camera_front': '13 MP',
                     'camera_main': '108 MP + 8 MP avec Dual Flash',
                     'battery_capacity': 6000,
                     'memory_variants': [
                         {'rom': 256, 'ram': 16, 'price': 180000, 'stock': 10},
                         {'rom': 256, 'ram': 24, 'price': 220000, 'stock': 8}
                     ]
                 }
             }
        }
        
        # Déterminer quels modèles ajouter
        models_to_add = []
        if options['model']:
            if options['model'] in pova_configs:
                models_to_add = [options['model']]
            else:
                self.stdout.write(f'❌ Modèle "{options["model"]}" non trouvé dans la configuration')
                return
        else:
            # Ajouter tous les modèles manquants
            for model_name in pova_configs.keys():
                # Vérifier si le modèle existe (insensible à la casse)
                model_exists = any(
                    existing.lower() == model_name.lower() 
                    for existing in existing_models
                )
                if not model_exists:
                    models_to_add.append(model_name)
        
        if not models_to_add:
            self.stdout.write('✅ Tous les modèles POVA sont déjà présents dans la base de données')
            return
        
        self.stdout.write(f'📱 Modèles à ajouter: {models_to_add}')
        
        if options['dry_run']:
            self.stdout.write('🔍 Mode DRY-RUN - Aucune modification ne sera effectuée')
        
        created_count = 0
        updated_count = 0
        
        for model_name in models_to_add:
            self.stdout.write(f'📱 Traitement du modèle {model_name}...')
            config = pova_configs[model_name]
            
            for color_name in config['colors']:
                try:
                    # Récupérer la couleur
                    color = Color.objects.get(name=color_name)
                except Color.DoesNotExist:
                    self.stdout.write(f'❌ Couleur non trouvée: {color_name}')
                    continue
                
                for memory in config['specs']['memory_variants']:
                    # Générer le titre unique
                    title = f"TECNO {model_name} {memory['rom']}GB {memory['ram']}GB {color_name}"
                    sku = f"TECNO-{model_name.replace(' ', '').replace('5G', '5G')}-{memory['rom']}-{memory['ram']}-{color_name.replace(' ', '').upper()}"
                    
                    if options['dry_run']:
                        self.stdout.write(f'  🔍 [DRY-RUN] Créerait: {title}')
                        created_count += 1
                        continue
                    
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
                                'model': model_name,
                                'operating_system': config['specs']['operating_system'],
                                'processor': config['specs']['processor'],
                                'network': config['specs']['network'],
                                'screen_size': config['specs']['screen_size'],
                                'resolution': config['specs']['resolution'],
                                'camera_front': config['specs']['camera_front'],
                                'camera_main': config['specs']['camera_main'],
                                'battery_capacity': config['specs']['battery_capacity'],
                                'storage': memory['rom'],
                                'ram': memory['ram'],
                                'color': color,
                                'is_new': True,
                                'box_included': True,
                                'accessories': 'Chargeur 33W, Câble Type-C, Coque de protection, Écouteurs'
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
        if options['dry_run']:
            self.stdout.write(f'🔍 [DRY-RUN] Résumé: {created_count} téléphones seraient créés')
        else:
            self.stdout.write(f'📱 Résumé: {created_count} téléphones créés, {updated_count} mis à jour')
        
        self.stdout.write('✅ Ajout des modèles POVA manquants terminé !')
        self.stdout.write('')
        self.stdout.write('💡 Gamme POVA : Smartphones gaming et performance TECNO avec batteries haute capacité')
        self.stdout.write('🎮 Optimisés pour le gaming et les applications intensives') 