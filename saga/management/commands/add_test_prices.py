from django.core.management.base import BaseCommand
from decimal import Decimal
from datetime import datetime, timedelta
import random
from price_checker.models import PriceSubmission, PriceEntry, City
from product.models import Product
from accounts.models import Shopper

class Command(BaseCommand):
    help = 'Ajouter des prix de test au comparateur de prix'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer l\'ajout même si des prix existent déjà',
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 Ajout de prix de test au comparateur de prix")
        self.stdout.write("=" * 50)
        
        # Afficher les statistiques avant
        self.show_statistics()
        
        # Vérifier s'il y a déjà des prix
        existing_prices = PriceSubmission.objects.count()
        if existing_prices > 0 and not options['force']:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠️  {existing_prices} prix existent déjà. "
                    "Utilisez --force pour ajouter des prix supplémentaires."
                )
            )
            return
        
        # Créer les prix de test
        self.create_test_prices()
        
        self.stdout.write("\n" + "=" * 50)
        self.show_statistics()

    def create_test_prices(self):
        """Créer des prix de test pour différents produits"""
        
        # Créer ou récupérer la ville Bamako
        city, created = City.objects.get_or_create(
            name='Bamako',
            defaults={
                'slug': 'bamako',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f"✅ Ville créée: {city.name}")
        else:
            self.stdout.write(f"✅ Ville utilisée: {city.name}")
        
        # Récupérer quelques produits existants
        products = Product.objects.all()[:10]  # Prendre les 10 premiers produits
        
        if not products.exists():
            self.stdout.write(
                self.style.ERROR("❌ Aucun produit trouvé dans la base de données")
            )
            return
        
        # Fournisseurs de test
        suppliers = [
            {
                'name': 'ElectroPlus',
                'phone': '+223 20 12 34 56',
                'address': 'Hamdallaye ACI 2000, Bamako'
            },
            {
                'name': 'TechMall',
                'phone': '+223 20 98 76 54',
                'address': 'Badalabougou, Bamako'
            },
            {
                'name': 'DigitalStore',
                'phone': '+223 20 45 67 89',
                'address': 'Faladié, Bamako'
            },
            {
                'name': 'SmartElectronics',
                'phone': '+223 20 11 22 33',
                'address': 'Sikasso, Mali'
            },
            {
                'name': 'GadgetWorld',
                'phone': '+223 20 44 55 66',
                'address': 'Ségou, Mali'
            }
        ]
        
        # Prix de base pour différents types de produits
        base_prices = {
            'phone': {'min': 50000, 'max': 150000},
            'laptop': {'min': 200000, 'max': 500000},
            'tablet': {'min': 80000, 'max': 200000},
            'accessory': {'min': 5000, 'max': 25000}
        }
        
        created_count = 0
        
        for product in products:
            # Créer 2-4 soumissions par produit
            num_submissions = random.randint(2, 4)
            
            for i in range(num_submissions):
                # Choisir un fournisseur aléatoire
                supplier = random.choice(suppliers)
                
                # Déterminer le type de produit pour le prix
                product_type = 'accessory'  # par défaut
                if 'phone' in product.title.lower() or 'téléphone' in product.title.lower():
                    product_type = 'phone'
                elif 'laptop' in product.title.lower() or 'ordinateur' in product.title.lower():
                    product_type = 'laptop'
                elif 'tablet' in product.title.lower():
                    product_type = 'tablet'
                
                # Générer un prix aléatoire
                price_range = base_prices[product_type]
                price = random.randint(price_range['min'], price_range['max'])
                
                # Statut aléatoire (majorité validés)
                status = random.choices(['APPROVED', 'PENDING'], weights=[0.75, 0.25])[0]
                
                # Créer la soumission
                submission = PriceSubmission.objects.create(
                    product=product,
                    city=city,  # Utiliser la ville Bamako créée
                    price=price,
                    supplier_name=supplier['name'],
                    supplier_phone=supplier['phone'],
                    supplier_address=supplier['address'],
                    user=Shopper.objects.first(),  # à adapter selon la logique métier
                    status=status,
                )
                created_count += 1
                self.stdout.write(
                    f"✅ Prix ajouté: {product.title} - {supplier['name']} - {price:,} FCFA (statut: {status})"
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"\n🎉 {created_count} prix de test ont été créés avec succès!")
        )
        self.stdout.write(f"📊 Répartition:")
        self.stdout.write(f"   - Ville: {city.name}")
        self.stdout.write(f"   - Produits: {products.count()}")
        self.stdout.write(f"   - Fournisseurs: {len(suppliers)}")
        self.stdout.write(f"   - Prix créés: {created_count}")

    def show_statistics(self):
        """Afficher les statistiques des prix"""
        total_submissions = PriceSubmission.objects.count()
        approved_submissions = PriceSubmission.objects.filter(status='APPROVED').count()
        pending_submissions = PriceSubmission.objects.filter(status='PENDING').count()
        rejected_submissions = PriceSubmission.objects.filter(status='REJECTED').count()
        
        self.stdout.write(f"\n📈 Statistiques actuelles:")
        self.stdout.write(f"   - Total soumissions: {total_submissions}")
        self.stdout.write(f"   - Soumissions validées: {approved_submissions}")
        self.stdout.write(f"   - Soumissions en attente: {pending_submissions}")
        self.stdout.write(f"   - Soumissions rejetées: {rejected_submissions}")
        
        # Top 5 des fournisseurs
        from django.db.models import Count
        top_suppliers = PriceSubmission.objects.values('supplier_name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        if top_suppliers:
            self.stdout.write(f"\n🏆 Top 5 des fournisseurs:")
            for i, supplier in enumerate(top_suppliers, 1):
                self.stdout.write(f"   {i}. {supplier['supplier_name']}: {supplier['count']} prix") 