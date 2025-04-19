from django.contrib import messages
from django.db.models import Avg, Count
from django.shortcuts import render, redirect, get_object_or_404
import requests
from .models import Product, Review, Clothing, Size, ShippingMethod, Category
from .forms import ReviewForm
from django.http import HttpResponse


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
    # Récupérer les produits depuis la base de données
    products = Product.objects.all()

    # Passer les données au contexte pour les afficher dans le modèle
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
