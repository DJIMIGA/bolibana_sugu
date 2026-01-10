"""
Commande de management pour tester la synchronisation automatique B2B
"""
from django.core.management.base import BaseCommand
from inventory.models import ApiKey, ExternalProduct
from inventory.utils import get_b2b_products
from inventory.tasks import should_sync_products, sync_products_auto, sync_categories_auto


class Command(BaseCommand):
    help = 'Teste la synchronisation automatique des produits B2B'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la synchronisation même si récente',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("TEST SYNCHRONISATION AUTOMATIQUE B2B"))
        self.stdout.write("="*60)
        
        # Test 1: Clé API
        self.stdout.write("\n1. Vérification de la clé API...")
        api_key = ApiKey.get_active_key()
        if api_key:
            masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
            self.stdout.write(self.style.SUCCESS(f"   ✅ Clé API trouvée: {masked_key}"))
        else:
            self.stdout.write(self.style.ERROR("   ❌ Aucune clé API - Configurez dans /admin/inventory/apikey/"))
            return
        
        # Test 2: Logique de synchronisation
        self.stdout.write("\n2. Test de la logique de synchronisation...")
        should_sync = should_sync_products()
        if should_sync:
            self.stdout.write(self.style.SUCCESS("   ✅ Devrait synchroniser"))
        else:
            self.stdout.write(self.style.WARNING("   ⚠️  Synchronisation non nécessaire (trop récente)"))
        
        # Test 3: Produits existants
        self.stdout.write("\n3. Produits B2B actuellement synchronisés...")
        products_count = ExternalProduct.objects.filter(sync_status='synced').count()
        self.stdout.write(f"   {products_count} produits synchronisés")
        
        if products_count > 0:
            products = get_b2b_products(limit=3)
            self.stdout.write(f"   {len(products)} produits récupérés pour test")
            if products:
                self.stdout.write(f"   Exemple: {products[0].title}")
        
        # Test 4: Synchronisation des produits
        self.stdout.write("\n4. Test de synchronisation automatique des produits...")
        try:
            result = sync_products_auto(force=force)
            if result['success']:
                stats = result['stats']
                self.stdout.write(self.style.SUCCESS("   ✅ Synchronisation réussie"))
                self.stdout.write(f"      - Total: {stats['total']}")
                self.stdout.write(f"      - Créés: {stats['created']}")
                self.stdout.write(f"      - Mis à jour: {stats['updated']}")
                self.stdout.write(f"      - Erreurs: {stats['errors']}")
                
                if stats['errors'] > 0:
                    self.stdout.write(self.style.WARNING(f"\n   ⚠️  {stats['errors']} erreurs détectées:"))
                    for error in stats['errors_list'][:3]:
                        self.stdout.write(f"      - Produit {error.get('product_id')}: {error.get('error')[:50]}")
            else:
                self.stdout.write(self.style.WARNING(f"   ⚠️  {result['message']}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Erreur: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())
        
        # Test 5: Synchronisation des catégories
        self.stdout.write("\n5. Test de synchronisation automatique des catégories...")
        try:
            result = sync_categories_auto(force=force)
            if result['success']:
                stats = result['stats']
                self.stdout.write(self.style.SUCCESS("   ✅ Synchronisation des catégories réussie"))
                self.stdout.write(f"      - Total: {stats['total']}")
                self.stdout.write(f"      - Créées: {stats['created']}")
                self.stdout.write(f"      - Mises à jour: {stats['updated']}")
                self.stdout.write(f"      - Erreurs: {stats['errors']}")
            else:
                self.stdout.write(self.style.WARNING(f"   ⚠️  {result['message']}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Erreur: {str(e)}"))
        
        # Test 6: Vérification finale
        self.stdout.write("\n6. Vérification finale...")
        final_count = ExternalProduct.objects.filter(sync_status='synced').count()
        self.stdout.write(f"   {final_count} produits B2B synchronisés au total")
        
        if final_count > 0:
            products = get_b2b_products(limit=5)
            self.stdout.write(f"   {len(products)} produits disponibles pour affichage")
            if products:
                self.stdout.write("\n   Exemples de produits:")
                for i, product in enumerate(products[:3], 1):
                    self.stdout.write(f"      {i}. {product.title} - {product.format_price()}")
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("Test terminé!"))
        self.stdout.write("="*60 + "\n")

