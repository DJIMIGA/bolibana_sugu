from django.core.management.base import BaseCommand
from product.models import Product, Category, Phone, Color
from suppliers.models import Supplier
from django.db import transaction
import uuid

class Command(BaseCommand):
    help = 'Ajoute les modèles d\'iPhone à la base de données'

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                # Récupérer ou créer la catégorie iPhone
                iphone_category, created = Category.objects.get_or_create(
                    name='iPhone',
                    defaults={'slug': 'iphone'}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS('Catégorie iPhone créée avec succès'))
                else:
                    self.stdout.write(self.style.SUCCESS('Catégorie iPhone existante récupérée'))

                # Récupérer ou créer le fournisseur Apple
                apple_supplier, created = Supplier.objects.get_or_create(
                    name='Apple',
                    defaults={'slug': 'apple'}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS('Fournisseur Apple créé avec succès'))
                else:
                    self.stdout.write(self.style.SUCCESS('Fournisseur Apple existant récupéré'))

                # Couleurs disponibles
                colors = {
                    'Noir': '#000000',
                    'Blanc': '#FFFFFF',
                    'Or': '#FFD700',
                    'Argent': '#C0C0C0',
                    'Bleu': '#0000FF',
                    'Rose': '#FFC0CB',
                    'Vert': '#00FF00',
                    'Rouge': '#FF0000',
                    'Violet': '#800080',
                    'Jaune': '#FFFF00',
                    'Corail': '#FF7F50',
                    'Bleu Saphir': '#0F52BA',
                    'Bleu Ciel': '#87CEEB',
                    'Vert Menthe': '#98FF98',
                    'Rose Poudré': '#FFD1DC',
                    'Or Rose': '#B76E79',
                    'Bleu Pacifique': '#1E90FF',
                    'Vert Minuit': '#004953',
                }

                # Créer les couleurs si elles n'existent pas
                color_objects = {}
                for name, code in colors.items():
                    color, created = Color.objects.get_or_create(
                        name=name,
                        defaults={'code': code}
                    )
                    color_objects[name] = color
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Couleur {name} créée avec succès'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Couleur {name} existante récupérée'))

                # Liste des iPhones à ajouter
                iphones = [
                    # iPhone 16 (modèles anticipés)
                    {
                        'model': 'iPhone 16 Pro Max',
                        'price': 1600000,
                        'os': 'iOS 18',
                        'screen': 6.9,
                        'resolution': '2876 x 1290',
                        'processor': 'A18 Pro',
                        'ram': 8,
                        'storage': 256,
                        'battery': 4677,
                        'camera_main': '48MP + 12MP + 12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Or', 'Bleu']
                    },
                    {
                        'model': 'iPhone 16 Pro',
                        'price': 1400000,
                        'os': 'iOS 18',
                        'screen': 6.3,
                        'resolution': '2556 x 1179',
                        'processor': 'A18 Pro',
                        'ram': 8,
                        'storage': 256,
                        'battery': 3274,
                        'camera_main': '48MP + 12MP + 12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Or', 'Bleu']
                    },
                    {
                        'model': 'iPhone 16 Plus',
                        'price': 1300000,
                        'os': 'iOS 18',
                        'screen': 6.7,
                        'resolution': '2796 x 1290',
                        'processor': 'A17 Pro',
                        'ram': 6,
                        'storage': 256,
                        'battery': 4383,
                        'camera_main': '48MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Rose', 'Bleu', 'Vert']
                    },
                    {
                        'model': 'iPhone 16',
                        'price': 1100000,
                        'os': 'iOS 18',
                        'screen': 6.1,
                        'resolution': '2556 x 1179',
                        'processor': 'A17 Pro',
                        'ram': 6,
                        'storage': 256,
                        'battery': 3349,
                        'camera_main': '48MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Rose', 'Bleu', 'Vert']
                    },
                    # iPhone 15 (déjà existant)
                    {
                        'model': 'iPhone 15 Pro Max',
                        'price': 1500000,
                        'os': 'iOS 17',
                        'screen': 6.7,
                        'resolution': '2796 x 1290',
                        'processor': 'A17 Pro',
                        'ram': 8,
                        'storage': 256,
                        'battery': 4422,
                        'camera_main': '48MP + 12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Or', 'Bleu']
                    },
                    {
                        'model': 'iPhone 15 Pro',
                        'price': 1300000,
                        'os': 'iOS 17',
                        'screen': 6.1,
                        'resolution': '2556 x 1179',
                        'processor': 'A17 Pro',
                        'ram': 8,
                        'storage': 256,
                        'battery': 3274,
                        'camera_main': '48MP + 12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Or', 'Bleu']
                    },
                    {
                        'model': 'iPhone 15 Plus',
                        'price': 1200000,
                        'os': 'iOS 17',
                        'screen': 6.7,
                        'resolution': '2796 x 1290',
                        'processor': 'A16 Bionic',
                        'ram': 6,
                        'storage': 256,
                        'battery': 4383,
                        'camera_main': '48MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Rose', 'Bleu', 'Vert']
                    },
                    {
                        'model': 'iPhone 15',
                        'price': 1000000,
                        'os': 'iOS 17',
                        'screen': 6.1,
                        'resolution': '2556 x 1179',
                        'processor': 'A16 Bionic',
                        'ram': 6,
                        'storage': 256,
                        'battery': 3349,
                        'camera_main': '48MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Rose', 'Bleu', 'Vert']
                    },
                    # iPhone 14 (déjà existant)
                    {
                        'model': 'iPhone 14 Pro Max',
                        'price': 1400000,
                        'os': 'iOS 16',
                        'screen': 6.7,
                        'resolution': '2796 x 1290',
                        'processor': 'A16 Bionic',
                        'ram': 6,
                        'storage': 256,
                        'battery': 4323,
                        'camera_main': '48MP + 12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Or', 'Violet']
                    },
                    {
                        'model': 'iPhone 14 Pro',
                        'price': 1200000,
                        'os': 'iOS 16',
                        'screen': 6.1,
                        'resolution': '2556 x 1179',
                        'processor': 'A16 Bionic',
                        'ram': 6,
                        'storage': 256,
                        'battery': 3200,
                        'camera_main': '48MP + 12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Or', 'Violet']
                    },
                    {
                        'model': 'iPhone 14 Plus',
                        'price': 1100000,
                        'os': 'iOS 16',
                        'screen': 6.7,
                        'resolution': '2778 x 1284',
                        'processor': 'A15 Bionic',
                        'ram': 6,
                        'storage': 256,
                        'battery': 4325,
                        'camera_main': '12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Bleu', 'Rouge', 'Violet']
                    },
                    {
                        'model': 'iPhone 14',
                        'price': 900000,
                        'os': 'iOS 16',
                        'screen': 6.1,
                        'resolution': '2532 x 1170',
                        'processor': 'A15 Bionic',
                        'ram': 6,
                        'storage': 256,
                        'battery': 3279,
                        'camera_main': '12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Bleu', 'Rouge', 'Violet']
                    },
                    # iPhone 13
                    {
                        'model': 'iPhone 13 Pro Max',
                        'price': 1300000,
                        'os': 'iOS 15',
                        'screen': 6.7,
                        'resolution': '2778 x 1284',
                        'processor': 'A15 Bionic',
                        'ram': 6,
                        'storage': 256,
                        'battery': 4352,
                        'camera_main': '12MP + 12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Or', 'Bleu Saphir']
                    },
                    {
                        'model': 'iPhone 13 Pro',
                        'price': 1100000,
                        'os': 'iOS 15',
                        'screen': 6.1,
                        'resolution': '2532 x 1170',
                        'processor': 'A15 Bionic',
                        'ram': 6,
                        'storage': 256,
                        'battery': 3095,
                        'camera_main': '12MP + 12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Or', 'Bleu Saphir']
                    },
                    {
                        'model': 'iPhone 13',
                        'price': 900000,
                        'os': 'iOS 15',
                        'screen': 6.1,
                        'resolution': '2532 x 1170',
                        'processor': 'A15 Bionic',
                        'ram': 4,
                        'storage': 256,
                        'battery': 3227,
                        'camera_main': '12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Rose', 'Bleu', 'Vert Menthe', 'Rouge']
                    },
                    {
                        'model': 'iPhone 13 mini',
                        'price': 800000,
                        'os': 'iOS 15',
                        'screen': 5.4,
                        'resolution': '2340 x 1080',
                        'processor': 'A15 Bionic',
                        'ram': 4,
                        'storage': 256,
                        'battery': 2406,
                        'camera_main': '12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Rose', 'Bleu', 'Vert Menthe', 'Rouge']
                    },
                    # iPhone 12
                    {
                        'model': 'iPhone 12 Pro Max',
                        'price': 1200000,
                        'os': 'iOS 14',
                        'screen': 6.7,
                        'resolution': '2778 x 1284',
                        'processor': 'A14 Bionic',
                        'ram': 6,
                        'storage': 256,
                        'battery': 3687,
                        'camera_main': '12MP + 12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Or', 'Bleu Pacifique']
                    },
                    {
                        'model': 'iPhone 12 Pro',
                        'price': 1000000,
                        'os': 'iOS 14',
                        'screen': 6.1,
                        'resolution': '2532 x 1170',
                        'processor': 'A14 Bionic',
                        'ram': 6,
                        'storage': 256,
                        'battery': 2815,
                        'camera_main': '12MP + 12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Or', 'Bleu Pacifique']
                    },
                    {
                        'model': 'iPhone 12',
                        'price': 800000,
                        'os': 'iOS 14',
                        'screen': 6.1,
                        'resolution': '2532 x 1170',
                        'processor': 'A14 Bionic',
                        'ram': 4,
                        'storage': 256,
                        'battery': 2815,
                        'camera_main': '12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Rouge', 'Vert', 'Bleu']
                    },
                    {
                        'model': 'iPhone 12 mini',
                        'price': 700000,
                        'os': 'iOS 14',
                        'screen': 5.4,
                        'resolution': '2340 x 1080',
                        'processor': 'A14 Bionic',
                        'ram': 4,
                        'storage': 256,
                        'battery': 2227,
                        'camera_main': '12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '5G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Rouge', 'Vert', 'Bleu']
                    },
                    # iPhone 11
                    {
                        'model': 'iPhone 11 Pro Max',
                        'price': 1100000,
                        'os': 'iOS 13',
                        'screen': 6.5,
                        'resolution': '2688 x 1242',
                        'processor': 'A13 Bionic',
                        'ram': 4,
                        'storage': 256,
                        'battery': 3969,
                        'camera_main': '12MP + 12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '4G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Or', 'Vert Minuit']
                    },
                    {
                        'model': 'iPhone 11 Pro',
                        'price': 900000,
                        'os': 'iOS 13',
                        'screen': 5.8,
                        'resolution': '2436 x 1125',
                        'processor': 'A13 Bionic',
                        'ram': 4,
                        'storage': 256,
                        'battery': 3046,
                        'camera_main': '12MP + 12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '4G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Or', 'Vert Minuit']
                    },
                    {
                        'model': 'iPhone 11',
                        'price': 700000,
                        'os': 'iOS 13',
                        'screen': 6.1,
                        'resolution': '1792 x 828',
                        'processor': 'A13 Bionic',
                        'ram': 4,
                        'storage': 256,
                        'battery': 3110,
                        'camera_main': '12MP + 12MP',
                        'camera_front': '12MP',
                        'network': '4G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Rouge', 'Vert', 'Jaune', 'Violet']
                    },
                    # iPhone XR
                    {
                        'model': 'iPhone XR',
                        'price': 600000,
                        'os': 'iOS 12',
                        'screen': 6.1,
                        'resolution': '1792 x 828',
                        'processor': 'A12 Bionic',
                        'ram': 3,
                        'storage': 256,
                        'battery': 2942,
                        'camera_main': '12MP',
                        'camera_front': '7MP',
                        'network': '4G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Rouge', 'Jaune', 'Bleu', 'Corail']
                    },
                    # iPhone X
                    {
                        'model': 'iPhone X',
                        'price': 800000,
                        'os': 'iOS 11',
                        'screen': 5.8,
                        'resolution': '2436 x 1125',
                        'processor': 'A11 Bionic',
                        'ram': 3,
                        'storage': 256,
                        'battery': 2716,
                        'camera_main': '12MP + 12MP',
                        'camera_front': '7MP',
                        'network': '4G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc']
                    },
                    # iPhone 8
                    {
                        'model': 'iPhone 8 Plus',
                        'price': 500000,
                        'os': 'iOS 11',
                        'screen': 5.5,
                        'resolution': '1920 x 1080',
                        'processor': 'A11 Bionic',
                        'ram': 3,
                        'storage': 256,
                        'battery': 2691,
                        'camera_main': '12MP + 12MP',
                        'camera_front': '7MP',
                        'network': '4G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Or', 'Rose Poudré']
                    },
                    {
                        'model': 'iPhone 8',
                        'price': 400000,
                        'os': 'iOS 11',
                        'screen': 4.7,
                        'resolution': '1334 x 750',
                        'processor': 'A11 Bionic',
                        'ram': 2,
                        'storage': 256,
                        'battery': 1821,
                        'camera_main': '12MP',
                        'camera_front': '7MP',
                        'network': '4G',
                        'warranty': '1 an',
                        'colors': ['Noir', 'Blanc', 'Or', 'Rose Poudré']
                    }
                ]

                # Ajouter chaque iPhone
                for iphone_data in iphones:
                    try:
                        # Vérifier si le produit existe déjà
                        product, created = Product.objects.get_or_create(
                            title=f"iPhone {iphone_data['model']}",
                            defaults={
                                'category': iphone_category,
                                'price': iphone_data['price'],
                                'description': f"iPhone {iphone_data['model']} - Le dernier smartphone d'Apple",
                                'highlight': "Écran Super Retina XDR, Processeur puissant, Appareil photo professionnel",
                                'supplier': apple_supplier
                            }
                        )

                        if created:
                            # Générer un IMEI unique
                            imei = str(uuid.uuid4().int)[:15]
                            
                            # Créer le téléphone uniquement si le produit est nouveau
                            phone = Phone.objects.create(
                                product=product,
                                model=iphone_data['model'],
                                operating_system=iphone_data['os'],
                                screen_size=iphone_data['screen'],
                                resolution=iphone_data['resolution'],
                                processor=iphone_data['processor'],
                                ram=iphone_data['ram'],
                                storage=iphone_data['storage'],
                                battery_capacity=iphone_data['battery'],
                                camera_main=iphone_data['camera_main'],
                                camera_front=iphone_data['camera_front'],
                                network=iphone_data['network'],
                                warranty=iphone_data['warranty'],
                                imei=imei,
                                is_new=True,
                                box_included=True,
                                accessories="Chargeur, Câble USB-C, Écouteurs, Manuel d'utilisation"
                            )

                            # Ajouter les couleurs
                            phone_colors = []
                            for color_name in iphone_data['colors']:
                                if color_name in color_objects:
                                    phone_colors.append(color_objects[color_name])
                                else:
                                    self.stdout.write(self.style.WARNING(f'Couleur {color_name} non trouvée pour l\'iPhone {iphone_data["model"]}'))
                            
                            # Ajouter toutes les couleurs en une seule fois
                            if phone_colors:
                                phone.color.set(phone_colors)
                                self.stdout.write(self.style.SUCCESS(f'Couleurs ajoutées pour l\'iPhone {iphone_data["model"]}: {", ".join([c.name for c in phone_colors])}'))

                            self.stdout.write(self.style.SUCCESS(f'iPhone {iphone_data["model"]} ajouté avec succès'))
                        else:
                            self.stdout.write(self.style.WARNING(f'iPhone {iphone_data["model"]} existe déjà, ignoré'))

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Erreur lors de la création de l\'iPhone {iphone_data["model"]}: {str(e)}'))
                        continue

                self.stdout.write(self.style.SUCCESS('Tous les iPhones ont été traités avec succès'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Une erreur est survenue: {str(e)}'))
            # Ne pas lever l'exception pour éviter le rollback
            pass 