import os
from django.conf import settings
from django.core.management.base import BaseCommand
from product.models import Category, Color, Product, Phone
from suppliers.models import Supplier
import json

class Command(BaseCommand):
    help = 'Importe les produits depuis un fichier JSON'

    def handle(self, *args, **options):
        # Obtenir le chemin absolu du fichier products.json
        base_dir = settings.BASE_DIR
        print(f"Répertoire de base : {base_dir}")
        print(f"Contenu du répertoire de base :")
        for item in os.listdir(base_dir):
            print(f"- {item}")

        json_path = os.path.join(base_dir, 'products.json')
        print(f"\nChemin du fichier JSON : {json_path}")
        print(f"Le fichier existe : {os.path.exists(json_path)}")

        if not os.path.exists(json_path):
            print("\nRecherche du fichier dans les sous-répertoires :")
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file == 'products.json':
                        json_path = os.path.join(root, file)
                        print(f"Fichier trouvé : {json_path}")
                        break

        if not os.path.exists(json_path):
            print("\nFichier products.json non trouvé")
            return

        try:
            print(f"\nLecture du fichier {json_path}")
            with open(json_path, 'r', encoding='utf-8') as file:
                content = file.read()
                print(f"Taille du contenu : {len(content)} caractères")
                print(f"Début du contenu :")
                print(content[:200] + "..." if len(content) > 200 else content)

                try:
                    data = json.loads(content)
                    print("\nParsing JSON réussi")
                    print(f"Type de données : {type(data)}")
                    if isinstance(data, dict):
                        print(f"Clés disponibles : {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"Nombre d'éléments : {len(data)}")
                        if data:
                            print(f"Premier élément : {data[0]}")
                except json.JSONDecodeError as e:
                    print(f"\nErreur lors du parsing JSON : {e}")
                    return

                # Créer le fournisseur Tecno s'il n'existe pas
                tecno_supplier, created = Supplier.objects.get_or_create(
                    name="Tecno",
                    defaults={
                        'description': "Fournisseur officiel Tecno",
                        'email': "contact@tecno.com",
                        'phone': "+22300000000",
                        'specialty': 'Fournisseur de TELEPHONE',
                        'slug': 'tecno'
                    }
                )
                print(f"\nFournisseur Tecno {'créé' if created else 'existant'} : {tecno_supplier}")

                # Créer le fournisseur par défaut s'il n'existe pas
                default_supplier, created = Supplier.objects.get_or_create(
                    name="Fournisseur par défaut",
                    defaults={
                        'description': "Fournisseur par défaut pour les produits",
                        'email': "contact@fournisseur.com",
                        'phone': "+22300000000",
                        'specialty': 'Fournisseur de TELEPHONE',
                        'slug': 'fournisseur-par-defaut'
                    }
                )
                print(f"\nFournisseur par défaut {'créé' if created else 'existant'} : {default_supplier}")

                # Importer les catégories
                categories_count = 0
                for category_data in data.get('categories', []):
                    category, created = Category.objects.get_or_create(
                        name=category_data['name'],
                        defaults={'description': category_data.get('description', '')}
                    )
                    if created:
                        categories_count += 1
                print(f"{categories_count} catégories importées avec succès")

                # Importer les couleurs
                colors_count = 0
                for color_data in data.get('colors', []):
                    color, created = Color.objects.get_or_create(
                        name=color_data['name'],
                        code=color_data.get('code', '#000000')
                    )
                    if created:
                        colors_count += 1
                print(f"{colors_count} couleurs importées avec succès")

                # Importer les produits
                products_count = 0
                for product_data in data.get('products', []):
                    try:
                        category = Category.objects.get(name=product_data['category'])
                        product, created = Product.objects.get_or_create(
                            name=product_data['name'],
                            defaults={
                                'description': product_data.get('description', ''),
                                'category': category,
                                'supplier': default_supplier
                            }
                        )
                        if created:
                            products_count += 1
                    except Category.DoesNotExist:
                        print(f"Catégorie {product_data['category']} non trouvée pour le produit {product_data['name']}")
                print(f"{products_count} produits importés avec succès")

                # Importer les téléphones
                phones_count = 0
                for phone_data in data.get('phones', []):
                    try:
                        product = Product.objects.get(name=phone_data['product'])
                        phone, created = Phone.objects.get_or_create(
                            product=product,
                            defaults={
                                'brand': phone_data.get('brand', ''),
                                'model': phone_data.get('model', ''),
                                'year': phone_data.get('year', 2024)
                            }
                        )
                        if created:
                            phones_count += 1
                    except Product.DoesNotExist:
                        print(f"Produit {phone_data['product']} non trouvé pour le téléphone")
                print(f"{phones_count} téléphones importés avec succès")

                # Importer les variantes de téléphones
                variants_count = 0
                for variant_data in data.get('variants', []):
                    try:
                        phone = Phone.objects.get(product__name=variant_data['phone'])
                        color = Color.objects.get(name=variant_data['color'])
                        variant, created = Phone.objects.get_or_create(
                            phone=phone,
                            color=color,
                            storage=variant_data.get('storage', '128GB'),
                            defaults={
                                'price': variant_data.get('price', 0),
                                'stock': variant_data.get('stock', 0)
                            }
                        )
                        if created:
                            variants_count += 1
                    except (Phone.DoesNotExist, Color.DoesNotExist) as e:
                        print(f"Erreur lors de l'importation de la variante : {e}")
                print(f"{variants_count} variantes de téléphones importées avec succès")

                print("\nRésumé de l'importation :")
                print(f"- {categories_count} catégories")
                print(f"- {colors_count} couleurs")
                print(f"- {products_count} produits")
                print(f"- {phones_count} téléphones")
                print(f"- {variants_count} variantes")

        except Exception as e:
            print(f"\nErreur lors de l'importation : {e}")
            raise 