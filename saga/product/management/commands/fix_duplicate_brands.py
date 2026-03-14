from django.core.management.base import BaseCommand
from django.db import transaction
from product.models import Phone, Product
from product.utils import normalize_phone_brand
from django.db.models import Count

class Command(BaseCommand):
    help = 'Corrige les doublons de marques en normalisant la casse'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les changements sans les appliquer',
        )
        parser.add_argument(
            '--include-products',
            action='store_true',
            help='Inclut aussi la normalisation des marques dans Product',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Analyse des doublons de marques...'))
        
        # Analyser les marques Phone
        phone_brands = Phone.objects.values('brand').annotate(
            count=Count('id')
        ).order_by('brand')
        
        self.stdout.write('\n📱 Marques dans Phone:')
        for brand in phone_brands:
            self.stdout.write(f'  • {brand["brand"]}: {brand["count"]} téléphones')
        
        # Analyser les marques Product si demandé
        product_brands = []
        if options['include_products']:
            product_brands = Product.objects.values('brand').annotate(
                count=Count('id')
            ).order_by('brand')
            
            self.stdout.write('\n📦 Marques dans Product:')
            for brand in product_brands:
                self.stdout.write(f'  • {brand["brand"]}: {brand["count"]} produits')
        
        # Identifier les changements nécessaires
        changes_needed = []
        
        # Vérifier les marques Phone
        for brand_info in phone_brands:
            original_brand = brand_info['brand']
            normalized_brand = normalize_phone_brand(original_brand)
            
            if original_brand != normalized_brand:
                changes_needed.append({
                    'model': 'Phone',
                    'original': original_brand,
                    'normalized': normalized_brand,
                    'count': brand_info['count']
                })
        
        # Vérifier les marques Product
        for brand_info in product_brands:
            original_brand = brand_info['brand']
            normalized_brand = normalize_phone_brand(original_brand)
            
            if original_brand != normalized_brand:
                changes_needed.append({
                    'model': 'Product',
                    'original': original_brand,
                    'normalized': normalized_brand,
                    'count': brand_info['count']
                })
        
        if not changes_needed:
            self.stdout.write(self.style.SUCCESS('\n✅ Toutes les marques sont déjà normalisées !'))
            return
        
        # Afficher les changements prévus
        self.stdout.write('\n🔄 Changements prévus:')
        for change in changes_needed:
            self.stdout.write(
                f'  • {change["model"]}: {change["original"]} → {change["normalized"]} '
                f'({change["count"]} éléments)'
            )
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('\n🔍 Mode dry-run: Aucun changement appliqué'))
            return
        
        # Corriger les doublons
        self.stdout.write('\n🔧 Correction des doublons...')
        
        try:
            with transaction.atomic():
                updated_phones = 0
                updated_products = 0
                
                # Mettre à jour les Phone
                for change in changes_needed:
                    if change['model'] == 'Phone':
                        count = Phone.objects.filter(brand=change['original']).update(
                            brand=change['normalized']
                        )
                        updated_phones += count
                        self.stdout.write(
                            f'  ✅ {count} téléphones mis à jour: '
                            f'{change["original"]} → {change["normalized"]}'
                        )
                
                # Mettre à jour les Product
                for change in changes_needed:
                    if change['model'] == 'Product':
                        count = Product.objects.filter(brand=change['original']).update(
                            brand=change['normalized']
                        )
                        updated_products += count
                        self.stdout.write(
                            f'  ✅ {count} produits mis à jour: '
                            f'{change["original"]} → {change["normalized"]}'
                        )
                
                # Vérifier le résultat
                final_phone_brands = Phone.objects.values('brand').annotate(
                    count=Count('id')
                ).order_by('brand')
                
                self.stdout.write('\n📊 Résultat final:')
                self.stdout.write('\n📱 Marques Phone après correction:')
                for brand in final_phone_brands:
                    self.stdout.write(f'  • {brand["brand"]}: {brand["count"]} téléphones')
                
                if options['include_products']:
                    final_product_brands = Product.objects.values('brand').annotate(
                        count=Count('id')
                    ).order_by('brand')
                    
                    self.stdout.write('\n📦 Marques Product après correction:')
                    for brand in final_product_brands:
                        self.stdout.write(f'  • {brand["brand"]}: {brand["count"]} produits')
                
                self.stdout.write(f'\n📈 Résumé: {updated_phones} téléphones et {updated_products} produits mis à jour')
                self.stdout.write(self.style.SUCCESS('\n🎉 Correction terminée avec succès!'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Erreur lors de la correction: {str(e)}'))
            return
        
        # Recommandations
        self.stdout.write('\n💡 Recommandations:')
        self.stdout.write('• Utilisez toujours le template add_phone_template.py pour les nouveaux téléphones')
        self.stdout.write('• La normalisation est maintenant automatique dans les nouvelles commandes')
        self.stdout.write('• Vérifiez régulièrement avec --dry-run pour détecter les nouveaux doublons') 