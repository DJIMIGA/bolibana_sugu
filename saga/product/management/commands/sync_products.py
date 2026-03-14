from django.core.management.base import BaseCommand
from product.models import Product, Phone
from django.db.models import Q
import json
import os
from django.core import serializers
import codecs

class Command(BaseCommand):
    help = 'Synchronise les données locales vers Heroku'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Synchroniser tous les produits',
        )
        parser.add_argument(
            '--brand',
            type=str,
            help='Filtrer par marque',
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Filtrer par modèle',
        )

    def handle(self, *args, **options):
        # Construire le filtre de base
        filters = Q()
        if options['brand']:
            filters &= Q(phone__brand__iexact=options['brand'])
        if options['model']:
            filters &= Q(phone__model__iexact=options['model'])

        # Récupérer les produits à synchroniser
        products = Product.objects.filter(filters)
        
        if not products.exists():
            self.stdout.write(self.style.WARNING('Aucun produit trouvé avec les filtres spécifiés'))
            return

        # Créer un fichier temporaire pour les données avec encodage UTF-8
        temp_file = 'temp_products.json'
        with codecs.open(temp_file, 'w', encoding='utf-8') as f:
            serializers.serialize('json', products, stream=f, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(f'{products.count()} produits exportés vers {temp_file}'))

        # Instructions pour l'utilisateur
        self.stdout.write(self.style.SUCCESS('\nPour synchroniser ces données sur Heroku :'))
        self.stdout.write('1. Copiez le fichier sur Heroku :')
        self.stdout.write(f'   heroku ps:copy {temp_file} -a bolibana-sugu')
        self.stdout.write('\n2. Exécutez la commande d\'import sur Heroku :')
        self.stdout.write('   heroku run python manage.py loaddata temp_products.json -a bolibana-sugu')
        self.stdout.write('\n3. Supprimez le fichier temporaire :')
        self.stdout.write(f'   rm {temp_file}')

        # Nettoyer le fichier temporaire local
        if os.path.exists(temp_file):
            os.remove(temp_file) 