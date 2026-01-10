"""
Commande de management pour tester la connexion à l'API B2B
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from inventory.services import InventoryAPIClient, InventoryAPIError
from inventory.models import ApiKey


class Command(BaseCommand):
    help = 'Teste la connexion à l\'API B2B et affiche les informations'

    def handle(self, *args, **options):
        # Vérifier la configuration
        self.stdout.write("\n" + "="*60)
        self.stdout.write("TEST DE CONNEXION À L'API B2B")
        self.stdout.write("="*60 + "\n")
        
        # Vérifier l'URL
        api_url = getattr(settings, 'B2B_API_URL', None)
        if api_url:
            self.stdout.write(self.style.SUCCESS(f"[OK] URL API: {api_url}"))
        else:
            self.stdout.write(self.style.WARNING("[WARN] B2B_API_URL non configure"))
        
        # Vérifier le token
        api_key = ApiKey.get_active_key()
        if not api_key:
            api_key = getattr(settings, 'B2B_API_KEY', None)
        
        if api_key:
            masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
            self.stdout.write(self.style.SUCCESS(f"[OK] Token API: {masked_key}"))
        else:
            self.stdout.write(self.style.ERROR("[ERREUR] Aucune cle API configuree (ni dans ApiKey ni dans .env)"))
            return
        
        # Créer le client API
        try:
            self.stdout.write(f"\n[INFO] Test avec URL: {api_url}")
            
            api_client = InventoryAPIClient()
            
            # Test 1: Récupérer les catégories
            self.stdout.write("\n[TEST 1] Recuperation des categories...")
            try:
                categories = api_client.get_categories_list()
                self.stdout.write(self.style.SUCCESS(f"[OK] {len(categories)} categorie(s) recuperee(s)"))
                if categories:
                    self.stdout.write(f"   Premiere categorie: {categories[0].get('name', 'N/A')}")
            except InventoryAPIError as e:
                self.stdout.write(self.style.ERROR(f"[ERREUR] {str(e)}"))
            
            # Test 2: Récupérer les produits
            self.stdout.write("\n[TEST 2] Recuperation des produits...")
            try:
                products_response = api_client.get_products_list(page=1, page_size=5)
                
                # Gérer différents formats de réponse
                if isinstance(products_response, dict):
                    products = products_response.get('results', products_response.get('products', []))
                    total = products_response.get('count', len(products))
                else:
                    products = products_response if isinstance(products_response, list) else []
                    total = len(products)
                
                self.stdout.write(self.style.SUCCESS(f"[OK] {len(products)} produit(s) recupere(s) (total: {total})"))
                if products:
                    first_product = products[0]
                    self.stdout.write(f"   Premier produit: {first_product.get('name', first_product.get('title', 'N/A'))}")
            except InventoryAPIError as e:
                self.stdout.write(self.style.ERROR(f"[ERREUR] {str(e)}"))
            
            # Test 3: Récupérer les sites
            self.stdout.write("\n[TEST 3] Recuperation des sites...")
            try:
                sites = api_client.get_sites_list()
                self.stdout.write(self.style.SUCCESS(f"[OK] {len(sites)} site(s) recupere(s)"))
                if sites:
                    for site in sites[:3]:  # Afficher les 3 premiers
                        self.stdout.write(f"   - {site.get('name', 'N/A')} (ID: {site.get('id', 'N/A')})")
            except InventoryAPIError as e:
                self.stdout.write(self.style.ERROR(f"[ERREUR] {str(e)}"))
            
            # Test 4: Test de connexion général
            self.stdout.write("\n[TEST 4] Test de connexion general...")
            if api_client.test_connection():
                self.stdout.write(self.style.SUCCESS("[OK] Connexion reussie !"))
            else:
                self.stdout.write(self.style.ERROR("[ERREUR] Connexion echouee"))
            
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f"[ERREUR] Erreur de configuration: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[ERREUR] Erreur inattendue: {str(e)}"))
        
        self.stdout.write("\n" + "="*60 + "\n")
