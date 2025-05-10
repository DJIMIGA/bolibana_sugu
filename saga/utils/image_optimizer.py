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

logger = logging.getLogger(__name__)

class ImageOptimizer:
    def __init__(self):
        # Configuration de Tinify avec la clé API
        tinify.key = settings.TINIFY_API_KEY
        self.max_size = 5 * 1024 * 1024  # 5MB
        self.max_dimensions = (4000, 4000)  # max width, height
        self.quality = 80  # qualité de compression (0-100)
        
        # Configuration S3
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Formats d'image prédéfinis
        self.image_formats = {
            'original': {
                'width': 630, 
                'height': 732,
                'usage': 'product_detail',
                'required': True,
                'description': 'Version originale optimisée pour la page détaillée du produit'
            },
            'thumbnail': {
                'width': 200,
                'height': 232,
                'usage': 'product_list',
                'required': True,
                'description': 'Miniature pour les listes de produits et aperçus'
            },
            'medium': {
                'width': 400,
                'height': 464,
                'usage': 'product_grid',
                'required': True,
                'description': 'Format moyen pour la grille de produits'
            },
            'large': {
                'width': 800,
                'height': 928,
                'usage': 'product_zoom',
                'required': True,
                'description': 'Format grand pour le zoom sur les produits'
            }
        }

    def remove_background(self, image):
        """Supprime le fond de l'image."""
        try:
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
            
            return output
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du fond: {str(e)}")
            return None

    def resize_image(self, image, target_size):
        """Redimensionne l'image aux dimensions cibles."""
        try:
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
            
            return output
        except Exception as e:
            logger.error(f"Erreur lors du redimensionnement: {str(e)}")
            return None

    def optimize_image(self, image):
        """Optimise l'image en utilisant Tinify."""
        try:
            # Vérifier si l'image est valide
            if not self.validate_image(image):
                return None

            # Sauvegarder la taille initiale
            initial_size = image.size
            logger.info(f"Taille initiale de l'image: {initial_size[0]}x{initial_size[1]}")

            # Supprimer le fond si nécessaire
            if hasattr(image, 'name') and image.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                output = self.remove_background(image)
                if output:
                    image = Image.open(output)
                    logger.info(f"Taille après suppression du fond: {image.size[0]}x{image.size[1]}")

            # Optimiser avec Tinify
            try:
                source = tinify.from_file(image)
                optimized = source.to_buffer()
                
                # Sauvegarder l'image optimisée
                output = BytesIO(optimized)
                output.seek(0)
                
                # Créer les versions redimensionnées
                for format_name, format_config in self.image_formats.items():
                    if format_config['required']:
                        resized = self.resize_image(Image.open(output), 
                                                  (format_config['width'], format_config['height']))
                        if resized:
                            # Sauvegarder dans S3
                            file_name = f"{os.path.splitext(image.name)[0]}_{format_name}.png"
                            self.s3_client.upload_fileobj(
                                resized,
                                settings.AWS_STORAGE_BUCKET_NAME,
                                f"products/{format_name}/{file_name}",
                                ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/png'}
                            )
                
                return output
            except Exception as e:
                logger.error(f"Erreur Tinify: {str(e)}")
                # Fallback vers PIL si Tinify échoue
                output = BytesIO()
                image.save(output, format='PNG', optimize=True, compress_level=9)
                output.seek(0)
                return output

        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation: {str(e)}")
            return None

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