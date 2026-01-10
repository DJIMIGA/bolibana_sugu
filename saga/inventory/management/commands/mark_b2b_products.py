"""
Commande de management pour marquer les produits synchronisés comme B2B
"""
from django.core.management.base import BaseCommand
from inventory.models import ExternalProduct


class Command(BaseCommand):
    help = 'Marque tous les produits synchronisés comme B2B (is_b2b=True)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche ce qui sera fait sans modifier la base de données',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("MARQUAGE DES PRODUITS B2B")
        self.stdout.write("="*60 + "\n")
        
        # Récupérer tous les produits synchronisés qui ne sont pas encore marqués B2B
        synced_products = ExternalProduct.objects.filter(
            sync_status='synced',
            is_b2b=False
        ).select_related('product')
        
        count = synced_products.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("  ✅ Tous les produits synchronisés sont déjà marqués comme B2B"))
            
            # Afficher les statistiques
            total_synced = ExternalProduct.objects.filter(sync_status='synced').count()
            total_b2b = ExternalProduct.objects.filter(sync_status='synced', is_b2b=True).count()
            self.stdout.write(f"\n  Statistiques:")
            self.stdout.write(f"  - Total synchronisés: {total_synced}")
            self.stdout.write(f"  - Marqués B2B: {total_b2b}")
            return
        
        self.stdout.write(f"\n  Produits à marquer comme B2B: {count}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\n  [DRY RUN] Aucune modification ne sera effectuée"))
            for ep in synced_products[:10]:  # Afficher les 10 premiers
                self.stdout.write(f"  - {ep.product.title if ep.product else 'N/A'} (ID: {ep.external_id})")
            if count > 10:
                self.stdout.write(f"  ... et {count - 10} autres")
        else:
            # Marquer tous les produits synchronisés comme B2B
            updated = synced_products.update(is_b2b=True)
            self.stdout.write(self.style.SUCCESS(f"\n  ✅ {updated} produits marqués comme B2B"))
            
            # Afficher les détails des produits marqués
            self.stdout.write("\n  Produits marqués:")
            marked_products = ExternalProduct.objects.filter(
                sync_status='synced',
                is_b2b=True
            ).select_related('product')[:10]
            
            for ep in marked_products:
                product_name = ep.product.title if ep.product else 'N/A'
                self.stdout.write(f"  - {product_name} (ID externe: {ep.external_id})")
            
            total_b2b = ExternalProduct.objects.filter(sync_status='synced', is_b2b=True).count()
            if total_b2b > 10:
                self.stdout.write(f"  ... et {total_b2b - 10} autres")
        
        self.stdout.write("\n" + "="*60 + "\n")




