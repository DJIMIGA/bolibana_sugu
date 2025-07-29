from django.core.management.base import BaseCommand
from product.models import Product, Phone, Category, Color, Supplier

class Command(BaseCommand):
    help = 'Ajoute les téléphones TECNO CAMON 40 Premier 5G avec toutes les variantes'

    def handle(self, *args, **options):
        # Données des téléphones TECNO CAMON 40 Premier 5G
        phones_data = [
            {
                "description": "Le TECNO CAMON 40 Premier 5G est un smartphone premium avec un écran AMOLED de 6.67 pouces et une résolution de 1260 x 2800 pixels. Équipé du système Android 15 et du processeur MediaTek Dimensity 8350 Ultimate AI, il offre une expérience utilisateur exceptionnelle.\n\nCaractéristiques principales :\n- Écran 6.67 pouces AMOLED 144 Hz (1260 x 2800 pixels)\n- Processeur MediaTek Dimensity 8350 Ultimate AI\n- Système Android 15\n- Support 2G/3G/4G/5G\n- Dimensions : 161 x 75 x 7.7 mm\n- Poids : ~200 grammes\n\nCaméras :\n- Caméra frontale : 50 MP AF\n- Caméra arrière : 50 MP 1/1.56\" OIS + 50 MP 3X + 50 MP Wide-angle\n- Double Flash + Capteur Flicker\n\nMémoire :\n- 256GB ROM + 24GB RAM (12GB + 12GB Extended)\n\nConnectivité :\n- Wi-Fi\n- Bluetooth\n- FM\n- GPS\n- NFC\n- Port Type-C\n- OTG\n\nCapteurs :\n- Capteur géomagnétique\n- Capteur A+G\n- Capteur de lumière ambiante et de distance\n- Télécommande infrarouge\n- Boussole électronique\n\nBatterie :\n- 5100 mAh\n- Charge ultra-rapide 70W\n\nAudio :\n- Haut-parleurs doubles\n- Dolby Atmos\n\nContenu de la boîte :\n- Téléphone TECNO CAMON 40 Premier 5G\n- Chargeur adaptatif 70W\n- Câble USB-C\n- Écouteurs (selon disponibilité)\n- Guide d'utilisation",
                "price": 200000,
                "brand": "TECNO",
                "model": "CAMON 40 Premier 5G",
                "operating_system": "Android 15",
                "screen_size": 6.67,
                "resolution": "1260x2800",
                "processor": "MediaTek Dimensity 8350 Ultimate AI Processor",
                "battery_capacity": 5100,
                "camera_main": "50 MP 1/1.56\" OIS + 50 MP 3X + 50 MP Wide-angle",
                "camera_front": "50 MP AF",
                "network": "2G/3G/4G/5G",
                "storage": 256,
                "ram": 24,
                "color": "Noir Galaxy",
                "stock": 20,
                "sku": "TEC-C40P-256-24-NG",
                "is_new": True,
                "box_included": True,
                "accessories": "Téléphone, Chargeur 70W, Câble USB-C, Écouteurs",
                "condition": "new",
                "has_warranty": True,
                "is_trending": True
            },
            {
                "description": "Le TECNO CAMON 40 Premier 5G est un smartphone premium avec un écran AMOLED de 6.67 pouces et une résolution de 1260 x 2800 pixels. Équipé du système Android 15 et du processeur MediaTek Dimensity 8350 Ultimate AI, il offre une expérience utilisateur exceptionnelle.\n\nCaractéristiques principales :\n- Écran 6.67 pouces AMOLED 144 Hz (1260 x 2800 pixels)\n- Processeur MediaTek Dimensity 8350 Ultimate AI\n- Système Android 15\n- Support 2G/3G/4G/5G\n- Dimensions : 161 x 75 x 7.7 mm\n- Poids : ~200 grammes\n\nCaméras :\n- Caméra frontale : 50 MP AF\n- Caméra arrière : 50 MP 1/1.56\" OIS + 50 MP 3X + 50 MP Wide-angle\n- Double Flash + Capteur Flicker\n\nMémoire :\n- 256GB ROM + 24GB RAM (12GB + 12GB Extended)\n\nConnectivité :\n- Wi-Fi\n- Bluetooth\n- FM\n- GPS\n- NFC\n- Port Type-C\n- OTG\n\nCapteurs :\n- Capteur géomagnétique\n- Capteur A+G\n- Capteur de lumière ambiante et de distance\n- Télécommande infrarouge\n- Boussole électronique\n\nBatterie :\n- 5100 mAh\n- Charge ultra-rapide 70W\n\nAudio :\n- Haut-parleurs doubles\n- Dolby Atmos\n\nContenu de la boîte :\n- Téléphone TECNO CAMON 40 Premier 5G\n- Chargeur adaptatif 70W\n- Câble USB-C\n- Écouteurs (selon disponibilité)\n- Guide d'utilisation",
                "price": 200000,
                "brand": "TECNO",
                "model": "CAMON 40 Premier 5G",
                "operating_system": "Android 15",
                "screen_size": 6.67,
                "resolution": "1260x2800",
                "processor": "MediaTek Dimensity 8350 Ultimate AI Processor",
                "battery_capacity": 5100,
                "camera_main": "50 MP 1/1.56\" OIS + 50 MP 3X + 50 MP Wide-angle",
                "camera_front": "50 MP AF",
                "network": "2G/3G/4G/5G",
                "storage": 256,
                "ram": 24,
                "color": "Vert Émeraude",
                "stock": 15,
                "sku": "TEC-C40P-256-24-VE",
                "is_new": True,
                "box_included": True,
                "accessories": "Téléphone, Chargeur 70W, Câble USB-C, Écouteurs",
                "condition": "new",
                "has_warranty": True,
                "is_trending": True
            }
        ]

        try:
            # Récupérer la catégorie et le fournisseur
            category = Category.objects.get(id=1)  # Catégorie téléphones
            supplier = Supplier.objects.get(id=1)  # Fournisseur par défaut

            phones_created = 0
            phones_updated = 0

            for phone_data in phones_data:
                try:
                    # Extraire les données pour le titre unique
                    storage = phone_data.get('storage', 256)
                    ram = phone_data.get('ram', 24)
                    color_name = phone_data.get('color', 'Noir Galaxy')
                    brand = phone_data['brand']
                    model = phone_data['model']
                    
                    # Générer un titre unique avec ROM, RAM et couleur
                    unique_title = f"{brand} {model} {storage}GB {ram}GB {color_name}"
                    
                    # Créer ou mettre à jour le produit
                    product, product_created = Product.objects.update_or_create(
                        title=unique_title,
                        defaults={
                            'description': phone_data.get('description', ''),
                            'price': phone_data['price'],
                            'category': category,
                            'supplier': supplier,
                            'brand': brand,
                            'is_available': phone_data.get('is_available', True),
                            'stock': phone_data.get('stock', 0),
                            'sku': phone_data.get('sku', ''),
                            'condition': phone_data.get('condition', 'new'),
                            'has_warranty': phone_data.get('has_warranty', True),
                            'discount_price': phone_data.get('discount_price'),
                            'is_trending': phone_data.get('is_trending', False),
                        }
                    )

                    # Obtenir la couleur
                    color = Color.objects.get(name=color_name)

                    # Créer ou mettre à jour le téléphone
                    phone, phone_created = Phone.objects.update_or_create(
                        product=product,
                        defaults={
                            'brand': brand,
                            'model': model,
                            'operating_system': phone_data.get('operating_system', 'Android'),
                            'screen_size': phone_data.get('screen_size', 6.0),
                            'resolution': phone_data.get('resolution', '1920x1080'),
                            'processor': phone_data.get('processor', 'Inconnu'),
                            'battery_capacity': phone_data.get('battery_capacity', 3000),
                            'camera_main': phone_data.get('camera_main', 'Inconnue'),
                            'camera_front': phone_data.get('camera_front', 'Inconnue'),
                            'network': phone_data.get('network', '4G'),
                            'imei': phone_data.get('imei'),
                            'is_new': phone_data.get('is_new', True),
                            'box_included': phone_data.get('box_included', True),
                            'accessories': phone_data.get('accessories', ''),
                            'storage': storage,
                            'ram': ram,
                            'color': color,
                        }
                    )

                    if phone_created:
                        phones_created += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Téléphone créé: {unique_title}')
                        )
                    else:
                        phones_updated += 1
                        self.stdout.write(
                            self.style.WARNING(f'🔄 Téléphone mis à jour: {unique_title}')
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Erreur avec {phone_data.get("title", "Téléphone inconnu")}: {str(e)}')
                    )

            self.stdout.write(self.style.SUCCESS(
                f'\n📱 Résumé: {phones_created} téléphones créés, {phones_updated} mis à jour'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur générale: {str(e)}')) 