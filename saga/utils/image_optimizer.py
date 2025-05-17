import os
import tinify
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image
import logging
from rembg import remove as remove_background
import numpy as np
import boto3
from botocore.exceptions import ClientError
import time
from django.core.files.storage import default_storage
from django.core.cache import cache
from botocore.config import Config
from django.utils import timezone
from .path_utils import get_product_image_path

logger = logging.getLogger(__name__)

class ImageOptimizer:
    def __init__(self):
        # Configuration S3 avec retry
        self.s3_config = Config(
            retries=dict(
                max_attempts=3,
                mode='adaptive'
            ),
            connect_timeout=5,
            read_timeout=10
        )
        
        # Initialisation du client S3 avec la configuration
        self.s3_client = boto3.client(
            's3',
            config=self.s3_config,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        self.region = settings.AWS_S3_REGION_NAME
        self.tinify_key = settings.TINIFY_API_KEY
        
        if self.tinify_key:
            tinify.key = self.tinify_key
            
        # Récupération des paramètres depuis settings.py
        self.max_size = settings.MAX_IMAGE_SIZE
        self.max_dimensions = settings.MAX_IMAGE_DIMENSIONS
        self.quality = settings.IMAGE_QUALITY
        self.image_formats = settings.IMAGE_FORMATS

    def get_cache_key(self, image_path, format_name):
        """Génère une clé de cache unique pour une image."""
        return f"image_optimizer_{image_path}_{format_name}"

    def get_cached_url(self, image_path, format_name):
        """Récupère l'URL de l'image depuis le cache."""
        cache_key = self.get_cache_key(image_path, format_name)
        return cache.get(cache_key)

    def set_cached_url(self, image_path, format_name, url):
        """Stocke l'URL de l'image dans le cache."""
        cache_key = self.get_cache_key(image_path, format_name)
        cache.set(cache_key, url, timeout=3600)  # Cache pour 1 heure

    def remove_background(self, image):
        """Supprime le fond de l'image."""
        start_time = time.time()
        try:
            logger.info("Début de la suppression du fond")
            # Convertir l'image en tableau numpy
            img_array = np.array(image)
            
            # Supprimer le fond
            output = remove_background(img_array)
            
            # Convertir en image PIL
            output_image = Image.fromarray(output)
            
            # Sauvegarder en PNG avec compression maximale
            output = BytesIO()
            output_image.save(output, format='PNG', optimize=True, compress_level=9)
            output.seek(0)
            
            logger.info(f"Suppression du fond terminée en {time.time() - start_time:.2f} secondes")
            return output
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du fond: {str(e)}")
            return None

    def resize_image(self, image, target_size):
        """Redimensionne l'image aux dimensions cibles."""
        start_time = time.time()
        try:
            logger.info(f"Début du redimensionnement vers {target_size}")
            # Calculer les nouvelles dimensions en conservant le ratio
            width, height = image.size
            target_width, target_height = target_size
            
            ratio = min(target_width/width, target_height/height)
            new_size = (int(width * ratio), int(height * ratio))
            
            # Redimensionner l'image
            resized = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Sauvegarder avec compression optimale
            output = BytesIO()
            resized.save(output, format='PNG', optimize=True, compress_level=9)
            output.seek(0)
            
            logger.info(f"Redimensionnement terminé en {time.time() - start_time:.2f} secondes")
            return output
        except Exception as e:
            logger.error(f"Erreur lors du redimensionnement: {str(e)}")
            return None

    def upload_to_s3(self, image_data, key, content_type='image/jpeg'):
        """Upload une image vers S3 avec gestion des erreurs et retry."""
        max_retries = 3
        retry_delay = 1  # secondes
        
        for attempt in range(max_retries):
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=image_data,
                    ContentType=content_type,
                    CacheControl='max-age=86400'  # Cache pour 24h
                )
                return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NoSuchBucket':
                    logger.error(f"Le bucket {self.bucket_name} n'existe pas")
                    raise
                elif error_code == 'AccessDenied':
                    logger.error(f"Accès refusé au bucket {self.bucket_name}")
                    raise
                else:
                    if attempt < max_retries - 1:
                        logger.warning(f"Tentative {attempt + 1} échouée, nouvelle tentative dans {retry_delay} secondes")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Augmentation exponentielle du délai
                    else:
                        logger.error(f"Échec de l'upload après {max_retries} tentatives: {str(e)}")
                        raise

    def check_s3_object_exists(self, key):
        """Vérifie si un objet existe dans S3."""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise

    def optimize_image(self, image, model_instance=None):
        """Optimise l'image avec gestion des erreurs améliorée."""
        start_time = time.time()
        try:
            logger.info("Début de l'optimisation de l'image")
            
            if not self.validate_image(image):
                return None, {}

            # Vérifier le cache si un modèle est fourni
            if model_instance and hasattr(model_instance, 'image'):
                image_path = model_instance.image.name
                cached_urls = {}
                for format_name in self.image_formats.keys():
                    cached_url = self.get_cached_url(image_path, format_name)
                    if cached_url and self.check_s3_object_exists(image_path):
                        cached_urls[format_name] = cached_url
                if cached_urls:
                    return None, cached_urls

            # Ouvrir l'image avec PIL
            if isinstance(image, InMemoryUploadedFile):
                img = Image.open(image)
            else:
                img = Image.open(image)

            # Sauvegarder la taille initiale
            initial_size = img.size
            logger.info(f"Taille initiale de l'image: {initial_size[0]}x{initial_size[1]}")

            # Supprimer le fond si nécessaire
            if hasattr(image, 'name') and image.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                output = self.remove_background(img)
                if output:
                    img = Image.open(output)
                    logger.info(f"Taille après suppression du fond: {img.size[0]}x{img.size[1]}")

            # Optimiser avec Tinify
            try:
                # Sauvegarder l'image dans un buffer temporaire
                temp_buffer = BytesIO()
                img.save(temp_buffer, format='PNG')
                temp_buffer.seek(0)
                
                source = tinify.from_buffer(temp_buffer.getvalue())
                optimized = source.to_buffer()
                
                # Sauvegarder l'image optimisée
                output = BytesIO(optimized)
                output.seek(0)
                
                # Créer les versions redimensionnées
                urls = {}
                for format_name, format_config in self.image_formats.items():
                    if format_config['required']:
                        resized = self.resize_image(Image.open(output), 
                                                  (format_config['width'], format_config['height']))
                        if resized:
                            # Utiliser get_product_image_path pour générer le chemin
                            if model_instance:
                                file_name = get_product_image_path(model_instance, image.name, format_name)
                            else:
                                # Fallback si pas de modèle
                                file_name = f"{os.path.splitext(image.name)[0]}_{format_name}.{format_config['format'].lower()}"
                            
                            # Upload vers S3 avec le bon content-type
                            url = self.upload_to_s3(
                                resized,
                                file_name,
                                content_type=f'image/{format_config["format"].lower()}'
                            )
                            if url:
                                urls[format_name] = url
                
                # Mettre en cache les URLs générées
                if model_instance and hasattr(model_instance, 'image'):
                    for format_name, url in urls.items():
                        self.set_cached_url(model_instance.image.name, format_name, url)

                logger.info(f"Optimisation terminée en {time.time() - start_time:.2f} secondes")
                return output, urls
            except Exception as e:
                logger.error(f"Erreur Tinify: {str(e)}")
                # Fallback vers PIL si Tinify échoue
                output = BytesIO()
                img.save(output, format='PNG', optimize=True, compress_level=9)
                output.seek(0)
                return output, {}

        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation: {str(e)}")
            return None, {}

    def validate_image(self, image):
        """Vérifie si l'image est valide."""
        try:
            # Vérifier le type de fichier
            if not isinstance(image, (InMemoryUploadedFile, BytesIO)):
                logger.error("Type de fichier non supporté")
                return False

            # Vérifier la taille
            if isinstance(image, InMemoryUploadedFile):
                if image.size > self.max_size:
                    logger.error(f"Image trop grande: {image.size} bytes")
                    return False
            else:
                if len(image.getvalue()) > self.max_size:
                    logger.error(f"Image trop grande: {len(image.getvalue())} bytes")
                    return False

            # Vérifier les dimensions
            img = Image.open(image)
            width, height = img.size
            if width > self.max_dimensions[0] or height > self.max_dimensions[1]:
                logger.error(f"Dimensions trop grandes: {width}x{height}")
                return False

            return True
        except Exception as e:
            logger.error(f"Erreur lors de la validation: {str(e)}")
            return False

    def optimize_product_image(self, image, product_instance):
        """Optimise spécifiquement une image de produit."""
        try:
            if not self.validate_image(image):
                return None, {}

            # Vérifier le cache
            image_path = product_instance.image.name
            cached_urls = {}
            for format_name in self.image_formats.keys():
                cached_url = self.get_cached_url(image_path, format_name)
                if cached_url and self.check_s3_object_exists(image_path):
                    cached_urls[format_name] = cached_url
            if cached_urls:
                return None, cached_urls

            # Ouvrir l'image avec PIL
            if isinstance(image, InMemoryUploadedFile):
                img = Image.open(image)
            else:
                img = Image.open(image)

            # Supprimer le fond si c'est une image de produit
            if hasattr(image, 'name') and image.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                output = self.remove_background(img)
                if output:
                    img = Image.open(output)

            # Créer les versions optimisées
            urls = {}
            for format_name, format_config in self.image_formats.items():
                if format_config['required']:
                    # Redimensionner l'image
                    resized = self.resize_image(
                        img, 
                        (format_config['width'], format_config['height'])
                    )
                    
                    if resized:
                        # Générer le chemin avec la fonction utilitaire
                        file_name = get_product_image_path(product_instance, image.name, format_name)
                        
                        # Optimiser avec Tinify si disponible
                        try:
                            if self.tinify_key:
                                temp_buffer = BytesIO()
                                Image.open(resized).save(temp_buffer, format=format_config['format'])
                                temp_buffer.seek(0)
                                
                                source = tinify.from_buffer(temp_buffer.getvalue())
                                optimized = source.to_buffer()
                                
                                # Upload vers S3
                                url = self.upload_to_s3(
                                    optimized,
                                    file_name,
                                    content_type=f'image/{format_config["format"].lower()}'
                                )
                            else:
                                # Fallback vers PIL si Tinify n'est pas disponible
                                url = self.upload_to_s3(
                                    resized,
                                    file_name,
                                    content_type=f'image/{format_config["format"].lower()}'
                                )
                            
                            if url:
                                urls[format_name] = url
                                # Mettre en cache
                                self.set_cached_url(image_path, format_name, url)
                                
                        except Exception as e:
                            logger.error(f"Erreur lors de l'optimisation {format_name}: {str(e)}")
                            continue

            return None, urls

        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation de l'image produit: {str(e)}")
            return None, {} 