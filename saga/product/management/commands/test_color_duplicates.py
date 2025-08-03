from django.core.management.base import BaseCommand
from django.db import transaction
from product.models import Color, Phone, Fabric, Clothing, Product, Category


class Command(BaseCommand):
    help = 'Teste les commandes de nettoyage des doublons de couleurs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Nettoie les données de test après l\'exécution',
        )

    def handle(self, *args, **options):
        cleanup = options['cleanup']
        
        self.stdout.write('🧪 Test des commandes de nettoyage des doublons de couleurs...')
        
        # Créer des données de test
        test_data = self._create_test_data()
        
        try:
            # Tester la détection des doublons
            self._test_duplicate_detection()
            
            # Tester la migration des références
            self._test_reference_migration()
            
            self.stdout.write('✅ Tous les tests sont passés avec succès!')
            
        except Exception as e:
            self.stdout.write(f'❌ Erreur lors des tests: {str(e)}')
            raise
        finally:
            if cleanup:
                self._cleanup_test_data(test_data)
                self.stdout.write('🧹 Données de test nettoyées')

    def _create_test_data(self):
        """Crée des données de test avec des doublons"""
        test_data = {
            'colors': [],
            'products': [],
            'phones': [],
            'fabrics': [],
            'clothing': []
        }
        
        with transaction.atomic():
            # Créer une catégorie de test
            category = Category.objects.create(
                name='Test Category',
                slug='test-category'
            )
            test_data['category'] = category
            
            # Créer des couleurs avec doublons
            color1 = Color.objects.create(name='Édition Loewe', code='#1a1a1a')
            color2 = Color.objects.create(name='Édition LOEWE', code='#1a1a1a')
            color3 = Color.objects.create(name='edition loewe', code='#1a1a1a')
            
            test_data['colors'].extend([color1, color2, color3])
            
            # Créer des produits de test
            product1 = Product.objects.create(
                title='Test Phone',
                price=100000,
                category=category,
                brand='Test Brand'
            )
            product2 = Product.objects.create(
                title='Test Fabric',
                price=50000,
                category=category,
                brand='Test Brand'
            )
            product3 = Product.objects.create(
                title='Test Clothing',
                price=25000,
                category=category,
                brand='Test Brand'
            )
            
            test_data['products'].extend([product1, product2, product3])
            
            # Créer un téléphone avec une couleur
            phone = Phone.objects.create(
                product=product1,
                brand='Test Brand',
                model='Test Model',
                color=color2  # Utiliser le doublon
            )
            test_data['phones'].append(phone)
            
            # Créer un tissu avec une couleur
            fabric = Fabric.objects.create(
                product=product2,
                fabric_type='BAZIN',
                color=color3  # Utiliser le doublon
            )
            test_data['fabrics'].append(fabric)
            
            # Créer un vêtement avec une couleur
            clothing = Clothing.objects.create(
                product=product3,
                gender='U'
            )
            clothing.color.add(color1)  # Utiliser le doublon
            test_data['clothing'].append(clothing)
        
        self.stdout.write('📝 Données de test créées:')
        self.stdout.write(f'  - {len(test_data["colors"])} couleurs (avec doublons)')
        self.stdout.write(f'  - {len(test_data["products"])} produits')
        self.stdout.write(f'  - {len(test_data["phones"])} téléphone(s)')
        self.stdout.write(f'  - {len(test_data["fabrics"])} tissu(x)')
        self.stdout.write(f'  - {len(test_data["clothing"])} vêtement(s)')
        
        return test_data

    def _test_duplicate_detection(self):
        """Teste la détection des doublons"""
        self.stdout.write('\n🔍 Test de détection des doublons...')
        
        # Vérifier qu'il y a bien des doublons
        loewe_colors = Color.objects.filter(name__iexact='Édition Loewe')
        count = loewe_colors.count()
        
        if count >= 2:
            self.stdout.write(f'✅ {count} doublons détectés pour "Édition Loewe"')
        else:
            raise Exception(f'Attendu au moins 2 doublons, trouvé {count}')

    def _test_reference_migration(self):
        """Teste la migration des références"""
        self.stdout.write('\n🔄 Test de migration des références...')
        
        # Identifier la couleur principale (la plus ancienne)
        primary_color = Color.objects.filter(name__iexact='Édition Loewe').order_by('id').first()
        duplicate_colors = Color.objects.filter(name__iexact='Édition Loewe').exclude(id=primary_color.id)
        
        # Vérifier les références avant migration
        total_references_before = 0
        for duplicate in duplicate_colors:
            phones_count = Phone.objects.filter(color=duplicate).count()
            fabrics_count = Fabric.objects.filter(color=duplicate).count()
            clothing_count = Clothing.objects.filter(color=duplicate).count()
            total_references_before += phones_count + fabrics_count + clothing_count
        
        self.stdout.write(f'📊 Références avant migration: {total_references_before}')
        
        # Simuler la migration
        with transaction.atomic():
            for duplicate in duplicate_colors:
                # Migrer les téléphones
                Phone.objects.filter(color=duplicate).update(color=primary_color)
                
                # Migrer les tissus
                Fabric.objects.filter(color=duplicate).update(color=primary_color)
                
                # Migrer les vêtements
                clothing_with_old_color = Clothing.objects.filter(color=duplicate)
                for clothing in clothing_with_old_color:
                    clothing.color.add(primary_color)
                    clothing.color.remove(duplicate)
        
        # Vérifier les références après migration
        total_references_after = (
            Phone.objects.filter(color=primary_color).count() +
            Fabric.objects.filter(color=primary_color).count() +
            Clothing.objects.filter(color=primary_color).count()
        )
        
        self.stdout.write(f'📊 Références après migration: {total_references_after}')
        
        if total_references_after == total_references_before:
            self.stdout.write('✅ Migration des références réussie')
        else:
            raise Exception(f'Migration échouée: {total_references_before} -> {total_references_after}')

    def _cleanup_test_data(self, test_data):
        """Nettoie les données de test"""
        with transaction.atomic():
            # Supprimer dans l'ordre inverse des dépendances
            for clothing in test_data['clothing']:
                clothing.delete()
            
            for fabric in test_data['fabrics']:
                fabric.delete()
            
            for phone in test_data['phones']:
                phone.delete()
            
            for product in test_data['products']:
                product.delete()
            
            for color in test_data['colors']:
                color.delete()
            
            if 'category' in test_data:
                test_data['category'].delete() 