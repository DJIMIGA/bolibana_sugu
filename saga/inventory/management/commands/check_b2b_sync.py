"""
Commande de management pour vérifier l'état de la synchronisation B2B
"""
from django.core.management.base import BaseCommand
from inventory.models import ExternalProduct, ExternalCategory, ApiKey
from product.models import Product, Category
from django.conf import settings


class Command(BaseCommand):
    help = 'Vérifie l\'état de la synchronisation B2B et affiche les statistiques'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*60)
        self.stdout.write("DIAGNOSTIC DE SYNCHRONISATION B2B")
        self.stdout.write("="*60 + "\n")
        
        # 1. Vérifier l'API key
        self.stdout.write("\n[1] Configuration API Key")
        api_key = ApiKey.get_active_key()
        if api_key:
            masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
            self.stdout.write(self.style.SUCCESS(f"  ✅ Clé API active: {masked_key}"))
        else:
            self.stdout.write(self.style.ERROR("  ❌ Aucune clé API active"))
            self.stdout.write(self.style.WARNING("  → Ajoutez une clé API via /admin/inventory/apikey/add/"))
        
        # 2. Vérifier les produits synchronisés
        self.stdout.write("\n[2] Produits synchronisés")
        total_external = ExternalProduct.objects.count()
        synced_external = ExternalProduct.objects.filter(sync_status='synced').count()
        pending_external = ExternalProduct.objects.filter(sync_status='pending').count()
        error_external = ExternalProduct.objects.filter(sync_status='error').count()
        
        self.stdout.write(f"  Total ExternalProduct: {total_external}")
        self.stdout.write(self.style.SUCCESS(f"  ✅ Synchronisés: {synced_external}"))
        if pending_external > 0:
            self.stdout.write(self.style.WARNING(f"  ⏳ En attente: {pending_external}"))
        if error_external > 0:
            self.stdout.write(self.style.ERROR(f"  ❌ Erreurs: {error_external}"))
        
        if synced_external == 0:
            self.stdout.write(self.style.ERROR("\n  ⚠️  AUCUN PRODUIT SYNCHRONISÉ"))
            self.stdout.write(self.style.WARNING("  → Exécutez: python manage.py sync_products_from_inventory"))
        else:
            # Vérifier que les produits existent
            synced_products = ExternalProduct.objects.filter(sync_status='synced').select_related('product')
            valid_products = [ep for ep in synced_products if ep.product]
            self.stdout.write(f"  Produits valides: {len(valid_products)}/{synced_external}")
            
            if len(valid_products) < synced_external:
                self.stdout.write(self.style.WARNING(f"  ⚠️  {synced_external - len(valid_products)} produits sans relation Product"))
        
        # 3. Vérifier les catégories synchronisées
        self.stdout.write("\n[3] Catégories synchronisées")
        total_external_cat = ExternalCategory.objects.count()
        self.stdout.write(f"  Total ExternalCategory: {total_external_cat}")
        
        if total_external_cat == 0:
            self.stdout.write(self.style.WARNING("  ⚠️  AUCUNE CATÉGORIE SYNCHRONISÉE"))
            self.stdout.write(self.style.WARNING("  → Exécutez: python manage.py sync_categories_from_inventory"))
        
        # 4. Test de l'endpoint API
        self.stdout.write("\n[4] Test de l'endpoint API")
        if synced_external > 0:
            product_ids = [ep.product.id for ep in ExternalProduct.objects.filter(sync_status='synced').select_related('product') if ep.product]
            products = Product.objects.filter(id__in=product_ids)
            self.stdout.write(self.style.SUCCESS(f"  ✅ {products.count()} produits disponibles via /api/inventory/products/synced/"))
        else:
            self.stdout.write(self.style.ERROR("  ❌ Aucun produit disponible (synchronisation requise)"))
        
        # 5. Recommandations
        self.stdout.write("\n[5] Recommandations")
        if synced_external == 0:
            self.stdout.write(self.style.WARNING("  → Synchroniser les produits: python manage.py sync_products_from_inventory"))
        if total_external_cat == 0:
            self.stdout.write(self.style.WARNING("  → Synchroniser les catégories: python manage.py sync_categories_from_inventory"))
        if synced_external > 0 and total_external_cat > 0:
            self.stdout.write(self.style.SUCCESS("  ✅ Synchronisation OK - Les produits sont disponibles"))
        
        self.stdout.write("\n" + "="*60 + "\n")

