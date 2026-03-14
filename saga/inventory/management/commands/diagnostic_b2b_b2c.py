"""
Commande de management pour diagnostiquer pourquoi tous les produits B2B ne sont pas dans B2C

Usage:
    python manage.py diagnostic_b2b_b2c
"""
from django.core.management.base import BaseCommand
from inventory.models import ExternalProduct, InventoryConnection, ApiKey
from inventory.services import InventoryAPIClient
from product.models import Product


class Command(BaseCommand):
    help = 'Diagnostique pourquoi tous les produits B2B ne sont pas dans B2C'

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write("DIAGNOSTIC SYNCHRONISATION B2B → B2C")
        self.stdout.write("=" * 80)
        self.stdout.write("")
        
        # 1. Vérifier la configuration API
        self.stdout.write("1. CONFIGURATION API")
        self.stdout.write("-" * 80)
        api_key = ApiKey.get_active_key()
        if not api_key:
            self.stdout.write(self.style.ERROR("❌ Aucune clé API active trouvée"))
            return
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ Clé API active trouvée: {api_key.name}"))
        
        connection = InventoryConnection.objects.first()
        if not connection:
            self.stdout.write(self.style.ERROR("❌ Aucune connexion Inventory trouvée"))
            return
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ Connexion trouvée: {connection.name}"))
        self.stdout.write("")
        
        # 2. Récupérer les produits depuis l'API B2B
        self.stdout.write("2. PRODUITS DANS L'API B2B")
        self.stdout.write("-" * 80)
        try:
            api_client = InventoryAPIClient(connection)
            all_b2b_products = []
            page = 1
            has_next = True
            
            while has_next:
                response = api_client.get_products_list(page=page)
                if isinstance(response, dict):
                    products = response.get('results', response.get('products', []))
                    all_b2b_products.extend(products)
                    has_next = response.get('next') is not None
                else:
                    products = response if isinstance(response, list) else []
                    all_b2b_products.extend(products)
                    has_next = False
                page += 1
                if page > 100:  # Limite de sécurité
                    break
            
            b2b_count = len(all_b2b_products)
            b2b_ids = [p.get('id') for p in all_b2b_products if p.get('id')]
            self.stdout.write(self.style.SUCCESS(f"✅ Produits dans l'API B2B: {b2b_count}"))
            self.stdout.write(f"   IDs B2B: {len(b2b_ids)} produits avec ID")
            self.stdout.write("")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erreur lors de la récupération des produits B2B: {str(e)}"))
            return
        
        # 3. Vérifier les ExternalProduct
        self.stdout.write("3. PRODUITS SYNCHRONISÉS (ExternalProduct)")
        self.stdout.write("-" * 80)
        all_external = ExternalProduct.objects.all()
        synced_external = ExternalProduct.objects.filter(sync_status='synced')
        b2b_external = ExternalProduct.objects.filter(is_b2b=True)
        synced_b2b_external = ExternalProduct.objects.filter(sync_status='synced', is_b2b=True)
        
        self.stdout.write(f"Total ExternalProduct: {all_external.count()}")
        self.stdout.write(f"  - sync_status='synced': {synced_external.count()}")
        self.stdout.write(f"  - is_b2b=True: {b2b_external.count()}")
        self.stdout.write(f"  - sync_status='synced' ET is_b2b=True: {synced_b2b_external.count()}")
        self.stdout.write("")
        
        # 4. Identifier les produits B2B non synchronisés
        self.stdout.write("4. PRODUITS B2B NON SYNCHRONISÉS")
        self.stdout.write("-" * 80)
        synced_external_ids = set(synced_b2b_external.values_list('external_id', flat=True))
        missing_ids = [id for id in b2b_ids if id not in synced_external_ids]
        
        self.stdout.write(f"Produits B2B non synchronisés: {len(missing_ids)}")
        if missing_ids:
            self.stdout.write(f"   IDs manquants (premiers 20): {missing_ids[:20]}")
            self.stdout.write("")
            
            # Analyser pourquoi ils ne sont pas synchronisés
            self.stdout.write("   Analyse des raisons:")
            errors_external = ExternalProduct.objects.filter(
                external_id__in=missing_ids,
                sync_status='error'
            )
            if errors_external.exists():
                self.stdout.write(self.style.WARNING(f"   - Produits avec sync_status='error': {errors_external.count()}"))
                for ep in errors_external[:5]:
                    error_msg = ep.sync_error[:100] if ep.sync_error else 'Pas d\'erreur'
                    self.stdout.write(f"     * ID externe {ep.external_id}: {error_msg}")
            
            pending_external = ExternalProduct.objects.filter(
                external_id__in=missing_ids,
                sync_status='pending'
            )
            if pending_external.exists():
                self.stdout.write(f"   - Produits avec sync_status='pending': {pending_external.count()}")
            
            all_external_ids = set(all_external.values_list('external_id', flat=True))
            not_in_db = [id for id in missing_ids if id not in all_external_ids]
            if not_in_db:
                self.stdout.write(f"   - Produits jamais tentés de synchronisation: {len(not_in_db)}")
        self.stdout.write("")
        
        # 5. Vérifier les produits avec relation Product
        self.stdout.write("5. PRODUITS AVEC RELATION Product")
        self.stdout.write("-" * 80)
        synced_b2b_with_product = synced_b2b_external.filter(product__isnull=False)
        synced_b2b_without_product = synced_b2b_external.filter(product__isnull=True)
        
        self.stdout.write(f"Produits synchronisés avec Product: {synced_b2b_with_product.count()}")
        self.stdout.write(f"Produits synchronisés SANS Product: {synced_b2b_without_product.count()}")
        if synced_b2b_without_product.exists():
            self.stdout.write(self.style.WARNING("   ⚠️  Ces produits ont un ExternalProduct mais pas de Product associé!"))
            self.stdout.write(f"   IDs externes: {list(synced_b2b_without_product.values_list('external_id', flat=True))[:10]}")
        self.stdout.write("")
        
        # 6. Vérifier les produits disponibles
        self.stdout.write("6. PRODUITS DISPONIBLES (is_available=True)")
        self.stdout.write("-" * 80)
        product_ids = [ep.product.id for ep in synced_b2b_with_product if ep.product]
        available_products = Product.objects.filter(
            id__in=product_ids,
            is_available=True
        )
        unavailable_products = Product.objects.filter(
            id__in=product_ids,
            is_available=False
        )
        
        self.stdout.write(f"Produits disponibles: {available_products.count()}")
        self.stdout.write(f"Produits non disponibles: {unavailable_products.count()}")
        if unavailable_products.exists():
            self.stdout.write(self.style.WARNING("   ⚠️  Ces produits sont synchronisés mais non disponibles:"))
            for p in unavailable_products[:10]:
                self.stdout.write(f"     * {p.title} (ID: {p.id}, is_available={p.is_available})")
        self.stdout.write("")
        
        # 7. Résumé final
        self.stdout.write("=" * 80)
        self.stdout.write("RÉSUMÉ")
        self.stdout.write("=" * 80)
        self.stdout.write(f"Produits dans l'API B2B: {b2b_count}")
        self.stdout.write(f"Produits synchronisés (sync_status='synced' + is_b2b=True): {synced_b2b_external.count()}")
        self.stdout.write(f"Produits avec Product valide: {synced_b2b_with_product.count()}")
        self.stdout.write(f"Produits disponibles dans B2C: {available_products.count()}")
        self.stdout.write("")
        
        # Calculer les écarts
        gap_sync = b2b_count - synced_b2b_external.count()
        gap_product = synced_b2b_external.count() - synced_b2b_with_product.count()
        gap_available = synced_b2b_with_product.count() - available_products.count()
        
        self.stdout.write("ÉCARTS:")
        if gap_sync > 0:
            self.stdout.write(self.style.WARNING(f"  ⚠️  {gap_sync} produits B2B ne sont pas synchronisés"))
        if gap_product > 0:
            self.stdout.write(self.style.WARNING(f"  ⚠️  {gap_product} produits synchronisés n'ont pas de Product"))
        if gap_available > 0:
            self.stdout.write(self.style.WARNING(f"  ⚠️  {gap_available} produits synchronisés ne sont pas disponibles (is_available=False)"))
        
        if gap_sync == 0 and gap_product == 0 and gap_available == 0:
            self.stdout.write(self.style.SUCCESS("  ✅ Tous les produits B2B sont synchronisés et disponibles dans B2C!"))
        self.stdout.write("")
