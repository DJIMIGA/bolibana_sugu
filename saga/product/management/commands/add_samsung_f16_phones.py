from django.core.management.base import BaseCommand
from product.models import Product, Phone, Category, Color, Supplier

class Command(BaseCommand):
    help = 'Ajoute les téléphones Samsung Galaxy F16 avec toutes les variantes'

    def handle(self, *args, **options):
        # Données des téléphones Samsung Galaxy F16
        phones_data = [
            {
                "description": "Le Samsung Galaxy F16 est un smartphone premium avec un écran de 6.7 pouces et une résolution Full HD+. Équipé du système Android 15 avec One UI 7, il offre une expérience utilisateur fluide et moderne.\n\nCaractéristiques principales :\n- Écran 6.7 pouces (1080 x 2340 pixels)\n- Processeur Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)\n- GPU Mali-G57 MC2\n- Système Android 15 avec One UI 7\n- Support microSDXC (shared SIM slot)\n- Dimensions : 164.4 x 77.9 x 7.9 mm\n- Poids : 191 grammes\n\nConnectivité :\n- 4G LTE\n- WiFi\n- Bluetooth\n- GPS\n\nContenu de la boîte :\n- Téléphone Samsung Galaxy F16\n- Chargeur adaptatif\n- Câble USB-C\n- Écouteurs (selon disponibilité)\n- Guide d'utilisation",
                "price": 95000,
                "brand": "Samsung",
                "model": "Galaxy F16",
                "operating_system": "Android 15, One UI 7",
                "screen_size": 6.7,
                "resolution": "1080x2340",
                "processor": "Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)",
                "battery_capacity": 5000,
                "camera_main": "50MP + 8MP + 2MP",
                "camera_front": "13MP",
                "network": "4G LTE",
                "storage": 128,
                "ram": 4,
                "color": "Noir Brillant",
                "stock": 25,
                "sku": "SAM-F16-128-4-NB",
                "is_new": True,
                "box_included": True,
                "accessories": "Téléphone, Chargeur, Câble USB-C, Écouteurs",
                "condition": "new",
                "has_warranty": True,
                "is_trending": True
            },
            {
                "description": "Le Samsung Galaxy F16 est un smartphone premium avec un écran de 6.7 pouces et une résolution Full HD+. Équipé du système Android 15 avec One UI 7, il offre une expérience utilisateur fluide et moderne.\n\nCaractéristiques principales :\n- Écran 6.7 pouces (1080 x 2340 pixels)\n- Processeur Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)\n- GPU Mali-G57 MC2\n- Système Android 15 avec One UI 7\n- Support microSDXC (shared SIM slot)\n- Dimensions : 164.4 x 77.9 x 7.9 mm\n- Poids : 191 grammes\n\nConnectivité :\n- 4G LTE\n- WiFi\n- Bluetooth\n- GPS\n\nContenu de la boîte :\n- Téléphone Samsung Galaxy F16\n- Chargeur adaptatif\n- Câble USB-C\n- Écouteurs (selon disponibilité)\n- Guide d'utilisation",
                "price": 105000,
                "brand": "Samsung",
                "model": "Galaxy F16",
                "operating_system": "Android 15, One UI 7",
                "screen_size": 6.7,
                "resolution": "1080x2340",
                "processor": "Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)",
                "battery_capacity": 5000,
                "camera_main": "50MP + 8MP + 2MP",
                "camera_front": "13MP",
                "network": "4G LTE",
                "storage": 128,
                "ram": 6,
                "color": "Noir Brillant",
                "stock": 20,
                "sku": "SAM-F16-128-6-NB",
                "is_new": True,
                "box_included": True,
                "accessories": "Téléphone, Chargeur, Câble USB-C, Écouteurs",
                "condition": "new",
                "has_warranty": True,
                "is_trending": True
            },
            {
                "description": "Le Samsung Galaxy F16 est un smartphone premium avec un écran de 6.7 pouces et une résolution Full HD+. Équipé du système Android 15 avec One UI 7, il offre une expérience utilisateur fluide et moderne.\n\nCaractéristiques principales :\n- Écran 6.7 pouces (1080 x 2340 pixels)\n- Processeur Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)\n- GPU Mali-G57 MC2\n- Système Android 15 avec One UI 7\n- Support microSDXC (shared SIM slot)\n- Dimensions : 164.4 x 77.9 x 7.9 mm\n- Poids : 191 grammes\n\nConnectivité :\n- 4G LTE\n- WiFi\n- Bluetooth\n- GPS\n\nContenu de la boîte :\n- Téléphone Samsung Galaxy F16\n- Chargeur adaptatif\n- Câble USB-C\n- Écouteurs (selon disponibilité)\n- Guide d'utilisation",
                "price": 115000,
                "brand": "Samsung",
                "model": "Galaxy F16",
                "operating_system": "Android 15, One UI 7",
                "screen_size": 6.7,
                "resolution": "1080x2340",
                "processor": "Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)",
                "battery_capacity": 5000,
                "camera_main": "50MP + 8MP + 2MP",
                "camera_front": "13MP",
                "network": "4G LTE",
                "storage": 128,
                "ram": 8,
                "color": "Noir Brillant",
                "stock": 15,
                "sku": "SAM-F16-128-8-NB",
                "is_new": True,
                "box_included": True,
                "accessories": "Téléphone, Chargeur, Câble USB-C, Écouteurs",
                "condition": "new",
                "has_warranty": True,
                "is_trending": True
            },
            {
                "description": "Le Samsung Galaxy F16 est un smartphone premium avec un écran de 6.7 pouces et une résolution Full HD+. Équipé du système Android 15 avec One UI 7, il offre une expérience utilisateur fluide et moderne.\n\nCaractéristiques principales :\n- Écran 6.7 pouces (1080 x 2340 pixels)\n- Processeur Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)\n- GPU Mali-G57 MC2\n- Système Android 15 avec One UI 7\n- Support microSDXC (shared SIM slot)\n- Dimensions : 164.4 x 77.9 x 7.9 mm\n- Poids : 191 grammes\n\nConnectivité :\n- 4G LTE\n- WiFi\n- Bluetooth\n- GPS\n\nContenu de la boîte :\n- Téléphone Samsung Galaxy F16\n- Chargeur adaptatif\n- Câble USB-C\n- Écouteurs (selon disponibilité)\n- Guide d'utilisation",
                "price": 95000,
                "brand": "Samsung",
                "model": "Galaxy F16",
                "operating_system": "Android 15, One UI 7",
                "screen_size": 6.7,
                "resolution": "1080x2340",
                "processor": "Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)",
                "battery_capacity": 5000,
                "camera_main": "50MP + 8MP + 2MP",
                "camera_front": "13MP",
                "network": "4G LTE",
                "storage": 128,
                "ram": 4,
                "color": "Bleu Vibrant",
                "stock": 20,
                "sku": "SAM-F16-128-4-BV",
                "is_new": True,
                "box_included": True,
                "accessories": "Téléphone, Chargeur, Câble USB-C, Écouteurs",
                "condition": "new",
                "has_warranty": True,
                "is_trending": True
            },
            {
                "description": "Le Samsung Galaxy F16 est un smartphone premium avec un écran de 6.7 pouces et une résolution Full HD+. Équipé du système Android 15 avec One UI 7, il offre une expérience utilisateur fluide et moderne.\n\nCaractéristiques principales :\n- Écran 6.7 pouces (1080 x 2340 pixels)\n- Processeur Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)\n- GPU Mali-G57 MC2\n- Système Android 15 avec One UI 7\n- Support microSDXC (shared SIM slot)\n- Dimensions : 164.4 x 77.9 x 7.9 mm\n- Poids : 191 grammes\n\nConnectivité :\n- 4G LTE\n- WiFi\n- Bluetooth\n- GPS\n\nContenu de la boîte :\n- Téléphone Samsung Galaxy F16\n- Chargeur adaptatif\n- Câble USB-C\n- Écouteurs (selon disponibilité)\n- Guide d'utilisation",
                "price": 105000,
                "brand": "Samsung",
                "model": "Galaxy F16",
                "operating_system": "Android 15, One UI 7",
                "screen_size": 6.7,
                "resolution": "1080x2340",
                "processor": "Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)",
                "battery_capacity": 5000,
                "camera_main": "50MP + 8MP + 2MP",
                "camera_front": "13MP",
                "network": "4G LTE",
                "storage": 128,
                "ram": 6,
                "color": "Bleu Vibrant",
                "stock": 18,
                "sku": "SAM-F16-128-6-BV",
                "is_new": True,
                "box_included": True,
                "accessories": "Téléphone, Chargeur, Câble USB-C, Écouteurs",
                "condition": "new",
                "has_warranty": True,
                "is_trending": True
            },
            {
                "description": "Le Samsung Galaxy F16 est un smartphone premium avec un écran de 6.7 pouces et une résolution Full HD+. Équipé du système Android 15 avec One UI 7, il offre une expérience utilisateur fluide et moderne.\n\nCaractéristiques principales :\n- Écran 6.7 pouces (1080 x 2340 pixels)\n- Processeur Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)\n- GPU Mali-G57 MC2\n- Système Android 15 avec One UI 7\n- Support microSDXC (shared SIM slot)\n- Dimensions : 164.4 x 77.9 x 7.9 mm\n- Poids : 191 grammes\n\nConnectivité :\n- 4G LTE\n- WiFi\n- Bluetooth\n- GPS\n\nContenu de la boîte :\n- Téléphone Samsung Galaxy F16\n- Chargeur adaptatif\n- Câble USB-C\n- Écouteurs (selon disponibilité)\n- Guide d'utilisation",
                "price": 115000,
                "brand": "Samsung",
                "model": "Galaxy F16",
                "operating_system": "Android 15, One UI 7",
                "screen_size": 6.7,
                "resolution": "1080x2340",
                "processor": "Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)",
                "battery_capacity": 5000,
                "camera_main": "50MP + 8MP + 2MP",
                "camera_front": "13MP",
                "network": "4G LTE",
                "storage": 128,
                "ram": 8,
                "color": "Bleu Vibrant",
                "stock": 12,
                "sku": "SAM-F16-128-8-BV",
                "is_new": True,
                "box_included": True,
                "accessories": "Téléphone, Chargeur, Câble USB-C, Écouteurs",
                "condition": "new",
                "has_warranty": True,
                "is_trending": True
            },
            {
                "description": "Le Samsung Galaxy F16 est un smartphone premium avec un écran de 6.7 pouces et une résolution Full HD+. Équipé du système Android 15 avec One UI 7, il offre une expérience utilisateur fluide et moderne.\n\nCaractéristiques principales :\n- Écran 6.7 pouces (1080 x 2340 pixels)\n- Processeur Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)\n- GPU Mali-G57 MC2\n- Système Android 15 avec One UI 7\n- Support microSDXC (shared SIM slot)\n- Dimensions : 164.4 x 77.9 x 7.9 mm\n- Poids : 191 grammes\n\nConnectivité :\n- 4G LTE\n- WiFi\n- Bluetooth\n- GPS\n\nContenu de la boîte :\n- Téléphone Samsung Galaxy F16\n- Chargeur adaptatif\n- Câble USB-C\n- Écouteurs (selon disponibilité)\n- Guide d'utilisation",
                "price": 95000,
                "brand": "Samsung",
                "model": "Galaxy F16",
                "operating_system": "Android 15, One UI 7",
                "screen_size": 6.7,
                "resolution": "1080x2340",
                "processor": "Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)",
                "battery_capacity": 5000,
                "camera_main": "50MP + 8MP + 2MP",
                "camera_front": "13MP",
                "network": "4G LTE",
                "storage": 128,
                "ram": 4,
                "color": "Vert Glamour",
                "stock": 15,
                "sku": "SAM-F16-128-4-VG",
                "is_new": True,
                "box_included": True,
                "accessories": "Téléphone, Chargeur, Câble USB-C, Écouteurs",
                "condition": "new",
                "has_warranty": True,
                "is_trending": True
            },
            {
                "description": "Le Samsung Galaxy F16 est un smartphone premium avec un écran de 6.7 pouces et une résolution Full HD+. Équipé du système Android 15 avec One UI 7, il offre une expérience utilisateur fluide et moderne.\n\nCaractéristiques principales :\n- Écran 6.7 pouces (1080 x 2340 pixels)\n- Processeur Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)\n- GPU Mali-G57 MC2\n- Système Android 15 avec One UI 7\n- Support microSDXC (shared SIM slot)\n- Dimensions : 164.4 x 77.9 x 7.9 mm\n- Poids : 191 grammes\n\nConnectivité :\n- 4G LTE\n- WiFi\n- Bluetooth\n- GPS\n\nContenu de la boîte :\n- Téléphone Samsung Galaxy F16\n- Chargeur adaptatif\n- Câble USB-C\n- Écouteurs (selon disponibilité)\n- Guide d'utilisation",
                "price": 105000,
                "brand": "Samsung",
                "model": "Galaxy F16",
                "operating_system": "Android 15, One UI 7",
                "screen_size": 6.7,
                "resolution": "1080x2340",
                "processor": "Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)",
                "battery_capacity": 5000,
                "camera_main": "50MP + 8MP + 2MP",
                "camera_front": "13MP",
                "network": "4G LTE",
                "storage": 128,
                "ram": 6,
                "color": "Vert Glamour",
                "stock": 12,
                "sku": "SAM-F16-128-6-VG",
                "is_new": True,
                "box_included": True,
                "accessories": "Téléphone, Chargeur, Câble USB-C, Écouteurs",
                "condition": "new",
                "has_warranty": True,
                "is_trending": True
            },
            {
                "description": "Le Samsung Galaxy F16 est un smartphone premium avec un écran de 6.7 pouces et une résolution Full HD+. Équipé du système Android 15 avec One UI 7, il offre une expérience utilisateur fluide et moderne.\n\nCaractéristiques principales :\n- Écran 6.7 pouces (1080 x 2340 pixels)\n- Processeur Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)\n- GPU Mali-G57 MC2\n- Système Android 15 avec One UI 7\n- Support microSDXC (shared SIM slot)\n- Dimensions : 164.4 x 77.9 x 7.9 mm\n- Poids : 191 grammes\n\nConnectivité :\n- 4G LTE\n- WiFi\n- Bluetooth\n- GPS\n\nContenu de la boîte :\n- Téléphone Samsung Galaxy F16\n- Chargeur adaptatif\n- Câble USB-C\n- Écouteurs (selon disponibilité)\n- Guide d'utilisation",
                "price": 115000,
                "brand": "Samsung",
                "model": "Galaxy F16",
                "operating_system": "Android 15, One UI 7",
                "screen_size": 6.7,
                "resolution": "1080x2340",
                "processor": "Octa-core (2x2.4 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)",
                "battery_capacity": 5000,
                "camera_main": "50MP + 8MP + 2MP",
                "camera_front": "13MP",
                "network": "4G LTE",
                "storage": 128,
                "ram": 8,
                "color": "Vert Glamour",
                "stock": 8,
                "sku": "SAM-F16-128-8-VG",
                "is_new": True,
                "box_included": True,
                "accessories": "Téléphone, Chargeur, Câble USB-C, Écouteurs",
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
                    storage = phone_data.get('storage', 128)
                    ram = phone_data.get('ram', 4)
                    color_name = phone_data.get('color', 'Noir Brillant')
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