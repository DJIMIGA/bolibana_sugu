"""
Services de synchronisation avec l'app de gestion de stock
"""
import requests
import logging
from typing import Dict, List, Optional, Any
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from io import BytesIO
from PIL import Image
from .models import (
    ApiKey,
    ExternalProduct,
    ExternalCategory
)
from product.models import Product, Category, ImageProduct
from cart.models import Order, OrderItem

logger = logging.getLogger(__name__)


class InventoryAPIError(Exception):
    """Exception personnalisée pour les erreurs API"""
    pass


class InventoryAPIClient:
    """
    Client pour appeler les API de l'app de gestion de stock (B2B)
    """
    
    def __init__(self):
        """
        Initialise le client API
        
        Note: Le token API est récupéré depuis ApiKey.get_active_key()
        ou depuis settings.B2B_API_KEY en fallback.
        """
        # Utiliser l'URL par défaut depuis settings
        self.base_url = getattr(settings, 'B2B_API_URL', 'https://www.bolibanastock.com/api/v1').rstrip('/')
        logger.info(f"URL API configurée: {self.base_url}")
        
        # Récupérer le token : depuis ApiKey active ou depuis settings
        self.token = ApiKey.get_active_key()
        
        if not self.token:
            # Vérifier si une clé existe en BDD mais n'est pas active
            api_key_count = ApiKey.objects.count()
            active_count = ApiKey.objects.filter(is_active=True).count()
            
            error_msg = (
                "Aucune clé API configurée.\n"
                f"  - Clés API en base: {api_key_count}\n"
                f"  - Clés actives: {active_count}\n"
                "Solutions:\n"
                "  1. Ajoutez une clé API via l'admin (/admin/inventory/apikey/add/) et cochez 'Active'\n"
                "  2. Ou configurez B2B_API_KEY dans .env"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Log de la clé utilisée (masquée)
        masked_token = f"{self.token[:6]}...{self.token[-4:]}" if len(self.token) > 10 else "***"
        logger.info(f"Clé API utilisée: {masked_token}")
        
        # Enregistrer l'utilisation de la clé si elle existe
        api_key_obj = ApiKey.objects.filter(is_active=True).first()
        if api_key_obj:
            api_key_obj.record_usage()
            logger.debug(f"Utilisation enregistrée pour la clé: {api_key_obj.name}")
        
        self.timeout = getattr(settings, 'INVENTORY_API_TIMEOUT', 30)  # Timeout en secondes
        
    def _get_headers(self) -> Dict[str, str]:
        """
        Retourne les en-têtes HTTP pour les requêtes
        
        Utilise X-API-Key comme header d'authentification
        selon l'architecture B2B/B2C
        """
        return {
            'X-API-Key': self.token,  # Header utilisé par B2B pour vérifier le token
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Effectue une requête HTTP vers l'API
        
        Args:
            method: Méthode HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint de l'API (sans le base_url)
            **kwargs: Arguments supplémentaires pour requests
            
        Returns:
            Dict contenant la réponse JSON
            
        Raises:
            InventoryAPIError: En cas d'erreur API
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        # Log de la requête (sans le token complet)
        logger.info(f"Requête {method} vers {url}")
        logger.debug(f"Headers envoyés: {list(headers.keys())}")
        if self.token:
            masked_token = f"{self.token[:6]}...{self.token[-4:]}" if len(self.token) > 10 else "***"
            logger.debug(f"Token utilisé: {masked_token}")
            # Vérifier que le header X-API-Key est bien présent
            if 'X-API-Key' in headers:
                logger.debug(f"Header X-API-Key présent: {masked_token}")
            else:
                logger.error("ERREUR: Header X-API-Key manquant dans les headers!")
        else:
            logger.error("AUCUN TOKEN CONFIGURE - La requête va échouer")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
            
            # Log de la réponse
            logger.debug(f"Réponse {response.status_code} de {url}")
            
            # Gestion spéciale des erreurs 403 (Forbidden)
            if response.status_code == 403:
                error_detail = "Non autorisé"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text[:200]
                
                # Log détaillé pour déboguer
                masked_token = f"{self.token[:6]}...{self.token[-4:]}" if len(self.token) > 10 else "***"
                logger.error(f"Erreur 403 - Token utilisé: {masked_token}")
                logger.error(f"Erreur 403 - Header X-API-Key présent: {'X-API-Key' in headers}")
                logger.error(f"Erreur 403 - Longueur du token: {len(self.token) if self.token else 0}")
                
                error_msg = (
                    f"Erreur 403 Forbidden lors de l'appel à {url}\n"
                    f"Détail: {error_detail}\n"
                    f"Token utilisé: {masked_token}\n"
                    f"Vérifiez que:\n"
                    f"  1. La clé API est correcte et active dans /admin/inventory/apikey/\n"
                    f"  2. Le header X-API-Key est bien envoyé (présent: {'X-API-Key' in headers})\n"
                    f"  3. La clé API a les permissions nécessaires dans l'admin B2B\n"
                    f"  4. La clé API n'est pas expirée ou révoquée"
                )
                logger.error(error_msg)
                raise InventoryAPIError(error_msg)
            
            # Vérifier le statut de la réponse
            response.raise_for_status()
            
            # Retourner la réponse JSON
            try:
                return response.json()
            except ValueError:
                # Si ce n'est pas du JSON, retourner le texte (limité pour éviter les logs HTML)
                text_preview = response.text[:200] if response.text else "N/A"
                if '<' in text_preview and '>' in text_preview:
                    text_preview = "Réponse HTML (non affichée)"
                logger.warning(f"Réponse non-JSON de {url}: {text_preview}")
                return {'content': response.text}
            
        except requests.exceptions.Timeout:
            error_msg = f"Timeout lors de l'appel à {url}"
            logger.error(error_msg)
            raise InventoryAPIError(error_msg)
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Erreur de connexion à {url}: {str(e)}"
            logger.error(error_msg)
            raise InventoryAPIError(error_msg)
            
        except requests.exceptions.HTTPError as e:
            error_detail = ""
            if hasattr(response, 'text'):
                try:
                    error_data = response.json()
                    error_detail = f" - Détail: {error_data.get('detail', str(error_data))}"
                except:
                    # Limiter la réponse texte pour éviter les logs HTML verbeux
                    text_preview = response.text[:200] if response.text else "N/A"
                    # Retirer le HTML si présent
                    if '<' in text_preview and '>' in text_preview:
                        text_preview = "Réponse HTML (non affichée)"
                    error_detail = f" - Réponse: {text_preview}"
            
            error_msg = f"Erreur HTTP {response.status_code} lors de l'appel à {url}: {str(e)}{error_detail}"
            logger.error(error_msg)
            raise InventoryAPIError(error_msg)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Erreur lors de l'appel à {url}: {str(e)}"
            logger.error(error_msg)
            raise InventoryAPIError(error_msg)
    
    def get_products_list(self, site_id: Optional[int] = None, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        """
        Récupère la liste des produits depuis l'app de gestion
        
        Args:
            site_id: ID du site/magasin (optionnel)
            page: Numéro de page
            page_size: Nombre d'éléments par page
            
        Returns:
            Dict contenant la liste des produits et les métadonnées de pagination
        """
        params = {
            'page': page,
            'page_size': page_size,
        }
        
        if site_id:
            params['site_id'] = site_id
        
        endpoint = 'b2c/products/'  # Endpoint B2C pour les produits
        return self._make_request('GET', endpoint, params=params)
    
    def get_product_detail(self, external_id: int) -> Dict[str, Any]:
        """
        Récupère les détails d'un produit depuis l'app de gestion
        
        Args:
            external_id: ID du produit dans l'app de gestion
            
        Returns:
            Dict contenant les détails du produit
        """
        endpoint = f'b2c/products/{external_id}/'
        return self._make_request('GET', endpoint)
    
    def get_categories_list(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste des catégories depuis l'app de gestion
        
        Returns:
            Liste des catégories
        """
        endpoint = 'b2c/categories/'  # Endpoint B2C pour les catégories
        response = self._make_request('GET', endpoint)
        
        # Si la réponse est une liste, la retourner directement
        if isinstance(response, list):
            return response
        
        # Si la réponse est un dict avec une clé 'results' ou 'categories'
        if isinstance(response, dict):
            return response.get('results', response.get('categories', []))
        
        return []
    
    def get_category_detail(self, external_id: int) -> Dict[str, Any]:
        """
        Récupère les détails d'une catégorie depuis l'app de gestion
        
        Args:
            external_id: ID de la catégorie dans l'app de gestion
            
        Returns:
            Dict contenant les détails de la catégorie
        """
        endpoint = f'b2c/categories/{external_id}/'
        return self._make_request('GET', endpoint)
    
    def get_sites_list(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste des sites/magasins depuis l'app de gestion
        
        Returns:
            Liste des sites
        """
        endpoint = 'b2c/sites/'  # Endpoint B2C pour les sites
        response = self._make_request('GET', endpoint)
        
        # Si la réponse est une liste, la retourner directement
        if isinstance(response, list):
            return response
        
        # Si la réponse est un dict avec une clé 'results' ou 'sites'
        if isinstance(response, dict):
            return response.get('results', response.get('sites', []))
        
        return []
    
    def create_sale(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée une vente dans l'app de gestion
        
        Args:
            order_data: Données de la commande à synchroniser
                Format attendu:
                {
                    'order_number': str,
                    'items': [
                        {
                            'product_id': int,  # ID externe du produit
                            'quantity': int,
                            'price': float,
                            'site_id': int,  # ID du site
                        }
                    ],
                    'total': float,
                    'customer_email': str,
                    'created_at': str,  # ISO format
                }
        
        Returns:
            Dict contenant les données de la vente créée
        """
        endpoint = 'b2c/sales/'  # Endpoint B2C pour les ventes
        return self._make_request('POST', endpoint, json=order_data)
    
    def update_sale(self, external_sale_id: int, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Met à jour une vente dans l'app de gestion
        
        Args:
            external_sale_id: ID de la vente dans l'app de gestion
            order_data: Données de la commande à mettre à jour
        
        Returns:
            Dict contenant les données de la vente mise à jour
        """
        endpoint = f'b2c/sales/{external_sale_id}/'  # Endpoint B2C pour les ventes
        return self._make_request('PUT', endpoint, json=order_data)
    
    def test_connection(self) -> bool:
        """
        Teste la connexion à l'API de l'app de gestion
        
        Returns:
            True si la connexion fonctionne, False sinon
        """
        try:
            # Essayer de récupérer la liste des catégories (endpoint simple)
            self.get_categories_list()
            return True
        except InventoryAPIError:
            return False


class ProductSyncService:
    """
    Service pour synchroniser les produits depuis l'app de gestion vers SagaKore
    """
    
    def __init__(self):
        self.api_client = InventoryAPIClient()
    
    def download_and_save_image(self, image_url: str, product: Product, is_main: bool = True, order: int = 0) -> Optional[str]:
        """
        Télécharge une image depuis une URL et la sauvegarde pour le produit
        
        Args:
            image_url: URL de l'image à télécharger
            product: Instance du produit
            is_main: True si c'est l'image principale, False pour la galerie
            order: Ordre d'affichage pour les images de galerie
        
        Returns:
            Chemin de l'image sauvegardée ou None en cas d'erreur
        """
        if not image_url:
            return None
        
        try:
            # Télécharger l'image
            response = requests.get(image_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Vérifier que c'est bien une image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                logger.warning(f"URL {image_url} ne retourne pas une image (content-type: {content_type})")
                return None
            
            # Lire le contenu de l'image
            image_content = BytesIO(response.content)
            
            # Vérifier et optimiser l'image avec PIL
            try:
                img = Image.open(image_content)
                # Convertir en RGB si nécessaire (pour les PNG avec transparence)
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = rgb_img
                
                # Sauvegarder dans un BytesIO
                output = BytesIO()
                img_format = img.format or 'JPEG'
                img.save(output, format=img_format, quality=85, optimize=True)
                output.seek(0)
                image_content = output
            except Exception as e:
                logger.warning(f"Erreur lors du traitement de l'image {image_url}: {str(e)}")
                # Utiliser l'image brute si le traitement échoue
                image_content = BytesIO(response.content)
            
            # Déterminer l'extension du fichier
            ext = 'jpg'
            if 'png' in content_type.lower():
                ext = 'png'
            elif 'webp' in content_type.lower():
                ext = 'webp'
            elif 'gif' in content_type.lower():
                ext = 'gif'
            
            # Générer un nom de fichier unique
            filename = f"b2b_{product.id}_{product.slug or 'product'}.{ext}"
            
            if is_main:
                # Sauvegarder comme image principale
                product.image.save(
                    filename,
                    ContentFile(image_content.read()),
                    save=False
                )
                logger.info(f"Image principale téléchargée et sauvegardée pour le produit {product.id}")
                return product.image.name
            else:
                # Sauvegarder dans la galerie
                # Vérifier si une image avec le même ordre existe déjà
                existing_image = ImageProduct.objects.filter(
                    product=product,
                    ordre=order
                ).first()
                
                if existing_image:
                    # Mettre à jour l'image existante
                    existing_image.image.save(
                        filename,
                        ContentFile(image_content.read()),
                        save=True
                    )
                    logger.info(f"Image de galerie mise à jour (ordre {order}) pour le produit {product.id}")
                    return existing_image.image.name
                else:
                    # Créer une nouvelle image
                    image_product = ImageProduct.objects.create(
                        product=product,
                        ordre=order
                    )
                    image_product.image.save(
                        filename,
                        ContentFile(image_content.read()),
                        save=True
                    )
                    logger.info(f"Image de galerie téléchargée et sauvegardée (ordre {order}) pour le produit {product.id}")
                    return image_product.image.name
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors du téléchargement de l'image {image_url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'image {image_url}: {str(e)}", exc_info=True)
            return None
    
    def sync_all_products(self, site_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Synchronise tous les produits depuis l'app de gestion
        
        Args:
            site_id: ID du site (optionnel)
            
        Returns:
            Dict avec les statistiques de synchronisation
        """
        stats = {
            'total': 0,
            'created': 0,
            'updated': 0,
            'errors': 0,
            'errors_list': []
        }
        
        page = 1
        has_next = True
        
        while has_next:
            try:
                response = self.api_client.get_products_list(site_id=site_id, page=page)
                
                # Gérer différents formats de réponse
                if isinstance(response, dict):
                    products = response.get('results', response.get('products', []))
                    has_next = response.get('next') is not None
                else:
                    products = response if isinstance(response, list) else []
                    has_next = False
                
                for product_data in products:
                    try:
                        # Récupérer les détails complets du produit pour avoir toutes les informations
                        external_id = product_data.get('id')
                        if external_id:
                            try:
                                # Récupérer les détails complets depuis l'API
                                detailed_product_data = self.api_client.get_product_detail(external_id)
                                # Fusionner les données de la liste avec les détails complets
                                # Les détails complets ont priorité
                                product_data = {**product_data, **detailed_product_data}
                            except InventoryAPIError as e:
                                logger.warning(f"Impossible de récupérer les détails du produit {external_id}: {str(e)}. Utilisation des données de base.")
                                # Continuer avec les données de base si les détails ne sont pas disponibles
                        
                        result = self.create_or_update_product(product_data)
                        stats['total'] += 1
                        if result['created']:
                            stats['created'] += 1
                        else:
                            stats['updated'] += 1
                    except Exception as e:
                        stats['errors'] += 1
                        stats['errors_list'].append({
                            'product_id': product_data.get('id'),
                            'error': str(e)
                        })
                        logger.error(f"Erreur lors de la synchronisation du produit {product_data.get('id')}: {str(e)}")
                
                page += 1
                
            except InventoryAPIError as e:
                logger.error(f"Erreur API lors de la synchronisation: {str(e)}")
                has_next = False
                stats['errors'] += 1
        
        return stats
    
    def sync_product(self, external_id: int) -> Dict[str, Any]:
        """
        Synchronise un produit spécifique depuis l'app de gestion
        
        Args:
            external_id: ID du produit dans l'app de gestion
            
        Returns:
            Dict avec le résultat de la synchronisation
        """
        try:
            product_data = self.api_client.get_product_detail(external_id)
            return self.create_or_update_product(product_data)
        except InventoryAPIError as e:
            logger.error(f"Erreur lors de la synchronisation du produit {external_id}: {str(e)}")
            raise
    
    def sync_categories(self) -> Dict[str, Any]:
        """
        Synchronise toutes les catégories depuis l'app de gestion
        
        Returns:
            Dict avec les statistiques de synchronisation
        """
        stats = {
            'total': 0,
            'created': 0,
            'updated': 0,
            'errors': 0,
            'errors_list': []
        }
        
        try:
            categories_data = self.api_client.get_categories_list()
            
            # Créer un mapping des catégories par ID externe pour gérer la hiérarchie
            categories_by_id = {}
            
            # Première passe : créer/mettre à jour toutes les catégories
            for category_data in categories_data:
                try:
                    result = self.create_or_update_category(category_data)
                    stats['total'] += 1
                    if result['created']:
                        stats['created'] += 1
                    else:
                        stats['updated'] += 1
                    
                    external_id = category_data.get('id')
                    if external_id:
                        categories_by_id[external_id] = result['category']
                except Exception as e:
                    stats['errors'] += 1
                    stats['errors_list'].append({
                        'category_id': category_data.get('id'),
                        'error': str(e)
                    })
                    logger.error(f"Erreur lors de la synchronisation de la catégorie {category_data.get('id')}: {str(e)}")
            
            # Deuxième passe : établir les relations parent/enfant
            for category_data in categories_data:
                external_id = category_data.get('id')
                parent_id = category_data.get('parent_id')
                
                if external_id and parent_id and external_id in categories_by_id and parent_id in categories_by_id:
                    category = categories_by_id[external_id]
                    parent_category = categories_by_id[parent_id]
                    category.parent = parent_category
                    category.save(update_fields=['parent'])
        
        except InventoryAPIError as e:
            logger.error(f"Erreur API lors de la synchronisation des catégories: {str(e)}")
            stats['errors'] += 1
        
        return stats
    
    @transaction.atomic
    def create_or_update_product(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée ou met à jour un produit dans SagaKore à partir des données de l'app de gestion
        
        Args:
            external_data: Données du produit depuis l'app de gestion
            
        Returns:
            Dict avec le produit créé/mis à jour et un flag 'created'
        """
        external_id = external_data.get('id')
        if not external_id:
            raise ValidationError("L'ID externe du produit est requis")
        
        # Chercher si le produit existe déjà
        external_product = ExternalProduct.objects.filter(
            external_id=external_id
        ).first()
        
        # Récupérer ou créer la catégorie depuis l'API B2B
        category = None
        external_category_id = None
        category_data = None
        
        # L'API B2B peut avoir category comme objet ou category_id comme entier
        if 'category' in external_data and isinstance(external_data['category'], dict):
            # Catégorie sous forme d'objet {id, name, slug, parent_id, etc.}
            category_data = external_data['category']
            external_category_id = category_data.get('id')
        else:
            # Catégorie sous forme d'ID direct
            external_category_id = external_data.get('category_id')
        
        # Chercher d'abord dans ExternalCategory
        if external_category_id:
            external_category = ExternalCategory.objects.filter(
                external_id=external_category_id
            ).first()
            if external_category:
                category = external_category.category
                logger.info(f"Catégorie trouvée via ExternalCategory: {category.name} (ID externe: {external_category_id})")
        
        # Si pas de catégorie trouvée mais qu'on a les données de la catégorie, créer la catégorie
        if not category and category_data:
            logger.warning(f"Catégorie non trouvée dans ExternalCategory pour ID externe {external_category_id}, création depuis les données API")
            try:
                # Créer la catégorie depuis les données de l'API
                category_result = self.create_or_update_category(category_data)
                category = category_result.get('category')
                logger.info(f"Catégorie créée/mise à jour depuis l'API: {category.name} (ID externe: {external_category_id})")
            except Exception as e:
                logger.error(f"Erreur lors de la création de la catégorie depuis l'API: {str(e)}")
        
        # Si toujours pas de catégorie et qu'on a juste l'ID, essayer de récupérer depuis l'API
        if not category and external_category_id:
            logger.warning(f"Tentative de récupération de la catégorie {external_category_id} depuis l'API B2B")
            try:
                category_detail = self.api_client.get_category_detail(external_category_id)
                if category_detail:
                    category_result = self.create_or_update_category(category_detail)
                    category = category_result.get('category')
                    logger.info(f"Catégorie récupérée depuis l'API B2B: {category.name} (ID externe: {external_category_id})")
            except Exception as e:
                logger.error(f"Erreur lors de la récupération de la catégorie depuis l'API: {str(e)}")
        
        # Si toujours pas de catégorie, lever une erreur explicite
        if not category:
            error_msg = (
                f"Impossible de trouver ou créer la catégorie pour le produit B2B (ID externe: {external_id}). "
                f"Category ID externe: {external_category_id}. "
                f"Veuillez synchroniser les catégories avant de synchroniser les produits."
            )
            logger.error(error_msg)
            raise ValidationError(error_msg)
        
        # Fonction helper pour convertir en nombre
        def to_number(value, default=0, is_integer=False):
            """Convertit une valeur en nombre (int ou float)
            
            Args:
                value: Valeur à convertir
                default: Valeur par défaut si la conversion échoue
                is_integer: Si True, force le retour en entier (pour stock, etc.)
            """
            if value is None:
                return default
            if isinstance(value, (int, float)):
                return int(value) if is_integer and isinstance(value, float) and value.is_integer() else value
            if isinstance(value, str):
                cleaned = value.strip()
                if not cleaned:
                    return default
                
                # Gérer les formats avec virgule comme séparateur décimal (format européen)
                if ',' in cleaned and '.' in cleaned:
                    # Format mixte: "1.234,56" ou "1,234.56"
                    # Si le dernier séparateur est une virgule, c'est un format européen
                    if cleaned.rindex(',') > cleaned.rindex('.'):
                        # Format européen: "1.234,56" -> "1234.56"
                        cleaned = cleaned.replace('.', '').replace(',', '.')
                    else:
                        # Format US: "1,234.56" -> "1234.56"
                        cleaned = cleaned.replace(',', '')
                elif ',' in cleaned:
                    # Format européen simple: "12,5" -> "12.5"
                    cleaned = cleaned.replace(',', '.')
                elif '.' in cleaned:
                    # Format avec point: "12.000" ou "12.5"
                    # Si c'est un entier avec point (ex: "12.000"), enlever le point
                    # Sinon, garder comme décimal
                    parts = cleaned.split('.')
                    if len(parts) == 2 and parts[1] == '0' * len(parts[1]):
                        # Format "12.000" -> entier 12
                        cleaned = parts[0]
                    # Sinon garder comme décimal "12.5"
                
                try:
                    num = float(cleaned)
                    # Si is_integer est True, retourner un entier
                    if is_integer:
                        return int(num)
                    # Sinon, retourner int si c'est un entier, sinon float
                    return int(num) if num.is_integer() else num
                except (ValueError, AttributeError):
                    return default
            return default
        
        # Détecter si le produit est vendu au poids
        # L'API B2B utilise 'sale_unit_type' avec la valeur 'weight'
        sold_by_weight = external_data.get('sold_by_weight', False) or \
                        external_data.get('by_weight', False) or \
                        external_data.get('sale_unit_type', '').lower() == 'weight' or \
                        external_data.get('unit_type', '').lower() in ['weight', 'kg', 'kilogram', 'poids'] or \
                        external_data.get('selling_unit', '').lower() in ['weight', 'kg', 'kilogram', 'poids']
        
        # Récupérer l'unité de poids (g, kg, etc.)
        weight_unit = external_data.get('weight_unit', 'kg')
        
        # Détecter si c'est un produit sur commande (Salam)
        # Un produit Salam est un produit fait sur commande, pas forcément un produit au poids
        # Un produit au poids peut avoir du stock disponible et être vendu directement
        is_salam_product = external_data.get('is_salam', False) or \
                          external_data.get('made_to_order', False) or \
                          external_data.get('on_demand', False)
        
        # Si le produit est au poids ET n'a pas de stock disponible, alors c'est un produit Salam
        # Sinon, un produit au poids avec stock peut être vendu directement
        if sold_by_weight and not is_salam_product:
            # Vérifier si le stock/poids disponible est suffisant pour une vente directe
            if weight_available is None or weight_available <= 0:
                # Pas de stock disponible = produit sur commande
                is_salam_product = True
            # Si weight_available > 0, le produit peut être vendu directement (is_salam = False)
        
        # Gérer le stock selon le type de produit
        # L'API B2B utilise 'quantity' (pas 'stock')
        stock_value = external_data.get('quantity') or external_data.get('stock') or external_data.get('available_quantity', 0)
        weight_available = None
        
        if sold_by_weight:
            # Pour les produits au poids, le stock est en poids (g, kg, etc.)
            # On stocke le poids disponible dans le champ weight
            weight_available = to_number(stock_value)
            
            # Convertir en kg si nécessaire (pour uniformiser)
            if weight_unit and weight_unit.lower() == 'g':
                weight_available = weight_available / 1000  # Convertir grammes en kg
            
            # Le stock en unités reste à 0 ou on met une valeur symbolique pour les produits au poids disponibles
            stock_units = 0 if is_salam_product else int(weight_available) if weight_available > 0 else 0
        else:
            # Produit normal vendu à l'unité
            stock_units = to_number(stock_value, is_integer=True)
        
        # Gérer le prix selon le type de produit
        # L'API B2B utilise 'selling_price' (pas 'price')
        price_value = external_data.get('selling_price') or external_data.get('price') or external_data.get('unit_price', 0)
        price_per_unit = to_number(price_value)
        
        # Initialiser les spécifications
        specifications = {}
        
        # Ajouter les informations B2B de base
        if 'slug' in external_data:
            specifications['b2b_slug'] = external_data['slug']
        
        if 'generated_ean' in external_data:
            specifications['ean'] = external_data['generated_ean']
            specifications['barcode'] = external_data['generated_ean']
        
        if 'alert_threshold' in external_data:
            # Seuil d'alerte de stock (quand alerter que le stock est bas)
            alert_threshold = to_number(external_data['alert_threshold'])
            if alert_threshold:
                specifications['alert_threshold'] = alert_threshold
        
        if 'unit_display' in external_data:
            # Unité d'affichage (ex: "g", "kg", "unité(s)")
            specifications['unit_display'] = external_data['unit_display']
        
        if 'formatted_quantity' in external_data:
            # Quantité formatée pour affichage
            specifications['formatted_quantity'] = external_data['formatted_quantity']
        
        # Ajouter les dates de création/mise à jour B2B
        if 'created_at' in external_data:
            specifications['b2b_created_at'] = external_data['created_at']
        if 'updated_at' in external_data:
            specifications['b2b_updated_at'] = external_data['updated_at']
        
        if sold_by_weight:
            # Stocker le prix au kg (ou g) dans les spécifications
            if weight_unit and weight_unit.lower() == 'g':
                # Si l'unité est en grammes, convertir le prix en prix au kg
                price_per_kg = price_per_unit * 1000
                specifications['price_per_kg'] = price_per_kg
                specifications['price_per_g'] = price_per_unit
            else:
                # Prix déjà au kg
                specifications['price_per_kg'] = price_per_unit
            
            specifications['sold_by_weight'] = True
            specifications['unit_type'] = 'weight'
            specifications['weight_unit'] = weight_unit or 'kg'
            if weight_available:
                specifications['available_weight_kg'] = weight_available
                if weight_unit and weight_unit.lower() == 'g':
                    specifications['available_weight_g'] = weight_available * 1000
        
        # Utiliser le slug B2B si disponible (pour cohérence avec l'API B2B)
        slug = None
        if 'slug' in external_data and external_data['slug']:
            slug = external_data['slug']
            # Vérifier que le slug est unique, sinon générer un nouveau
            from product.models import Product as ProductModel
            if ProductModel.objects.filter(slug=slug).exclude(id=external_product.product.id if external_product else None).exists():
                # Slug existe déjà, utiliser le slug généré par Django
                slug = None
        
        # Préparer les données du produit avec toutes les informations disponibles
        product_data = {
            'title': external_data.get('name') or external_data.get('title', 'Produit sans nom'),
            'description': external_data.get('description') or external_data.get('description_text', ''),
            'price': price_per_unit,
            'category': category,
            'stock': stock_units,
            'sku': external_data.get('cug') or external_data.get('sku') or external_data.get('code', ''),
            'is_available': external_data.get('is_available_b2c', 
                                            external_data.get('is_available', 
                                            external_data.get('is_active', 
                                            external_data.get('available', True)))),
            'is_salam': is_salam_product,
            'external_id': external_id,
            'external_sku': external_data.get('cug') or external_data.get('sku') or external_data.get('code', ''),
            'specifications': specifications,
        }
        
        # Ajouter le slug B2B si disponible et unique
        if slug:
            product_data['slug'] = slug
        
        # Ajouter le poids
        if sold_by_weight and weight_available:
            # Pour les produits au poids, le poids disponible est le stock
            product_data['weight'] = weight_available
        elif 'weight' in external_data and not sold_by_weight:
            # Poids du produit lui-même (pour la livraison) - seulement si pas un produit au poids
            product_data['weight'] = to_number(external_data['weight'])
        
        # Gérer les champs optionnels avec plusieurs variantes possibles
        if 'brand' in external_data:
            product_data['brand'] = external_data['brand']
        elif 'manufacturer' in external_data:
            product_data['brand'] = external_data['manufacturer']
        
        # Gérer le prix promotionnel (avec conversion)
        discount_price = None
        if 'discount_price' in external_data:
            discount_price = to_number(external_data['discount_price'])
        elif 'promotional_price' in external_data:
            discount_price = to_number(external_data['promotional_price'])
        elif 'sale_price' in external_data:
            discount_price = to_number(external_data['sale_price'])
        
        if discount_price and discount_price > 0:
            product_data['discount_price'] = discount_price
        
        # Gérer les images - peut être une URL unique ou une liste d'URLs
        image_urls = []
        
        # Vérifier si c'est une liste d'images
        if 'images' in external_data and isinstance(external_data['images'], list):
            image_urls = [img for img in external_data['images'] if img]
        elif 'image_urls' in external_data and isinstance(external_data['image_urls'], list):
            image_urls = [img for img in external_data['image_urls'] if img]
        elif 'gallery' in external_data and isinstance(external_data['gallery'], list):
            image_urls = [img for img in external_data['gallery'] if img]
        else:
            # Image unique
            image_url = None
            if 'image_url' in external_data and external_data['image_url']:
                image_url = external_data['image_url']
            elif 'image' in external_data and external_data['image']:
                image_url = external_data['image']
            elif 'main_image' in external_data and external_data['main_image']:
                image_url = external_data['main_image']
            elif 'photo' in external_data and external_data['photo']:
                image_url = external_data['photo']
            
            if image_url:
                image_urls = [image_url]
        
        # Stocker les URLs des images dans les spécifications pour référence
        if image_urls:
            specifications['b2b_image_urls'] = image_urls
            if len(image_urls) == 1:
                specifications['b2b_image_url'] = image_urls[0]  # Pour compatibilité
        
        # Ajouter les spécifications de l'API B2B (fusionner avec les spécifications existantes)
        if 'specifications' in external_data:
            if isinstance(external_data['specifications'], dict):
                product_data['specifications'].update(external_data['specifications'])
            else:
                product_data['specifications']['raw'] = external_data['specifications']
        elif 'attributes' in external_data:
            if isinstance(external_data['attributes'], dict):
                product_data['specifications'].update(external_data['attributes'])
            else:
                product_data['specifications']['attributes'] = external_data['attributes']
        elif 'features' in external_data:
            if isinstance(external_data['features'], dict):
                product_data['specifications'].update(external_data['features'])
            else:
                product_data['specifications']['features'] = external_data['features']
        
        # Gérer les dimensions (le poids est déjà géré plus haut)
        if 'dimensions' in external_data:
            product_data['dimensions'] = str(external_data['dimensions'])
        elif 'size' in external_data:
            product_data['dimensions'] = str(external_data['size'])
        
        # Gérer les tags et mots-clés pour améliorer la recherche
        if 'tags' in external_data:
            product_data['specifications']['tags'] = external_data['tags']
        
        # Ajouter le nom de catégorie B2B si disponible (pour référence)
        if 'category_name' in external_data:
            product_data['specifications']['b2b_category_name'] = external_data['category_name']
        elif 'category' in external_data and isinstance(external_data['category'], dict):
            category_name = external_data['category'].get('name')
            if category_name:
                product_data['specifications']['b2b_category_name'] = category_name
        
        if external_product:
            # Mettre à jour le produit existant
            product = external_product.product
            for key, value in product_data.items():
                setattr(product, key, value)
            
            # Générer le slug si nécessaire
            if not product.slug:
                product.slug = product.generate_unique_slug()
            
            product.save()
            created = False
        else:
            # Créer un nouveau produit
            product = Product(**product_data)
            if not product.slug:
                product.slug = product.generate_unique_slug()
            product.save()
            created = True
            
            # Créer l'ExternalProduct
            external_product = ExternalProduct.objects.create(
                product=product,
                external_id=external_id,
                external_sku=external_data.get('sku', ''),
                external_category_id=external_category_id,
                sync_status='synced',
                last_synced_at=timezone.now()
            )
        
        # Mettre à jour ExternalProduct
        external_product.sync_status = 'synced'
        external_product.last_synced_at = timezone.now()
        external_product.sync_error = None
        external_product.save()
        
        # Télécharger et sauvegarder les images si disponibles
        if image_urls:
            try:
                # Télécharger la première image comme image principale
                main_image_url = image_urls[0]
                if not product.image or (created and main_image_url):
                    image_path = self.download_and_save_image(main_image_url, product, is_main=True, order=0)
                    if image_path:
                        logger.info(f"Image principale téléchargée avec succès pour le produit {product.id}")
                    else:
                        logger.warning(f"Impossible de télécharger l'image principale pour le produit {product.id}")
                else:
                    logger.debug(f"Image principale déjà présente pour le produit {product.id}, pas de téléchargement")
                
                # Télécharger les images supplémentaires dans la galerie
                if len(image_urls) > 1:
                    for idx, gallery_image_url in enumerate(image_urls[1:], start=1):
                        try:
                            # Vérifier si l'image existe déjà à cet ordre
                            existing_image = ImageProduct.objects.filter(
                                product=product,
                                ordre=idx
                            ).first()
                            
                            if not existing_image or created:
                                image_path = self.download_and_save_image(
                                    gallery_image_url, 
                                    product, 
                                    is_main=False, 
                                    order=idx
                                )
                                if image_path:
                                    logger.info(f"Image de galerie {idx} téléchargée avec succès pour le produit {product.id}")
                                else:
                                    logger.warning(f"Impossible de télécharger l'image de galerie {idx} pour le produit {product.id}")
                            else:
                                logger.debug(f"Image de galerie {idx} déjà présente pour le produit {product.id}")
                        except Exception as e:
                            logger.error(f"Erreur lors du téléchargement de l'image de galerie {idx} pour le produit {product.id}: {str(e)}", exc_info=True)
                            # Continuer avec les autres images même en cas d'erreur
                
                # Mettre à jour image_urls si nécessaire
                product.update_image_urls()
                
            except Exception as e:
                logger.error(f"Erreur lors du téléchargement des images pour le produit {product.id}: {str(e)}", exc_info=True)
                # Ne pas faire échouer la synchronisation si les images ne peuvent pas être téléchargées
        
        return {
            'product': product,
            'created': created,
            'external_product': external_product
        }
    
    @transaction.atomic
    def create_or_update_category(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée ou met à jour une catégorie dans SagaKore à partir des données de l'app de gestion
        
        Args:
            external_data: Données de la catégorie depuis l'app de gestion
            
        Returns:
            Dict avec la catégorie créée/mise à jour et un flag 'created'
        """
        external_id = external_data.get('id')
        if not external_id:
            raise ValidationError("L'ID externe de la catégorie est requis")
        
        # Chercher si la catégorie existe déjà
        external_category = ExternalCategory.objects.filter(
            external_id=external_id
        ).first()
        
        # Préparer les données de la catégorie
        # Gérer parent_id qui peut être un entier ou un objet avec un id
        parent_id = external_data.get('parent_id')
        if not parent_id and 'parent' in external_data:
            if isinstance(external_data['parent'], dict):
                parent_id = external_data['parent'].get('id')
            elif isinstance(external_data['parent'], int):
                parent_id = external_data['parent']
        
        category_data = {
            'name': external_data.get('name', 'Catégorie sans nom'),
            'description': external_data.get('description', ''),
            'external_id': external_id,
            'external_parent_id': parent_id,
            'rayon_type': external_data.get('rayon_type'),
            'level': external_data.get('level'),
            'order': external_data.get('order', 0),
        }
        
        # Gérer le slug - générer un slug unique
        # Si la catégorie existe déjà, conserver son slug existant pour éviter les conflits
        if external_category and external_category.category:
            # Utiliser le slug existant si disponible, sinon en générer un nouveau
            existing_slug = external_category.category.slug
            if existing_slug and not Category.objects.filter(slug=existing_slug).exclude(id=external_category.category.id).exists():
                slug = existing_slug
            else:
                # Générer un nouveau slug unique
                base_slug = slugify(category_data['name'])
                slug = base_slug
                counter = 1
                while Category.objects.filter(slug=slug).exclude(id=external_category.category.id).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
        else:
            # Nouvelle catégorie - générer un slug unique
            base_slug = slugify(category_data['name'])
            slug = base_slug
            counter = 1
            # Utiliser l'ID externe pour garantir l'unicité si nécessaire
            while Category.objects.filter(slug=slug).exists():
                # Ajouter l'ID externe au slug pour garantir l'unicité
                slug = f"{base_slug}-{external_id}" if counter == 1 else f"{base_slug}-{external_id}-{counter}"
                counter += 1
        category_data['slug'] = slug
        
        # Déterminer le parent Category à partir de external_parent_id
        parent_category = None
        if parent_id:
            try:
                parent_external_category = ExternalCategory.objects.filter(
                    external_id=parent_id
                ).first()
                if parent_external_category:
                    parent_category = parent_external_category.category
            except Exception as e:
                logger.warning(f"Impossible de trouver le parent pour external_parent_id={parent_id}: {str(e)}")
        
        if external_category:
            # Mettre à jour la catégorie existante
            category = external_category.category
            for key, value in category_data.items():
                if key not in ['external_id', 'external_parent_id']:  # Ces champs sont gérés séparément
                    setattr(category, key, value)
            # Définir le parent
            category.parent = parent_category
            category.save()
            created = False
        else:
            # Créer une nouvelle catégorie
            category = Category(**{k: v for k, v in category_data.items() if k not in ['external_id', 'external_parent_id']})
            # S'assurer que le slug est défini
            if not category.slug:
                category.slug = category_data['slug']
            # Définir le parent
            category.parent = parent_category
            category.save()
            created = True
            
            # Créer l'ExternalCategory
            external_category = ExternalCategory.objects.create(
                category=category,
                external_id=external_id,
                external_parent_id=parent_id,
                last_synced_at=timezone.now()
            )
        
        # Mettre à jour ExternalCategory
        external_category.last_synced_at = timezone.now()
        external_category.save()
        
        return {
            'category': category,
            'created': created,
            'external_category': external_category
        }


# Note: SaleSyncService a été supprimé car il dépendait de InventoryConnection et SaleSync
# La synchronisation des ventes doit être gérée manuellement ou via des commandes de management

