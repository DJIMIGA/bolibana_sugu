from django.contrib import messages
from django.db.models import Avg, Count, Q, Min, Max
from django.shortcuts import render, redirect, get_object_or_404
import requests
from .models import Product, Review, Clothing, Size, ShippingMethod, Category, Phone, PhoneVariant, PhoneVariantImage
from .forms import ReviewForm, ProductForm, PhoneForm, PhoneVariantForm, PhoneVariantImageFormSet
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView, TemplateView
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def index(request):
    products = Product.objects.all()

    return render(request, 'base.html', {'products': products})


def detail(request, product_id):
    
    product = get_object_or_404(Product, id=product_id)
    shipping_method = ShippingMethod.objects.all()
    clothing = getattr(product, 'clothing_product', None)
    all_sizes = Size.objects.all()

    if clothing:
        colors = clothing.color.all()
        product_sizes = clothing.size.all()
    else:
        colors = []
        product_sizes = []

    sizes_info = [
        {
            'size': size,
            'available': size in product_sizes
        }
        for size in all_sizes
    ]
    reviews = product.reviews.all()
    average_rating = reviews.aggregate(Avg('note'))['note__avg'] or 0
    average_rating = round(average_rating, 1)
    images = product.image_products.all()
    total_reviews = reviews.count()
    note_reviews = reviews.values('note')
    # Compter le nombre d'avis pour chaque note
    ratings_count = reviews.values('note').annotate(count=Count('id')).order_by('note')

    # Créer un dictionnaire pour stocker le nombre d'avis par note
    ratings_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for rating in ratings_count:
        ratings_distribution[rating['note']] = rating['count']

    # Calculer les pourcentages
    ratings_percentage = {key: (value / total_reviews * 100) if total_reviews > 0 else 0 for key, value in
                          ratings_distribution.items()}

    if request.method == 'POST':
        if request.user.is_authenticated:  # Vérifiez si l'utilisateur est connecté
            note = request.POST.get('note')
            comment = request.POST.get('comment')

            # Créer un nouvel avis
            Review.objects.create(product=product, author=request.user, note=note, comment=comment)

            messages.success(request, 'Votre avis a été soumis avec succès!')
            return redirect('product_detail', product_id=product.id)
        else:
            messages.error(request, 'Vous devez être connecté pour soumettre un avis.')
            return redirect('login')  # Redirigez vers la page de connexion

    context = {
        'product': product,
        'shipping_method': shipping_method,
        'product_sizes': product_sizes,
        'colors': colors,
        'sizes_info': sizes_info,
        'images': images,
        'reviews': reviews,
        'average_rating': average_rating,
        'ratings_percentage': ratings_percentage,
        'note_reviews': note_reviews,
    }
    return render(request, 'detail.html', context)


def review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    average_rating = reviews.aggregate(Avg('note'))['note__avg'] or 0
    average_rating = round(average_rating, 1)
    images = product.image_products.all()
    total_reviews = reviews.count()
    note_reviews = reviews.values('note')
    # Compter le nombre d'avis pour chaque note
    ratings_count = reviews.values('note').annotate(count=Count('id')).order_by('note')

    # Créer un dictionnaire pour stocker le nombre d'avis par note
    ratings_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for rating in ratings_count:
        ratings_distribution[rating['note']] = rating['count']

    # Calculer les pourcentages
    ratings_percentage = {key: (value / total_reviews * 100) if total_reviews > 0 else 0 for key, value in
                          ratings_distribution.items()}

    if request.method == 'POST':
        if request.user.is_authenticated:  # Vérifiez si l'utilisateur est connecté
            note = request.POST.get('note')
            comment = request.POST.get('comment')

            # Créer un nouvel avis
            Review.objects.create(product=product, author=request.user, note=note, comment=comment)

            messages.success(request, 'Votre avis a été soumis avec succès!')
            return redirect('product_detail', product_id=product.id)
        else:
            messages.error(request, 'Vous devez être connecté pour soumettre un avis.')
            return redirect('login')  # Redirigez vers la page de connexion

    context = {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'images': images,
        'ratings_percentage': ratings_percentage,
        'note_reviews': note_reviews,
    }
    return render(request, 'review.html', context)


def quick_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    average_rating = reviews.aggregate(Avg('note'))['note__avg'] or 0
    average_rating = round(average_rating, 1)
    clothing = getattr(product, 'clothing_product', None)
    all_sizes = Size.objects.all()

    if clothing:
        colors = clothing.color.all()
        product_sizes = clothing.size.all()
    else:
        colors = []
        product_sizes = []

    sizes_info = [
        {
            'size': size,
            'available': size in product_sizes
        }
        for size in all_sizes
    ]
    context = {
        'product': product,
        'colors': colors,
        'product_sizes': product_sizes,
        'sizes_info': sizes_info,
        'reviews': reviews,
        'average_rating': average_rating,
    }

    return render(request, 'quick_view.html', context)


def category(request):
    return render(request, 'category.html')


def product_list(request):
    # Récupérer les produits avec leurs variantes et couleurs
    products = Product.objects.select_related(
        'category',
        'supplier'
    ).prefetch_related(
        'phone__variants__color'
    ).all()

    return render(request, 'product_list.html', {'products': products})


def search(request):
    query = request.GET.get('q', '')
    products_count = 0
    categories_count = 0
    products = []
    search_categories = []  # Renamed from categories
    if query:
        products = Product.objects.filter(title__icontains=query)
        search_categories = Category.objects.filter(name__icontains=query)
        products_count = len(products)
        categories_count = len(search_categories)
    return render(request, 'search_results.html', {
        'products': products,
        'search_categories': search_categories,  # Renamed from categories
        'products_count': products_count,
        'categories_count': categories_count,
        'query': query
    })


def cart(request):
    return render(request, 'cart_slide_over.html')


class CategoryTreeView(ListView):
    model = Category
    template_name = 'components/_subcategories_menu.html'
    context_object_name = 'subcategories'

    def get_queryset(self):
        # Récupérer uniquement les catégories racines (sans parent)
        return Category.objects.filter(parent=None).prefetch_related('children')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pas de catégorie parente pour le menu principal
        context['category'] = None
        # Récupérer les catégories principales pour le menu mobile
        context['categories'] = Category.objects.filter(parent=None).prefetch_related('children')
        return context


def category_subcategories(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        subcategories = category.children.all().prefetch_related('children')
        return render(request, 'components/_subcategories_menu.html', {
            'category': category,
            'subcategories': subcategories,
            'categories': Category.objects.filter(parent=None).prefetch_related('children')
        })
    except Category.DoesNotExist:
        return render(request, 'components/_subcategories_menu.html', {
            'category': None,
            'subcategories': [],
            'categories': Category.objects.filter(parent=None).prefetch_related('children')
        })


class CategoryProductsView(ListView):
    model = Product
    template_name = 'product/components/_category_products.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        self.category = get_object_or_404(Category, id=category_id)
        
        # Récupérer tous les produits de la catégorie et ses sous-catégories
        category_ids = self.category.get_all_children_ids()
        queryset = Product.objects.filter(category_id__in=category_ids)

        # Gérer le tri
        sort_by = self.request.GET.get('sort')
        if sort_by:
            if sort_by == 'price_asc':
                queryset = queryset.order_by('price')
            elif sort_by == 'price_desc':
                queryset = queryset.order_by('-price')
            elif sort_by == 'name_asc':
                queryset = queryset.order_by('name')
            elif sort_by == 'name_desc':
                queryset = queryset.order_by('-name')
            elif sort_by == 'newest':
                queryset = queryset.order_by('-created_at')

        return queryset.select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['product/components/_product_grid.html']
        return [self.template_name]


class TermsConditionsView(TemplateView):
    template_name = 'components/_terms_conditions.html'


class CGVView(TemplateView):
    template_name = 'components/_cgv.html'


@login_required
def create_product_with_phone(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        phone_form = PhoneForm(request.POST)
        variant_form = PhoneVariantForm(request.POST)
        image_formset = PhoneVariantImageFormSet(request.POST, request.FILES)
        
        if all([product_form.is_valid(), phone_form.is_valid(), variant_form.is_valid(), image_formset.is_valid()]):
            try:
                # Sauvegarder le produit
                product = product_form.save()
                
                # Créer le téléphone avec le produit associé
                phone = phone_form.save(commit=False)
                phone.product = product
                phone.id = product.id
                phone.save()
                
                # Créer la variante
                variant = variant_form.save(commit=False)
                variant.phone = phone
                variant.save()
                
                # Sauvegarder les images
                image_formset.instance = variant
                instances = image_formset.save(commit=False)
                
                # Traiter chaque instance d'image
                for instance in instances:
                    # Si c'est la première image, la marquer comme primaire
                    if not variant.images.exists():
                        instance.is_primary = True
                    instance.save()
                
                messages.success(request, 'Le produit, le téléphone, sa variante et les images ont été créés avec succès.')
                return redirect('product_detail', product_id=product.id)
            except Exception as e:
                messages.error(request, f'Une erreur est survenue lors de la création : {str(e)}')
                return redirect('create_product_with_phone')
    else:
        product_form = ProductForm()
        phone_form = PhoneForm()
        variant_form = PhoneVariantForm()
        image_formset = PhoneVariantImageFormSet()
    
    context = {
        'product_form': product_form,
        'phone_form': phone_form,
        'variant_form': variant_form,
        'image_formset': image_formset,
    }
    return render(request, 'product/create_product_with_phone.html', context)


class PhoneListView(ListView):
    model = Phone
    template_name = 'product/phone_list.html'
    context_object_name = 'phones'

    def get_queryset(self):
        queryset = super().get_queryset()
        brand_id = self.request.GET.get('brand')
        if brand_id:
            return queryset.filter(product__category_id=brand_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand_id = self.request.GET.get('brand')
        
        # Récupérer la catégorie sélectionnée
        if brand_id:
            try:
                category = Category.objects.get(id=brand_id)
                context['page_title'] = f"Nos {category.name}"
            except Category.DoesNotExist:
                context['page_title'] = "Nos téléphones"
        else:
            context['page_title'] = "Nos téléphones"
            
        # Récupérer toutes les marques pour le filtre
        context['brands'] = Category.objects.filter(parent__name='Téléphones')
        return context


def phone_detail(request, phone_id):
    phone = get_object_or_404(Phone, id=phone_id)
    phone = Phone.objects.select_related(
        'product__category',
        'product__supplier'
    ).prefetch_related(
        'variants__color',
        'variants__images'
    ).get(id=phone_id)
    
    context = {
        'phone': phone,
    }
    return render(request, 'product/phone_detail.html', context)


def get_variant_images(request, variant_id):
    try:
        # Vérifier le cache
        cache_key = f'variant_images_{variant_id}'
        cached_data = cache.get(cache_key)
        
        if cached_data and not request.GET.get('refresh'):
            return cached_data

        # Optimisation des requêtes
        variant = get_object_or_404(
            PhoneVariant.objects.select_related('phone', 'color')
                              .prefetch_related('images'),
            id=variant_id
        )
        
        # Préparer les données des images
        images_data = [{
            'id': image.id,
            'image': {
                'url': image.image.url,
                'alt': f"{variant.phone.model} - {variant.color.name} - {variant.storage}Go"
            },
            'is_primary': image.is_primary
        } for image in variant.images.all()]
        
        # Préparer la réponse
        response_data = {
            'variant': {
                'id': variant.id,
                'price': str(variant.price),
                'color': variant.color.name,
                'storage': variant.storage
            },
            'images': images_data
        }
        
        response = JsonResponse(response_data)
        # Mettre en cache la réponse
        cache.set(cache_key, response, 3600)  # Cache pour 1 heure
        return response

    except PhoneVariant.DoesNotExist:
        return JsonResponse({'error': 'Variante non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Erreur serveur'}, status=500)



