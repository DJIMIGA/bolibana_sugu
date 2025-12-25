from django.db.models import Count, Q, Avg
from product.models import Category, Product, ShippingMethod, Fabric
from django.utils import timezone
from datetime import timedelta

def format_dimension(value):
    """
    Formate une dimension en supprimant les zéros inutiles.
    Ex: 3.00 devient 3, 1.50 devient 1.5
    """
    if value is None:
        return ""
    
    # Convertir en string et remplacer le point par une virgule
    str_value = str(value).replace('.', ',')
    
    # Supprimer les zéros inutiles à la fin
    if ',' in str_value:
        # Supprimer les zéros à la fin après la virgule
        while str_value.endswith('0') and ',' in str_value:
            str_value = str_value[:-1]
        
        # Si on se retrouve avec juste une virgule, la supprimer
        if str_value.endswith(','):
            str_value = str_value[:-1]
    
    return str_value

def global_supplier_context(request):
    """
    Context processor qui fournit les données communes pour toutes les vues liées aux fournisseurs.
    """
    context = {}
    
    # Récupérer les catégories principales avec leurs produits
    main_categories = Category.objects.filter(
        is_main=True,
        parent__isnull=True
    ).exclude(
        slug='tous-les-produits'  # Exclure la catégorie "Tous les produits"
    ).prefetch_related(
        'products',
        'children'
    ).order_by('order', 'name')
    
    context['main_categories'] = main_categories
    
    # Récupérer tous les produits pour les filtres
    base_queryset = Product.objects.all().select_related(
        'phone',
        'phone__color',
        'supplier',
        'category',
        'fabric_product',
        'clothing_product',
        'cultural_product'
    ).prefetch_related(
        'clothing_product__size',
        'clothing_product__color',
        'fabric_product__color',
        'images'
    )
    
    # Log des produits par type
    phone_products = base_queryset.filter(phone__isnull=False)
    clothing_products = base_queryset.filter(clothing_product__isnull=False)
    fabric_products = base_queryset.filter(fabric_product__isnull=False)
    cultural_products = base_queryset.filter(cultural_product__isnull=False)
    
    # Appliquer les filtres de prix
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    
    if price_min:
        base_queryset = base_queryset.filter(price__gte=price_min)
    if price_max:
        base_queryset = base_queryset.filter(price__lte=price_max)
    
    # Trier les résultats : Disponible d'abord, puis nouveautés
    base_queryset = base_queryset.order_by('-is_available', '-created_at')
    
    # Ajouter les produits au contexte
    context['products'] = base_queryset
    
    # Produits téléphones
    context['phone_products'] = phone_products.order_by('-is_available', '-created_at')[:8]
    
    # Récupérer les marques de téléphones
    brands_list = list(phone_products.values_list('phone__brand', flat=True))
    brands_clean = sorted(set(filter(None, brands_list)))
    context['phone_categories'] = [{'brand': b} for b in brands_clean]
    
    # Produits vêtements
    context['clothing_products'] = clothing_products.order_by('-is_available', '-created_at')[:8]
    
    # Produits tissus avec toutes les informations
    fabric_products = fabric_products.select_related(
        'fabric_product',
        'fabric_product__color'
    ).order_by('-is_available', '-created_at')[:8]
    
    # Enrichir les produits tissus avec les informations spécifiques
    enriched_fabric_products = []
    for product in fabric_products:
        fabric = product.fabric_product
        if fabric:
            product_data = {
                'product': product,
                'fabric_type': fabric.get_fabric_type_display(),
                'quality': fabric.quality,
                'unique_id': fabric.unique_id,
                'dimensions': f"{format_dimension(fabric.length)}m x {format_dimension(fabric.width)}m" if fabric.length and fabric.width else None,
                'color': fabric.color.name if fabric.color else None,
                'pattern': fabric.pattern,
                'origin': fabric.origin,
                'care_instructions': fabric.care_instructions,
                'price_per_meter': fabric.get_price_per_meter()
            }
            enriched_fabric_products.append(product_data)
    
    context['fabric_products'] = enriched_fabric_products
    
    # Produits culturels
    context['cultural_products'] = cultural_products.order_by('-is_available', '-created_at')[:8]
    
    # Méthodes de livraison
    context['shipping_methods'] = ShippingMethod.objects.all().distinct().order_by('price')
    
    # Statistiques globales
    context['total_products'] = base_queryset.count()
    context['total_categories'] = Category.objects.filter(is_main=True).count()
    
    # Produits en vedette (les plus vendus ou les mieux notés)
    context['featured_products'] = base_queryset.annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-is_available', '-avg_rating')[:4]
    
    # Nouveaux produits (derniers 7 jours)
    seven_days_ago = timezone.now() - timedelta(days=7)
    context['new_products'] = base_queryset.filter(
        created_at__gte=seven_days_ago
    ).order_by('-is_available', '-created_at')[:4]
    
    # Produits en promotion
    context['promo_products'] = base_queryset.filter(
        discount_price__isnull=False
    ).order_by('-is_available', '-discount_price')[:4]
    
    # Filtres de prix sélectionnés
    context['selected_price_min'] = request.GET.get('price_min', '')
    context['selected_price_max'] = request.GET.get('price_max', '')
    
    # Filtres spécifiques aux marques
    brand = request.GET.get('brand')
    if brand:
        active_products = base_queryset.filter(
            phone__brand__iexact=brand
        )
        
        # Récupérer les modèles disponibles
        models_list = list(active_products.values_list('phone__model', flat=True))
        context['models'] = [{'phone__model': m} for m in sorted(set(filter(None, models_list)))]
        
        # Récupérer les stockages disponibles
        storages_list = list(active_products.values_list('phone__storage', flat=True))
        context['storages'] = [{'phone__storage': s} for s in sorted(set(filter(None, storages_list)))]
        
        # Récupérer les RAM disponibles
        rams_list = list(active_products.values_list('phone__ram', flat=True))
        context['rams'] = [{'phone__ram': r} for r in sorted(set(filter(None, rams_list)))]
        
        # Filtres sélectionnés
        context['selected_brand'] = brand
        context['selected_model'] = request.GET.get('model', '')
        context['selected_storage'] = request.GET.get('storage', '')
        context['selected_ram'] = request.GET.get('ram', '')
    else:
        # Initialiser les listes vides si pas de marque sélectionnée
        context['models'] = []
        context['storages'] = []
        context['rams'] = []
        context['selected_brand'] = ''
        context['selected_model'] = ''
        context['selected_storage'] = ''
        context['selected_ram'] = ''
    
    # Récupérer les catégories disponibles pour les filtres
    categories_list = Category.objects.all().values_list('name', flat=True).distinct()
    
    return context

def user_context(request):
    """
    Ajoute l'utilisateur au contexte de tous les templates.
    """
    return {
        'user': request.user,
        'is_authenticated': request.user.is_authenticated,
    } 