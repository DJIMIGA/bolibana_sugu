from django.core.management.base import BaseCommand
from product.models import Product, Category, Phone, Color, Supplier
from django.utils import timezone
from decimal import Decimal
import json
import os
from django.conf import settings
import uuid

class Command(BaseCommand):
    help = 'Importe les téléphones Tecno depuis un fichier JSON'

    def handle(self, *args, **options):
        # Chemin vers le fichier JSON
        json_path = os.path.join('saga', 'product', 'fixtures', 'tecno_phones.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Fichier non trouvé: {json_path}'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Erreur de format JSON'))
            return
            
        # Récupérer ou créer la catégorie
        category, _ = Category.objects.get_or_create(
            name='Téléphones',
            defaults={'slug': 'telephones'}
        )
        
        # Récupérer ou créer le fournisseur
        supplier, _ = Supplier.objects.get_or_create(
            name='Tecno',
            defaults={'slug': 'tecno'}
        )
        
        for phone_data in data:
            # Créer ou récupérer la couleur
            color, _ = Color.objects.get_or_create(
                name=phone_data['color'],
                defaults={'code': '#000000'}  # Valeur par défaut
            )
            
            # Vérifier si le produit existe déjà par son SKU
            try:
                product = Product.objects.get(sku=phone_data['sku'])
                self.stdout.write(self.style.WARNING(f'Produit existant mis à jour: {product.title}'))
            except Product.DoesNotExist:
                # Créer un nouveau produit
                product = Product.objects.create(
                    title=phone_data['name'],
                    category=category,
                    supplier=supplier,
                    description=phone_data.get('description', ''),
                    price=Decimal(phone_data['price']),
                    stock=phone_data['stock'],
                    sku=phone_data['sku'],
                    is_active=True,
                    color=color
                )
                self.stdout.write(self.style.SUCCESS(f'Produit créé: {product.title}'))
            
            # Vérifier si le téléphone existe déjà
            try:
                phone = Phone.objects.get(product=product)
                self.stdout.write(self.style.WARNING(f'Téléphone existant mis à jour: {phone}'))
            except Phone.DoesNotExist:
                # Créer un nouveau téléphone
                phone = Phone.objects.create(
                    product=product,
                    brand='Tecno',
                    model=phone_data['model'],
                    operating_system=phone_data['operating_system'],
                    processor=phone_data['processor'],
                    screen_size=phone_data['screen_size'],
                    camera=phone_data['main_camera'],
                    battery=phone_data['battery'],
                    storage=phone_data['storage'],
                    ram=phone_data['ram'],
                    color=color,
                    is_new=True,
                    imei=str(uuid.uuid4())[:15]  # Génère un IMEI unique
                )
                self.stdout.write(self.style.SUCCESS(f'Téléphone créé: {phone}')) 