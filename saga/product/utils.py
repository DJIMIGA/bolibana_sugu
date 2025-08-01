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

def normalize_phone_brand(brand_name):
    """
    Normalise le nom de la marque pour éviter les doublons.
    Utilise la même logique que Phone.normalize_brand().
    """
    if not brand_name:
        return 'Inconnu'
    
    # Nettoyer et normaliser
    brand = brand_name.strip()
    
    # Règles de normalisation spécifiques
    brand_mappings = {
        'tecno': 'TECNO',
        'Tecno': 'TECNO',
        'TECNO': 'TECNO',
        'samsung': 'Samsung',
        'SAMSUNG': 'Samsung',
        'Samsung': 'Samsung',
        'apple': 'Apple',
        'APPLE': 'Apple',
        'Apple': 'Apple',
        'huawei': 'Huawei',
        'HUAWEI': 'Huawei',
        'Huawei': 'Huawei',
        'xiaomi': 'Xiaomi',
        'XIAOMI': 'Xiaomi',
        'Xiaomi': 'Xiaomi',
        'oppo': 'OPPO',
        'OPPO': 'OPPO',
        'Oppo': 'OPPO',
        'vivo': 'Vivo',
        'VIVO': 'Vivo',
        'Vivo': 'Vivo',
        'realme': 'Realme',
        'REALME': 'Realme',
        'Realme': 'Realme',
        'oneplus': 'OnePlus',
        'ONEPLUS': 'OnePlus',
        'OnePlus': 'OnePlus',
        'nokia': 'Nokia',
        'NOKIA': 'Nokia',
        'Nokia': 'Nokia',
        'motorola': 'Motorola',
        'MOTOROLA': 'Motorola',
        'Motorola': 'Motorola',
        'lg': 'LG',
        'LG': 'LG',
        'sony': 'Sony',
        'SONY': 'Sony',
        'Sony': 'Sony',
        'google': 'Google',
        'GOOGLE': 'Google',
        'Google': 'Google',
    }
    
    # Vérifier d'abord si la marque exacte est dans le mapping
    if brand in brand_mappings:
        return brand_mappings[brand]
    
    # Sinon, chercher par la version en minuscules
    normalized = brand_mappings.get(brand.lower(), brand)
    
    # Si pas dans le mapping, appliquer une normalisation générique
    if normalized == brand:
        # Première lettre en majuscule, reste en minuscules
        normalized = brand.capitalize()
    
    return normalized 