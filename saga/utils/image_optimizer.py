import os
import tinify
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image

class ImageOptimizer:
    def __init__(self):
        # Configuration de Tinify avec la clé API
        tinify.key = settings.TINIFY_API_KEY
        
    def optimize_image(self, image_file):
        """
        Optimise une image avec Tinify
        Args:
            image_file: Fichier image à optimiser
        Returns:
            BytesIO: Image optimisée en mémoire
        """
        try:
            # Si c'est un InMemoryUploadedFile
            if isinstance(image_file, InMemoryUploadedFile):
                # Lire l'image
                image_data = image_file.read()
                
                # Optimiser avec Tinify
                optimized_image = tinify.from_buffer(image_data).to_buffer()
                
                # Créer un nouveau fichier en mémoire
                output = BytesIO(optimized_image)
                
                # Créer un nouveau InMemoryUploadedFile
                return InMemoryUploadedFile(
                    output,
                    'ImageField',
                    image_file.name,
                    image_file.content_type,
                    len(optimized_image),
                    None
                )
            
            # Si c'est un fichier local
            elif isinstance(image_file, str) and os.path.exists(image_file):
                # Optimiser avec Tinify
                optimized_image = tinify.from_file(image_file).to_buffer()
                
                # Créer un nouveau fichier en mémoire
                output = BytesIO(optimized_image)
                
                # Créer un nouveau InMemoryUploadedFile
                return InMemoryUploadedFile(
                    output,
                    'ImageField',
                    os.path.basename(image_file),
                    'image/jpeg',  # ou déterminer le type MIME correct
                    len(optimized_image),
                    None
                )
            
            return image_file
            
        except Exception as e:
            print(f"Erreur lors de l'optimisation de l'image: {str(e)}")
            return image_file

    def validate_image(self, image_file):
        """
        Valide une image avant l'optimisation
        Args:
            image_file: Fichier image à valider
        Returns:
            bool: True si l'image est valide
        """
        try:
            # Vérifier la taille maximale (par exemple 5MB)
            if image_file.size > 5 * 1024 * 1024:
                return False
                
            # Vérifier le type de fichier
            if not image_file.content_type.startswith('image/'):
                return False
                
            # Vérifier les dimensions
            img = Image.open(image_file)
            width, height = img.size
            if width > 4000 or height > 4000:
                return False
                
            return True
            
        except Exception as e:
            print(f"Erreur lors de la validation de l'image: {str(e)}")
            return False 