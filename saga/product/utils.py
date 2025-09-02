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

def extract_phone_series(model_name):
    """
    Extrait la série d'un modèle de téléphone.
    Exemples:
    - "POVA 7 Pro 5G" -> "POVA"
    - "CAMON 30 Premier 5G" -> "CAMON"
    - "SPARK 10 Pro" -> "SPARK"
    - "POP 8" -> "POP"
    """
    if not model_name:
        return None
    
    # Liste des séries connues
    known_series = ['POVA', 'CAMON', 'SPARK', 'POP', 'GALAXY', 'IPHONE', 'REDMI', 'POCO']
    
    # Essayer de trouver une série connue au début du nom
    for series in known_series:
        if model_name.upper().startswith(series.upper()):
            return series
    
    # Si aucune série connue n'est trouvée, prendre le premier mot
    words = model_name.strip().split()
    if words:
        return words[0].upper()
    
    return None

def normalize_phone_series(series_name):
    """
    Normalise le nom d'une série de téléphone.
    """
    if not series_name:
        return None
    
    # Normalisations spécifiques
    normalizations = {
        'GALAXY': 'Samsung Galaxy',
        'IPHONE': 'iPhone',
        'REDMI': 'Redmi',
        'POCO': 'POCO',
        'POVA': 'POVA',
        'CAMON': 'CAMON',
        'SPARK': 'SPARK',
        'POP': 'POP'
    }
    
    normalized = series_name.upper()
    return normalizations.get(normalized, series_name.title()) 