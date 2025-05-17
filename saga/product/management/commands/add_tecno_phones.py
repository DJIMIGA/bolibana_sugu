from django.core.management.base import BaseCommand
from product.models import Product, Phone, Color, Category
from suppliers.models import Supplier
import json
import os

class Command(BaseCommand):
    help = 'Charge les téléphones Tecno depuis le fichier JSON'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("\n" + "="*80))
        self.stdout.write(self.style.SUCCESS("DÉBUT DU CHARGEMENT DES TÉLÉPHONES TECNO"))
        self.stdout.write(self.style.SUCCESS("="*80))

        # Chemin vers le fichier JSON
        fixtures_dir = os.path.join('saga', 'product', 'fixtures')
        fixture_path = os.path.join(fixtures_dir, 'tecno_phones.json')
        
        self.stdout.write(f"\n>>> Lecture du fichier : {fixture_path}")
        
        if not os.path.exists(fixture_path):
            self.stdout.write(self.style.ERROR(f"!!! ERREUR: Fichier {fixture_path} non trouvé !!!"))
            return

        # Lire le fichier JSON
        with open(fixture_path, 'r', encoding='utf-8') as f:
            phones_data = json.load(f)

        # Récupérer ou créer la catégorie Téléphones
        category, _ = Category.objects.get_or_create(
            name="Téléphones",
            defaults={'slug': 'telephones'}
        )

        # Récupérer ou créer le fournisseur Tecno
        supplier, _ = Supplier.objects.get_or_create(
            name="Tecno",
            defaults={
                'slug': 'tecno',
                'description': 'Fabricant de smartphones',
                'email': 'contact@tecno.com',
                'phone': '+243000000000'
            }
        )

        # Compteurs
        colors_created = 0
        products_created = 0
        phones_created = 0

        # Traiter chaque téléphone
        for phone_data in phones_data:
            # Créer ou récupérer la couleur
            color, created = Color.objects.get_or_create(
                name=phone_data['color'],
                defaults={'code': '#000000'}  # Code couleur par défaut
            )
            if created:
                colors_created += 1
                self.stdout.write(self.style.SUCCESS(f">>> Couleur créée : {color.name}"))

            # Créer le produit
            product, created = Product.objects.get_or_create(
                title=phone_data['name'],
                category=category,
                defaults={
                    'price': phone_data['price'],
                    'description': phone_data['description'],
                    'supplier': supplier,
                    'is_active': True,
                    'stock': phone_data['stock'],
                    'sku': phone_data['sku'],
                    'color': color
                }
            )
            if created:
                products_created += 1
                self.stdout.write(self.style.SUCCESS(f">>> Produit créé : {product.title}"))

                # Créer le téléphone
                phone = Phone.objects.create(
                    product=product,
                    brand='Tecno',
                    model=phone_data['model'],
                    operating_system=phone_data['operating_system'],
                    screen_size=phone_data['screen_size'],
                    resolution=phone_data['display'],
                    processor=phone_data['processor'],
                    battery_capacity=int(phone_data['battery'].replace('mAh', '')),
                    camera_main=phone_data['main_camera'],
                    camera_front=phone_data['front_camera'],
                    network='4G',
                    warranty='12 mois',
                    is_new=True,
                    box_included=True,
                    storage=phone_data['storage'],
                    ram=phone_data['ram'],
                    color=color
                )
                phones_created += 1
                self.stdout.write(self.style.SUCCESS(f">>> Téléphone créé : {phone.brand} {phone.model}"))

        # Afficher le résumé
        self.stdout.write(self.style.SUCCESS("\n" + "="*80))
        self.stdout.write(self.style.SUCCESS("RÉSUMÉ DU CHARGEMENT"))
        self.stdout.write(self.style.SUCCESS("="*80))
        self.stdout.write(f"\n>>> Couleurs créées : {colors_created}")
        self.stdout.write(f">>> Produits créés : {products_created}")
        self.stdout.write(f">>> Téléphones créés : {phones_created}")
        self.stdout.write(self.style.SUCCESS("\n" + "="*80))
        self.stdout.write(self.style.SUCCESS("FIN DU CHARGEMENT"))
        self.stdout.write(self.style.SUCCESS("="*80 + "\n")) 