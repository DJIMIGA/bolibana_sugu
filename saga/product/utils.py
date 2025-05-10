from django.utils.text import slugify
import random
import string

def generate_unique_slug(title, model_class):
    """
    Génère un slug unique pour un modèle donné.
    """
    slug = slugify(title)
    unique_slug = slug
    num = 1
    
    while model_class.objects.filter(slug=unique_slug).exists():
        # Ajouter un suffixe aléatoire de 4 caractères
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        unique_slug = f"{slug}-{suffix}"
        num += 1
        
    return unique_slug 