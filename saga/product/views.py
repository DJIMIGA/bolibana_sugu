from django.contrib import messages
from django.db.models import Avg, Count, Q, Min, Max
from django.shortcuts import render, redirect, get_object_or_404
import requests
from .models import Product, Review, Clothing, Size, ShippingMethod, Category, Phone
from .forms import ReviewForm, ProductForm, PhoneForm
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView, TemplateView, DetailView
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
    reviews = product.reviews.all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] if reviews else None
    
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product:product_detail', product_id=product.id)
    else:
        review_form = ReviewForm()
    
    context = {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'review_form': review_form,
        'images': product.images.all().order_by('ordre'),
    }
    
    # Ajouter les attributs spécifiques au téléphone si c'est un téléphone
    if hasattr(product, 'phone'):
        context['phone'] = product.phone
        # Récupérer les téléphones similaires comme variantes
        similar_phones = Phone.objects.filter(
            Q(brand=product.phone.brand) | 
            Q(model=product.phone.model)
        ).exclude(id=product.phone.id)
        context['variants'] = similar_phones
    
    return render(request, 'product/detail.html', context)


def review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    average_rating = round(average_rating, 1)
    images = product.images.all()
    total_reviews = reviews.count()
    note_reviews = reviews.values('rating')
    # Compter le nombre d'avis pour chaque note
    ratings_count = reviews.values('rating').annotate(count=Count('id')).order_by('rating')

    # Créer un dictionnaire pour stocker le nombre d'avis par note
    ratings_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for rating in ratings_count:
        ratings_distribution[rating['rating']] = rating['count']

    # Calculer les pourcentages
    ratings_percentage = {key: (value / total_reviews * 100) if total_reviews > 0 else 0 for key, value in
                          ratings_distribution.items()}

    if request.method == 'POST':
        if request.user.is_authenticated:  # Vérifiez si l'utilisateur est connecté
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')

            # Créer un nouvel avis
            Review.objects.create(product=product, user=request.user, rating=rating, comment=comment)

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
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
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
    # Récupérer les produits avec leurs relations
    products = Product.objects.select_related(
        'category',
        'supplier',
        'phone',
        'phone__color'
    ).prefetch_related(
        'images'
    ).filter(is_salam=True)  # Ne montrer que les produits salam

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
        
        if all([product_form.is_valid(), phone_form.is_valid()]):
            try:
                # Sauvegarder le produit
                product = product_form.save()
                
                # Créer le téléphone avec le produit associé
                phone = phone_form.save(commit=False)
                phone.product = product
                phone.id = product.id
                phone.save()
                
                messages.success(request, 'Le produit, le téléphone et les images ont été créés avec succès.')
                return redirect('product_detail', product_id=product.id)
            except Exception as e:
                messages.error(request, f'Une erreur est survenue lors de la création : {str(e)}')
                return redirect('create_product_with_phone')
    else:
        product_form = ProductForm()
        phone_form = PhoneForm()
    
    context = {
        'product_form': product_form,
        'phone_form': phone_form,
    }
    return render(request, 'product/create_product_with_phone.html', context)


class PhoneListView(ListView):
    model = Phone
    template_name = 'product/phone_list.html'
    context_object_name = 'phones'
    paginate_by = 12

    def get_queryset(self):
        queryset = Phone.objects.select_related('product', 'color').prefetch_related('images')
        
        # Filtres
        brand = self.request.GET.get('brand')
        storage = self.request.GET.get('storage')
        ram = self.request.GET.get('ram')
        color = self.request.GET.get('color')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        if brand:
            queryset = queryset.filter(brand__iexact=brand)
        if storage:
            queryset = queryset.filter(storage=storage)
        if ram:
            queryset = queryset.filter(ram=ram)
        if color:
            queryset = queryset.filter(color__name__iexact=color)
        if min_price:
            queryset = queryset.filter(product__price__gte=min_price)
        if max_price:
            queryset = queryset.filter(product__price__lte=max_price)
            
        return queryset.order_by('brand', 'model')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        phones = self.get_queryset()
        
        # Données pour les filtres
        context['brands'] = phones.values_list('brand', flat=True).distinct()
        context['storages'] = phones.values_list('storage', flat=True).distinct()
        context['rams'] = phones.values_list('ram', flat=True).distinct()
        context['colors'] = phones.values_list('color__name', flat=True).distinct()
        
        # Filtres sélectionnés
        context['selected_brand'] = self.request.GET.get('brand', '')
        context['selected_storage'] = self.request.GET.get('storage', '')
        context['selected_ram'] = self.request.GET.get('ram', '')
        context['selected_color'] = self.request.GET.get('color', '')
        context['selected_min_price'] = self.request.GET.get('min_price', '')
        context['selected_max_price'] = self.request.GET.get('max_price', '')
        
        return context

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['product/components/_phone_grid.html']
        return ['product/phone_list.html']

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'product/components/_phone_grid.html', context)
        return super().render_to_response(context, **response_kwargs)


class PhoneDetailView(DetailView):
    model = Phone
    template_name = 'product/phone_detail.html'
    context_object_name = 'phone'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        phone = self.get_object()
        
        # Images via le produit associé
        context['images'] = phone.product.images.all().order_by('ordre')
        
        # Téléphones similaires
        similar_phones = Phone.objects.filter(
            Q(brand=phone.brand) | 
            Q(storage=phone.storage) |
            Q(ram=phone.ram)
        ).exclude(id=phone.id)[:4]
        context['similar_phones'] = similar_phones
        
        # Avis
        reviews = phone.product.reviews.all()
        context['reviews'] = reviews
        context['review_form'] = ReviewForm()
        
        if reviews.exists():
            context['average_rating'] = reviews.aggregate(Avg('rating'))['rating__avg']
            context['review_count'] = reviews.count()
        
        return context


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Votre avis a été ajouté avec succès.')
            return redirect('product_detail', product_id=product.id)
    
    return redirect('product_detail', product_id=product.id)


def get_filtered_phones(request):
    brand = request.GET.get('brand')
    storage = request.GET.get('storage')
    ram = request.GET.get('ram')
    color = request.GET.get('color')
    
    phones = Phone.objects.all()
    
    if brand:
        phones = phones.filter(brand=brand)
    if storage:
        phones = phones.filter(storage=storage)
    if ram:
        phones = phones.filter(ram=ram)
    if color:
        phones = phones.filter(color__name=color)
        
    data = []
    for phone in phones:
        phone_data = {
            'id': phone.id,
            'name': str(phone),
            'price': str(phone.product.price),
            'image': phone.images.filter(is_primary=True).first().image.url if phone.images.filter(is_primary=True).exists() else None
        }
        data.append(phone_data)
    
    return JsonResponse({'phones': data})



