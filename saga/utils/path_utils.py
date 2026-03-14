from django.conf import settings
from django.utils import timezone
import os

def get_product_image_path(instance, filename, image_type):
    """
    Génère le chemin de stockage pour une image produit (main ou gallery).
    Utilise le slug du produit, que ce soit une instance Product ou ImageProduct.
    
    Args:
        instance: L'instance du modèle
        filename: Le nom du fichier original
        image_type: Le type d'image ('main' ou 'gallery')
    
    Returns:
        str: Le chemin complet pour l'image
        
    Raises:
        ValueError: Si le type d'image n'est pas valide
    """
    # Valider le type d'image
    valid_types = ['main', 'gallery']
    if image_type not in valid_types:
        raise ValueError(f"Type d'image invalide. Doit être l'un des suivants: {', '.join(valid_types)}")
    
    # Obtenir l'extension du fichier
    ext = os.path.splitext(filename)[1]
    
    # Créer le chemin de date
    date_path = timezone.now().strftime('%Y/%m/%d')
    
    # Récupérer le slug selon le type d'instance
    if hasattr(instance, 'slug') and instance.slug:
        slug = instance.slug
    elif hasattr(instance, 'product') and hasattr(instance.product, 'slug'):
        slug = instance.product.slug
    else:
        slug = 'unknown'
    
    # Déterminer le dossier selon le type d'image
    if image_type == 'main':
        folder = settings.PRODUCT_MAIN_IMAGES_DIR
    elif image_type == 'gallery':
        folder = settings.PRODUCT_GALLERY_IMAGES_DIR
    else:
        raise ValueError('Type d\'image non supporté')
    
    # Construire le chemin complet (sans le préfixe media/products car il est déjà géré par le stockage)
    return f"{folder}/{date_path}/{slug}{ext}" 