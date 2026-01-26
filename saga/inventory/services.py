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
# Imports pour téléchargement d'images supprimés - on ne stocke plus les images B2B localement
# from django.core.files.base import ContentFile
# from django.core.files.storage import default_storage
# from io import BytesIO
# from PIL import Image
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
    
    def __init__(self, token: Optional[str] = None, api_key_id: Optional[int] = None, api_key_name: Optional[str] = None):
        """
        Initialise le client API
        
        Note: Le token API est récupéré depuis ApiKey.get_active_key()
        ou depuis settings.B2B_API_KEY en fallback si aucun token n'est fourni.
        """
        # Utiliser l'URL par défaut depuis settings
        self.base_url = getattr(settings, 'B2B_API_URL', 'https://www.bolibanastock.com/api/v1').rstrip('/')
        logger.info(f"URL API configurée: {self.base_url}")
        
        # Récupérer le token : depuis ApiKey active ou depuis settings, sauf si fourni
        self.token = token or ApiKey.get_active_key()
        self.api_key_id = api_key_id
        self.api_key_name = api_key_name
        
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
        if self.api_key_name or self.api_key_id:
            logger.info(
                f"Clé API utilisée: {masked_token} (id={self.api_key_id}, name='{self.api_key_name}')"
            )
        else:
            logger.info(f"Clé API utilisée: {masked_token}")
        
        # Enregistrer l'utilisation de la clé si elle existe
        api_key_obj = None
        if self.api_key_id:
            api_key_obj = ApiKey.objects.filter(id=self.api_key_id).first()
        else:
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
        
        # Log du payload pour les requêtes POST/PUT avec JSON
        if method in ['POST', 'PUT'] and 'json' in kwargs:
            import json
            payload = kwargs.get('json', {})
            logger.info(f"Payload {method} vers {url}: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
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
    
    # NOTE: Méthode de téléchargement d'images supprimée
    # On ne stocke plus les images B2B localement, on conserve uniquement les URLs
    # Les URLs sont stockées dans specifications['b2b_image_urls'] et exposées via l'API
    
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
            'errors_list': [],
            'skipped': 0,
            'skipped_reasons': {}
        }
        
        logger.info("=" * 80)
        logger.info("[SYNC B2B] 🚀 Démarrage synchronisation produits B2B")
        logger.info("=" * 80)
        
        keys = ApiKey.get_active_keys()
        if not keys:
            logger.error("[SYNC B2B] Aucune clé API disponible pour la synchronisation")
            return stats

        processed_external_ids = set()
        all_b2b_product_ids = set()

        for key_info in keys:
            key_label = f"id={key_info.get('id')}, name='{key_info.get('name')}'"
            logger.info(f"[SYNC B2B] 🔑 Synchronisation via clé: {key_label}")

            api_client = InventoryAPIClient(
                token=key_info.get('key'),
                api_key_id=key_info.get('id'),
                api_key_name=key_info.get('name')
            )

            page = 1
            has_next = True

            while has_next:
                try:
                    response = api_client.get_products_list(site_id=site_id, page=page)

                    # Gérer différents formats de réponse
                    if isinstance(response, dict):
                        products = response.get('results', response.get('products', []))
                        has_next = response.get('next') is not None
                    else:
                        products = response if isinstance(response, list) else []
                        has_next = False

                    logger.info(f"[SYNC B2B] 📄 Page {page}: {len(products)} produits récupérés")

                    for product_data in products:
                        try:
                            # Récupérer les détails complets du produit pour avoir toutes les informations
                            external_id = product_data.get('id')
                            if external_id:
                                if external_id in processed_external_ids:
                                    stats['skipped'] += 1
                                    stats['skipped_reasons']['duplicate_external_id'] = (
                                        stats['skipped_reasons'].get('duplicate_external_id', 0) + 1
                                    )
                                    logger.debug(
                                        f"[SYNC B2B] 🔁 Produit déjà traité (id={external_id}), clé={key_label}"
                                    )
                                    continue

                                processed_external_ids.add(external_id)
                                all_b2b_product_ids.add(external_id)
                                try:
                                    # Récupérer les détails complets depuis l'API
                                    detailed_product_data = api_client.get_product_detail(external_id)

                                    # Log des images avant fusion pour debug
                                    list_images = product_data.get('images') or product_data.get('image_urls') or product_data.get('gallery') or product_data.get('image_url') or product_data.get('image')
                                    detail_images = detailed_product_data.get('images') or detailed_product_data.get('image_urls') or detailed_product_data.get('gallery') or detailed_product_data.get('image_url') or detailed_product_data.get('image')

                                    logger.debug(f"[SYNC IMAGES] 📋 Avant fusion - Produit {external_id}:")
                                    logger.debug(f"  - Images LISTE: {list_images}")
                                    logger.debug(f"  - Images DÉTAIL: {detail_images}")

                                    # Fusionner les données de la liste avec les détails complets
                                    # Les détails complets ont priorité
                                    product_data = {**product_data, **detailed_product_data}

                                    # Log après fusion
                                    merged_images = product_data.get('images') or product_data.get('image_urls') or product_data.get('gallery') or product_data.get('image_url') or product_data.get('image')
                                    logger.debug(f"  - Images APRÈS FUSION: {merged_images}")

                                    # Si le détail n'a pas d'images mais que la liste en a, les restaurer
                                    if not detail_images and list_images:
                                        if isinstance(list_images, list):
                                            product_data['images'] = list_images
                                        else:
                                            product_data['image_url'] = list_images
                                        logger.debug(f"[SYNC IMAGES] 🔄 Images de la liste restaurées (détail sans images) pour produit {external_id}")
                                except InventoryAPIError as e:
                                    logger.warning(
                                        f"Impossible de récupérer les détails du produit {external_id}: {str(e)}. "
                                        f"Utilisation des données de base. clé={key_label}"
                                    )
                                    # Continuer avec les données de base si les détails ne sont pas disponibles

                            result = self.create_or_update_product(
                                product_data,
                                api_key_id=key_info.get('id'),
                                api_key_name=key_info.get('name')
                            )
                            stats['total'] += 1
                            if result['created']:
                                stats['created'] += 1
                                logger.info(f"[SYNC B2B] ✅ Produit {external_id} créé: {product_data.get('name', 'N/A')}")
                            else:
                                stats['updated'] += 1
                                logger.debug(f"[SYNC B2B] 🔄 Produit {external_id} mis à jour: {product_data.get('name', 'N/A')}")
                        except Exception as e:
                            external_id = product_data.get('id', 'N/A')
                            error_msg = str(e)
                            stats['errors'] += 1
                            stats['errors_list'].append({
                                'product_id': external_id,
                                'error': error_msg,
                                'api_key_id': key_info.get('id'),
                                'api_key_name': key_info.get('name')
                            })

                            # Catégoriser les erreurs pour statistiques
                            if 'catégorie' in error_msg.lower() or 'category' in error_msg.lower():
                                reason = 'category_missing'
                            elif 'validation' in error_msg.lower():
                                reason = 'validation_error'
                            else:
                                reason = 'other_error'

                            if reason not in stats['skipped_reasons']:
                                stats['skipped_reasons'][reason] = 0
                            stats['skipped_reasons'][reason] += 1
                            stats['skipped'] += 1

                            logger.error(f"[SYNC B2B] ❌ Erreur produit {external_id}: {error_msg} (clé={key_label})")

                    page += 1

                except InventoryAPIError as e:
                    logger.error(f"[SYNC B2B] ❌ Erreur API page {page} (clé={key_label}): {str(e)}")
                    has_next = False
                    stats['errors'] += 1
        
        # Résumé final de la synchronisation
        logger.info("=" * 80)
        logger.info("[SYNC B2B] 📊 RÉSUMÉ SYNCHRONISATION")
        logger.info("=" * 80)
        logger.info(f"Total produits B2B dans l'API: {len(all_b2b_product_ids)}")
        logger.info(f"Produits traités: {stats['total']}")
        logger.info(f"  - Créés: {stats['created']}")
        logger.info(f"  - Mis à jour: {stats['updated']}")
        logger.info(f"  - Erreurs: {stats['errors']}")
        logger.info(f"  - Ignorés: {stats['skipped']}")
        
        if stats['skipped_reasons']:
            logger.info("Raisons des produits ignorés:")
            for reason, count in stats['skipped_reasons'].items():
                logger.info(f"  - {reason}: {count}")
        
        # Vérifier combien de produits synchronisés sont disponibles
        from .models import ExternalProduct
        synced_count = ExternalProduct.objects.filter(
            external_id__in=all_b2b_product_ids,
            sync_status='synced',
            is_b2b=True
        ).count()
        
        from product.models import Product
        synced_with_product = ExternalProduct.objects.filter(
            external_id__in=all_b2b_product_ids,
            sync_status='synced',
            is_b2b=True,
            product__isnull=False
        )
        product_ids = [ep.product.id for ep in synced_with_product if ep.product]
        available_count = Product.objects.filter(
            id__in=product_ids,
            is_available=True
        ).count()
        
        logger.info(f"Produits synchronisés (sync_status='synced' + is_b2b=True): {synced_count}")
        logger.info(f"Produits avec relation Product: {len(product_ids)}")
        logger.info(f"Produits disponibles (is_available=True): {available_count}")
        
        gap = len(all_b2b_product_ids) - synced_count
        if gap > 0:
            logger.warning(f"⚠️  {gap} produits B2B ne sont pas synchronisés")
        
        gap_available = len(product_ids) - available_count
        if gap_available > 0:
            logger.warning(f"⚠️  {gap_available} produits synchronisés ne sont pas disponibles (is_available=False)")
        
        logger.info("=" * 80)
        
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
            return self.create_or_update_product(
                product_data,
                api_key_id=getattr(self.api_client, 'api_key_id', None),
                api_key_name=getattr(self.api_client, 'api_key_name', None)
            )
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
            'deleted': 0,
            'errors': 0,
            'duplicates': 0,
            'errors_list': []
        }
        
        try:
            keys = ApiKey.get_active_keys()
            if not keys:
                logger.error("[SYNC CAT] Aucune clé API disponible pour la synchronisation")
                return stats

            logger.info("[SYNC CAT] Récupération des catégories depuis l'API B2B (multi clés)")
            categories_data = []
            external_ids_seen = set()

            for key_info in keys:
                key_label = f"id={key_info.get('id')}, name='{key_info.get('name')}'"
                api_client = InventoryAPIClient(
                    token=key_info.get('key'),
                    api_key_id=key_info.get('id'),
                    api_key_name=key_info.get('name')
                )
                key_categories = api_client.get_categories_list()
                logger.info(f"[SYNC CAT] Catégories reçues (clé {key_label}): {len(key_categories)}")

                for category_data in key_categories:
                    external_id = category_data.get('id')
                    if external_id in external_ids_seen:
                        stats['duplicates'] += 1
                        logger.debug(
                            f"[SYNC CAT] Catégorie déjà vue (id={external_id}), clé={key_label}"
                        )
                        continue
                    external_ids_seen.add(external_id)
                    categories_data.append(category_data)

            logger.info(f"[SYNC CAT] Catégories uniques retenues: {len(categories_data)}")
            external_ids = {
                int(cat_id) for cat_id in (
                    category_data.get('id') for category_data in categories_data
                ) if cat_id is not None
            }
            
            # Créer un mapping des catégories par ID externe pour gérer la hiérarchie
            categories_by_id = {}
            
            # Première passe : créer/mettre à jour toutes les catégories
            for category_data in categories_data:
                try:
                    external_id = category_data.get('id')
                    logger.debug(f"[SYNC CAT] Traitement catégorie externe id={external_id}")
                    result = self.create_or_update_category(category_data)
                    stats['total'] += 1
                    if result['created']:
                        stats['created'] += 1
                    else:
                        stats['updated'] += 1
                    
                    if external_id:
                        categories_by_id[external_id] = result['category']
                except Exception as e:
                    stats['errors'] += 1
                    stats['errors_list'].append({
                        'category_id': category_data.get('id'),
                        'error': str(e)
                    })
                    logger.error(f"Erreur lors de la synchronisation de la catégorie {category_data.get('id')}: {str(e)}")
            
            # Deuxième passe : établir les relations parent/enfant (pour les cas où l'ordre de création n'est pas hiérarchique)
            for category_data in categories_data:
                external_id = category_data.get('id')
                # Gérer parent_id qui peut être un entier ou un objet avec un id (comme dans create_or_update_category)
                parent_id = category_data.get('parent_id')
                if not parent_id and 'parent' in category_data:
                    if isinstance(category_data['parent'], dict):
                        parent_id = category_data['parent'].get('id')
                    elif isinstance(category_data['parent'], int):
                        parent_id = category_data['parent']
                    elif category_data['parent'] is None:
                        parent_id = None
                
                if external_id and parent_id and external_id in categories_by_id and parent_id in categories_by_id:
                    category = categories_by_id[external_id]
                    parent_category = categories_by_id[parent_id]
                    # Mettre à jour seulement si le parent a changé
                    if category.parent != parent_category:
                        category.parent = parent_category
                        category.save(update_fields=['parent'])
                        logger.debug(f"Relation parent/enfant mise à jour: {category.name} -> {parent_category.name}")

            # Nettoyer les catégories supprimées côté B2B (supprimer le mapping externe)
            stale_qs = ExternalCategory.objects.exclude(external_id__in=external_ids)
            stale_count = stale_qs.count()
            if stale_count:
                stale_preview = list(
                    stale_qs.select_related('category')
                    .values_list('external_id', 'category__name')[:10]
                )
                logger.warning(
                    f"[SYNC CAT] {stale_count} catégories supprimées côté B2B détectées. "
                    f"Exemples: {stale_preview}"
                )
                for stale in stale_qs.select_related('category'):
                    # Garder la catégorie locale mais retirer la référence B2B
                    category = stale.category
                    category.external_id = None
                    category.external_parent_id = None
                    category.save(update_fields=['external_id', 'external_parent_id'])
                stale_qs.delete()
                stats['deleted'] = stale_count
        except InventoryAPIError as e:
            logger.error(f"Erreur API lors de la synchronisation des catégories: {str(e)}")
            stats['errors'] += 1
        
        logger.info(
            "[SYNC CAT] Résumé: "
            f"total={stats['total']} created={stats['created']} "
            f"updated={stats['updated']} deleted={stats.get('deleted', 0)} "
            f"errors={stats.get('errors', 0)} duplicates={stats.get('duplicates', 0)}"
        )

        return stats
    
    @transaction.atomic
    def create_or_update_product(
        self,
        external_data: Dict[str, Any],
        api_key_id: Optional[int] = None,
        api_key_name: Optional[str] = None
    ) -> Dict[str, Any]:
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
        
        # Si toujours pas de catégorie, permettre la synchronisation sans catégorie
        if not category:
            logger.warning(
                f"Produit B2B (ID externe: {external_id}) sans catégorie. "
                f"Category ID externe: {external_category_id}. "
                f"Synchronisation sans catégorie (category=None)."
            )
            # category reste None - le produit sera synchronisé sans catégorie
        
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

        def to_number_or_none(value, is_integer=False):
            """Convertit une valeur en nombre ou None si vide."""
            if value is None or value == '':
                return None
            return to_number(value, default=None, is_integer=is_integer)
        
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

        # Si le produit est au poids ET n'a pas de stock disponible, alors c'est un produit Salam
        # (IMPORTANT: weight_available est calculé plus haut, pour éviter "variable not associated with a value")
        if sold_by_weight and not is_salam_product:
            if weight_available is None or weight_available <= 0:
                is_salam_product = True
                # Mettre à jour stock_units si nécessaire (produit au poids sur commande)
                stock_units = 0
        
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

        # Méthodes de livraison (B2B)
        delivery_methods_raw = external_data.get('delivery_methods') or external_data.get('shipping_methods')
        if isinstance(delivery_methods_raw, list):
            normalized_methods = []
            for method in delivery_methods_raw:
                if not isinstance(method, dict):
                    continue
                method_id = method.get('id')
                method_name = method.get('name')
                if method_id is None or method_name is None:
                    continue
                normalized_methods.append({
                    'id': method_id,
                    'name': method_name,
                    'slug': method.get('slug'),
                    'description': method.get('description'),
                    'base_price': to_number_or_none(method.get('base_price')),
                    'effective_price': to_number_or_none(method.get('effective_price')),
                    'override_price': to_number_or_none(method.get('override_price')),
                    'order': to_number_or_none(method.get('order'), is_integer=True),
                    'site_configuration': to_number_or_none(method.get('site_configuration'), is_integer=True),
                })
            if normalized_methods:
                specifications['delivery_methods'] = normalized_methods
        
        # Utiliser le slug B2B si disponible (pour cohérence avec l'API B2B)
        slug = None
        if 'slug' in external_data and external_data['slug']:
            slug = external_data['slug']
            # Vérifier que le slug est unique, sinon générer un nouveau
            from product.models import Product as ProductModel
            if ProductModel.objects.filter(slug=slug).exclude(id=external_product.product.id if external_product else None).exists():
                # Slug existe déjà, utiliser le slug généré par Django
                slug = None
        
        # Déterminer is_available avec priorité
        is_available_value = external_data.get('is_available_b2c', 
                                            external_data.get('is_available', 
                                            external_data.get('is_active', 
                                            external_data.get('available', True))))
        
        # Préparer les données du produit avec toutes les informations disponibles
        product_data = {
            'title': external_data.get('name') or external_data.get('title', 'Produit sans nom'),
            'description': external_data.get('description') or external_data.get('description_text', ''),
            'price': price_per_unit,
            'stock': stock_units,
            'sku': external_data.get('cug') or external_data.get('sku') or external_data.get('code', ''),
            'is_available': is_available_value,
            'is_salam': is_salam_product,
            'external_id': external_id,
            'external_sku': external_data.get('cug') or external_data.get('sku') or external_data.get('code', ''),
            'specifications': specifications,
        }
        
        # Ajouter la catégorie seulement si elle existe
        if category:
            product_data['category'] = category
        
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

        # NOUVEAU (API B2B): promo_price + has_promotion + dates
        # Exemple:
        # - "promo_price": "100000.00"
        # - "has_promotion": true
        # - "discount_percent": "50.00"
        # - "promotion_start_date": "2026-01-11T17:07:00+00:00"
        # - "promotion_end_date": "2026-02-10T23:00:00+00:00"
        has_promotion = external_data.get('has_promotion', False) is True
        promo_price_value = external_data.get('promo_price')
        if has_promotion and promo_price_value is not None:
            promo_price = to_number(promo_price_value)
            if promo_price and promo_price > 0:
                discount_price = promo_price
                # Stocker les infos promo dans specifications (pour exposition API / debug)
                product_data['specifications']['has_promotion'] = True
                product_data['specifications']['promo_price'] = promo_price
                if 'discount_percent' in external_data and external_data.get('discount_percent') is not None:
                    product_data['specifications']['discount_percent'] = to_number(external_data.get('discount_percent'))
                if external_data.get('promotion_start_date'):
                    product_data['specifications']['promotion_start_date'] = str(external_data.get('promotion_start_date'))
                if external_data.get('promotion_end_date'):
                    product_data['specifications']['promotion_end_date'] = str(external_data.get('promotion_end_date'))
        
        if discount_price and discount_price > 0:
            product_data['discount_price'] = discount_price
        
        # Gérer les images - peut être une URL unique ou une liste d'URLs
        image_urls = []
        
        # Log détaillé des images reçues depuis l'API B2B (pour debug)
        logger.debug(f"[SYNC IMAGES] Produit ID externe {external_id} - Images reçues depuis API B2B:")
        logger.info(f"  - 'images': {external_data.get('images')}")
        logger.info(f"  - 'image_urls': {external_data.get('image_urls')}")
        logger.info(f"  - 'gallery': {external_data.get('gallery')}")
        logger.info(f"  - 'image_url': {external_data.get('image_url')}")
        logger.info(f"  - 'image': {external_data.get('image')}")
        logger.info(f"  - 'main_image': {external_data.get('main_image')}")
        logger.info(f"  - 'photo': {external_data.get('photo')}")
        
        # Vérifier si c'est une liste d'images
        if 'images' in external_data and isinstance(external_data['images'], list):
            image_urls = [img for img in external_data['images'] if img]
            logger.debug(f"[SYNC IMAGES] Utilisation de 'images' (liste): {len(image_urls)} images")
        elif 'image_urls' in external_data and isinstance(external_data['image_urls'], list):
            image_urls = [img for img in external_data['image_urls'] if img]
            logger.debug(f"[SYNC IMAGES] Utilisation de 'image_urls' (liste): {len(image_urls)} images")
        elif 'gallery' in external_data and isinstance(external_data['gallery'], list):
            image_urls = [img for img in external_data['gallery'] if img]
            logger.debug(f"[SYNC IMAGES] Utilisation de 'gallery' (liste): {len(image_urls)} images")
        
        # Si on a une liste d'images, prioriser les images "processed" (traitées/optimisées)
        if image_urls:
            # Chercher les images "processed" en premier
            processed_images = [img for img in image_urls if 'processed' in img.lower()]
            if processed_images:
                # Réorganiser : images processed en premier
                other_images = [img for img in image_urls if 'processed' not in img.lower()]
                image_urls = processed_images + other_images
                logger.debug(f"[SYNC IMAGES] 🔄 Réorganisation: {len(processed_images)} images 'processed' priorisées sur {len(image_urls)} total")
        else:
            # Image unique - priorité selon l'ordre de vérification
            image_url = None
            if 'image_url' in external_data and external_data['image_url']:
                image_url = external_data['image_url']
                logger.debug(f"[SYNC IMAGES] Utilisation de 'image_url': {image_url}")
            elif 'image' in external_data and external_data['image']:
                image_url = external_data['image']
                logger.debug(f"[SYNC IMAGES] Utilisation de 'image': {image_url}")
            elif 'main_image' in external_data and external_data['main_image']:
                image_url = external_data['main_image']
                logger.debug(f"[SYNC IMAGES] Utilisation de 'main_image': {image_url}")
            elif 'photo' in external_data and external_data['photo']:
                image_url = external_data['photo']
                logger.debug(f"[SYNC IMAGES] Utilisation de 'photo': {image_url}")
            
            if image_url:
                image_urls = [image_url]
        
        # Log final des URLs stockées
        if image_urls:
            logger.debug(f"[SYNC IMAGES] ✅ URLs finales stockées dans specifications['b2b_image_urls']: {image_urls}")
            specifications['b2b_image_urls'] = image_urls
            if len(image_urls) == 1:
                specifications['b2b_image_url'] = image_urls[0]  # Pour compatibilité
        else:
            logger.warning(f"[SYNC IMAGES] ⚠️ Aucune image trouvée pour le produit ID externe {external_id}")
        
        # IMPORTANT: Sauvegarder les b2b_image_urls avant la fusion des specifications
        # pour éviter qu'elles soient écrasées par les specifications de l'API
        saved_b2b_image_urls = specifications.get('b2b_image_urls')
        saved_b2b_image_url = specifications.get('b2b_image_url')
        
        # Ajouter les spécifications de l'API B2B (fusionner avec les spécifications existantes)
        if 'specifications' in external_data:
            if isinstance(external_data['specifications'], dict):
                # Fusionner les specifications mais préserver b2b_image_urls
                external_specs = external_data['specifications'].copy()
                # Retirer les clés d'images de external_specs pour éviter l'écrasement
                external_specs.pop('b2b_image_urls', None)
                external_specs.pop('b2b_image_url', None)
                product_data['specifications'].update(external_specs)
            else:
                product_data['specifications']['raw'] = external_data['specifications']
        
        # Restaurer les b2b_image_urls après la fusion (elles ont priorité)
        if saved_b2b_image_urls:
            product_data['specifications']['b2b_image_urls'] = saved_b2b_image_urls
            logger.debug(f"[SYNC IMAGES] 🔒 URLs restaurées après fusion specifications: {saved_b2b_image_urls}")
        if saved_b2b_image_url:
            product_data['specifications']['b2b_image_url'] = saved_b2b_image_url
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
                api_key_id=api_key_id,
                api_key_name=api_key_name,
                is_b2b=True,
                sync_status='synced',
                last_synced_at=timezone.now()
            )
        
        # Mettre à jour ExternalProduct
        external_product.sync_status = 'synced'
        external_product.last_synced_at = timezone.now()
        external_product.sync_error = None
        # IMPORTANT: ces produits proviennent de la synchro B2B → marquer is_b2b=True
        external_product.is_b2b = True
        if api_key_id is not None:
            external_product.api_key_id = api_key_id
        if api_key_name:
            external_product.api_key_name = api_key_name
        external_product.save()
        
        # Logger le statut is_available pour diagnostic
        if not is_available_value:
            logger.warning(
                f"[SYNC B2B] ⚠️  Produit {external_id} synchronisé mais is_available=False "
                f"(ne sera pas visible dans l'API /api/inventory/products/synced/)"
            )
        
        # IMPORTANT (choix produit):
        # On NE télécharge PAS les images B2B.
        # On conserve uniquement les URLs reçues (stockées dans specifications['b2b_image_urls'])
        # et l'API les expose au mobile via les serializers (gallery/images/image_url).
        
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
            elif external_data['parent'] is None:
                parent_id = None
        
        # Normaliser rayon_type et level (gérer les chaînes vides et None)
        rayon_type = external_data.get('rayon_type')
        if rayon_type == '' or rayon_type is None:
            rayon_type = None
        
        level = external_data.get('level')
        if level is None:
            # Essayer de déduire le level depuis parent_id
            level = 0 if not parent_id else None
        
        # Récupérer is_rayon si présent dans les données B2B
        is_rayon = external_data.get('is_rayon', False)
        
        raw_image_url = external_data.get('image_url') or external_data.get('image')
        if isinstance(raw_image_url, dict):
            raw_image_url = raw_image_url.get('url') or raw_image_url.get('image') or raw_image_url.get('image_url')
        if raw_image_url and not isinstance(raw_image_url, str):
            raw_image_url = None

        category_data = {
            'name': external_data.get('name', 'Catégorie sans nom'),
            'description': external_data.get('description', ''),
            'external_id': external_id,
            'external_parent_id': parent_id,
            'rayon_type': rayon_type,
            'level': level,
            'order': external_data.get('order', 0),
            'is_main': external_data.get('level', 0) == 0 if level is not None else (not parent_id),
            'image_url': raw_image_url or None,
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
            # Mettre à jour tous les champs sauf ceux gérés séparément
            for key, value in category_data.items():
                if key not in ['external_id', 'external_parent_id']:
                    setattr(category, key, value)
            # Mettre à jour external_id et external_parent_id dans Category (champs directs du modèle)
            category.external_id = external_id
            category.external_parent_id = parent_id
            # Définir le parent
            category.parent = parent_category
            category.save()
            created = False
        else:
            # Créer une nouvelle catégorie
            # Inclure external_id et external_parent_id car ce sont des champs du modèle Category
            category = Category(**category_data)
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
        
        # Mettre à jour ExternalCategory (y compris external_parent_id si changé)
        external_category.external_parent_id = parent_id
        external_category.last_synced_at = timezone.now()
        external_category.save()
        
        return {
            'category': category,
            'created': created,
            'external_category': external_category
        }


# Note: SaleSyncService a été supprimé car il dépendait de InventoryConnection et SaleSync
# La synchronisation des ventes doit être gérée manuellement ou via des commandes de management


class OrderSyncService:
    """
    Service pour synchroniser les commandes SagaKore vers l'app de gestion B2B
    """
    
    def __init__(self):
        self.api_client = InventoryAPIClient()
    
    def prepare_order_payload(self, order: Order) -> Dict[str, Any]:
        """
        Prépare le payload B2B à partir d'une commande SagaKore
        
        Args:
            order: Instance de Order
            
        Returns:
            Dict contenant les données formatées pour l'API B2B
        """
        items = []
        site_id = None
        
        # Récupérer le site_id depuis les métadonnées de la commande
        if order.metadata and 'delivery_site_configuration' in order.metadata:
            site_id = order.metadata.get('delivery_site_configuration')
        
        # Si pas de site_id dans metadata, essayer de le récupérer depuis le shipping_method
        if not site_id and order.shipping_method:
            # Le site_id peut être stocké dans les spécifications du shipping_method
            # ou dans les métadonnées de la commande
            pass
        
        # Par défaut, utiliser le premier site disponible si aucun n'est spécifié
        if not site_id:
            try:
                sites = self.api_client.get_sites_list()
                if sites and len(sites) > 0:
                    site_id = sites[0].get('id') if isinstance(sites[0], dict) else sites[0]
            except Exception as e:
                logger.warning(f"Impossible de récupérer les sites B2B: {str(e)}")
        
        # Construire les items de la commande
        for order_item in order.items.select_related('product').all():
            # Récupérer l'ID externe du produit
            try:
                external_product = ExternalProduct.objects.get(product=order_item.product)
                external_id = external_product.external_id
            except ExternalProduct.DoesNotExist:
                logger.warning(
                    f"Produit {order_item.product.id} ({order_item.product.title}) "
                    f"n'a pas de mapping B2B - ignoré dans la synchronisation"
                )
                continue
            
            # Déterminer l'unité de vente pour les produits au poids
            specs = order_item.product.specifications or {}
            unit = order_item.get_weight_unit() if hasattr(order_item, 'get_weight_unit') else 'unit'
            sold_by_weight = specs.get('sold_by_weight') is True or unit in ['kg', 'g']
            sale_unit_type = 'weight' if sold_by_weight else 'unit'
            weight_unit = unit if sold_by_weight else None

            # Convertir la quantité en float/int selon le besoin
            quantity = float(order_item.quantity)
            price = float(order_item.price)
            
            item_payload = {
                'product_id': external_id,
                'quantity': quantity,
                'price': price,
                'site_id': site_id,
                'sale_unit_type': sale_unit_type,
            }
            if weight_unit:
                item_payload['weight_unit'] = weight_unit

            items.append(item_payload)
        
        if not items:
            raise ValueError(
                f"Aucun produit avec mapping B2B trouvé pour la commande {order.order_number}"
            )
        
        # Préparer le payload
        user = order.user
        shipping_address = order.shipping_address
        customer_email = user.email if user and getattr(user, 'email', None) else ''
        customer_phone = str(user.phone) if user and getattr(user, 'phone', None) else ''
        customer_full_name = shipping_address.full_name if shipping_address and shipping_address.full_name else ''

        # Récupérer le moyen de paiement avec son libellé
        payment_method = order.payment_method if order.payment_method else ''
        payment_method_label = dict(Order.PAYMENT_CHOICES).get(payment_method, payment_method) if payment_method else ''
        
        payload = {
            'order_number': order.order_number,
            'items': items,
            'total': float(order.total),
            'payment_method': payment_method,
            'payment_method_label': payment_method_label,
            'is_paid': order.is_paid,
            'paid_at': order.paid_at.isoformat() if order.paid_at else None,
            'customer_email': customer_email,
            'customer_phone': customer_phone,
            'customer_full_name': customer_full_name,
            'customer': {
                'email': customer_email,
                'phone': customer_phone,
                'full_name': customer_full_name,
                'address': user.address if user and getattr(user, 'address', None) else '',
                'city': user.city if user and getattr(user, 'city', None) else '',
                'country': user.country if user and getattr(user, 'country', None) else '',
                'postal_code': user.postal_code if user and getattr(user, 'postal_code', None) else '',
            },
            'shipping_address': {
                'full_name': shipping_address.full_name if shipping_address and shipping_address.full_name else '',
                'address_type': shipping_address.address_type if shipping_address else '',
                'quarter': shipping_address.quarter if shipping_address else '',
                'street_address': shipping_address.street_address if shipping_address else '',
                'city': shipping_address.city if shipping_address else '',
                'additional_info': shipping_address.additional_info if shipping_address and shipping_address.additional_info else '',
                'is_default': bool(shipping_address.is_default) if shipping_address else False,
            },
            'created_at': order.created_at.isoformat(),
        }
        
        return payload
    
    def sync_order_to_b2b(self, order: Order) -> Dict[str, Any]:
        """
        Synchronise une commande vers B2B
        
        Args:
            order: Instance de Order
            
        Returns:
            Dict contenant la réponse de l'API B2B avec l'external_sale_id
            
        Raises:
            InventoryAPIError: Si la synchronisation échoue
        """
        # Vérifier si la commande a déjà été synchronisée
        metadata = order.metadata or {}
        if metadata.get('b2b_sync_status') == 'synced' and metadata.get('b2b_sale_id'):
            logger.info(
                f"Commande {order.order_number} déjà synchronisée (b2b_sale_id: {metadata.get('b2b_sale_id')})"
            )
            return {
                'external_sale_id': metadata.get('b2b_sale_id'),
                'status': 'already_synced'
            }
        
        # Vérifier que la commande est payée ou confirmée
        if not order.is_paid and order.status != Order.CONFIRMED:
            logger.warning(
                f"Commande {order.order_number} non payée - synchronisation ignorée"
            )
            raise ValueError(
                f"La commande {order.order_number} doit être payée avant synchronisation"
            )
        
        try:
            # Préparer le payload
            payload = self.prepare_order_payload(order)

            # Log du payload envoyé (anonymisé)
            items_preview = [
                {
                    'product_id': item.get('product_id'),
                    'quantity': item.get('quantity'),
                    'price': item.get('price'),
                    'site_id': item.get('site_id'),
                    'sale_unit_type': item.get('sale_unit_type'),
                }
                for item in payload.get('items', [])
            ]
            logger.info(
                "Payload B2B prêt - order=%s total=%s items=%s",
                payload.get('order_number'),
                payload.get('total'),
                items_preview
            )
            
            # Envoyer vers B2B
            logger.info(f"Synchronisation commande {order.order_number} vers B2B...")
            response = self.api_client.create_sale(payload)
            
            # Extraire l'ID externe de la réponse
            external_sale_id = response.get('id') or response.get('sale_id')
            
            if not external_sale_id:
                logger.error(
                    f"Réponse B2B ne contient pas d'ID de vente: {response}"
                )
                raise InventoryAPIError("Réponse B2B invalide: ID de vente manquant")
            
            # Mettre à jour les métadonnées de la commande
            metadata['b2b_sync_status'] = 'synced'
            metadata['b2b_sale_id'] = external_sale_id
            metadata['b2b_synced_at'] = timezone.now().isoformat()
            order.metadata = metadata
            order.save(update_fields=['metadata'])

            logger.info(
                "Commande %s envoyée avec succès vers B2B (external_sale_id=%s, total=%s)",
                order.order_number,
                external_sale_id,
                order.total
            )
            
            logger.info(
                f"Commande {order.order_number} synchronisée avec succès "
                f"(b2b_sale_id: {external_sale_id})"
            )
            
            return {
                'external_sale_id': external_sale_id,
                'status': 'synced',
                'response': response
            }
            
        except InventoryAPIError as e:
            # Mettre à jour le statut d'erreur
            metadata['b2b_sync_status'] = 'error'
            metadata['b2b_sync_error'] = str(e)
            metadata['b2b_sync_attempted_at'] = timezone.now().isoformat()
            order.metadata = metadata
            order.save(update_fields=['metadata'])
            
            logger.error(
                f"Erreur synchronisation commande {order.order_number}: {str(e)}"
            )
            raise
            
        except Exception as e:
            # Erreur inattendue
            metadata['b2b_sync_status'] = 'error'
            metadata['b2b_sync_error'] = str(e)
            metadata['b2b_sync_attempted_at'] = timezone.now().isoformat()
            order.metadata = metadata
            order.save(update_fields=['metadata'])
            
            logger.error(
                f"Erreur inattendue synchronisation commande {order.order_number}: {str(e)}",
                exc_info=True
            )
            raise InventoryAPIError(f"Erreur synchronisation: {str(e)}")

