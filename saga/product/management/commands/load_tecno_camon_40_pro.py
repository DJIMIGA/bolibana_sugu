from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from product.models import Product, Phone, Category, Color, Supplier
import json
import os

class Command(BaseCommand):
    help = 'Charge les téléphones TECNO CAMON 40 Pro 5G avec leurs couleurs spécifiques'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force le rechargement même si les données existent déjà',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Début du chargement des téléphones TECNO CAMON 40 Pro 5G...'))
        
        try:
            with transaction.atomic():
                # Étape 1: Charger les couleurs spécifiques
                self.stdout.write('📦 Chargement des couleurs spécifiques...')
                colors_fixture = os.path.join(
                    os.path.dirname(__file__), 
                    '..', '..', 'fixtures', 
                    'tecno_camon_40_pro_colors.json'
                )
                
                if os.path.exists(colors_fixture):
                    call_command('loaddata', colors_fixture, verbosity=0)
                    self.stdout.write(self.style.SUCCESS('✅ Couleurs chargées avec succès'))
                else:
                    self.stdout.write(self.style.WARNING('⚠️  Fichier de couleurs non trouvé, création manuelle...'))
                    self._create_colors_manually()
                
                # Étape 2: Charger les téléphones
                self.stdout.write('📱 Chargement des téléphones TECNO CAMON 40 Pro 5G...')
                phones_fixture = os.path.join(
                    os.path.dirname(__file__), 
                    '..', '..', 'fixtures', 
                    'tecno_camon_40_pro_phones.json'
                )
                
                if os.path.exists(phones_fixture):
                    call_command('loaddata', phones_fixture, verbosity=0)
                    self.stdout.write(self.style.SUCCESS('✅ Téléphones chargés avec succès'))
                else:
                    self.stdout.write(self.style.ERROR('❌ Fichier de téléphones non trouvé'))
                    return
                
                # Étape 3: Vérification et statistiques
                self._verify_and_display_stats()
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lors du chargement: {str(e)}'))
            return
        
        self.stdout.write(self.style.SUCCESS('🎉 Chargement terminé avec succès!'))

    def _create_colors_manually(self):
        """Crée les couleurs spécifiques aux téléphones TECNO CAMON 40 Pro 5G"""
        colors_data = [
            {"name": "Noir Galaxy", "code": "#1a1a1a"},
            {"name": "Vert Émeraude", "code": "#00a86b"},
            {"name": "Blanc Glacier", "code": "#f8f8ff"},
            {"name": "Titanium Sable", "code": "#8b7355"}
        ]
        
        for color_data in colors_data:
            color, created = Color.objects.get_or_create(
                name=color_data["name"],
                defaults={"code": color_data["code"]}
            )
            if created:
                self.stdout.write(f'  ✅ Couleur créée: {color_data["name"]}')
            else:
                self.stdout.write(f'  🔄 Couleur existante: {color_data["name"]}')

    def _verify_and_display_stats(self):
        """Vérifie les données chargées et affiche les statistiques"""
        # Compter les téléphones TECNO CAMON 40 Pro 5G
        tecno_phones = Phone.objects.filter(
            brand="TECNO",
            model="CAMON 40 Pro 5G"
        )
        
        total_phones = tecno_phones.count()
        variants_16gb = tecno_phones.filter(ram=16).count()
        variants_24gb = tecno_phones.filter(ram=24).count()
        
        # Compter les couleurs
        colors = Color.objects.filter(
            name__in=["Noir Galaxy", "Vert Émeraude", "Blanc Glacier", "Titanium Sable"]
        ).count()
        
        self.stdout.write('\n📊 Statistiques du chargement:')
        self.stdout.write(f'  📱 Total téléphones TECNO CAMON 40 Pro 5G: {total_phones}')
        self.stdout.write(f'  🔢 Variantes 16GB RAM: {variants_16gb}')
        self.stdout.write(f'  🔢 Variantes 24GB RAM: {variants_24gb}')
        self.stdout.write(f'  🎨 Couleurs spécifiques: {colors}')
        
        # Afficher les détails des variantes
        self.stdout.write('\n📋 Détails des variantes:')
        for phone in tecno_phones:
            product = phone.product
            self.stdout.write(
                f'  • {product.title} - {product.price} FCFA - Stock: {product.stock}'
            ) 