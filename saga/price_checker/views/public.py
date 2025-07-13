from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import Http404
from django.db.models import Q, Prefetch
from product.models import Phone
from ..models import PriceEntry

def check_price(request):
    # Si c'est une requête HTMX
    if request.headers.get('HX-Request'):
        product_name = request.GET.get('product_name', '').strip()
        page = request.GET.get('page', 1)
        
        if not product_name:
            return render(request, 'price_checker/partials/price_results.html', {
                'results': [],
                'empty_search': True
            })
        
        try:
            # Recherche des variantes similaires
            search_terms = product_name.split()
            query = Q()
            
            for term in search_terms:
                clean_term = term.lower().replace('gb', '').replace('go', '').replace('g', '').strip()
                
                try:
                    numeric_value = int(clean_term)
                    term_query = (
                        Q(brand__icontains=term) |
                        Q(model__icontains=term) |
                        Q(operating_system__icontains=term) |
                        Q(processor__icontains=term) |
                        Q(color__name__icontains=term) |
                        Q(ram=numeric_value) |
                        Q(storage=numeric_value)
                    )
                except ValueError:
                    term_query = (
                        Q(brand__icontains=term) |
                        Q(model__icontains=term) |
                        Q(operating_system__icontains=term) |
                        Q(processor__icontains=term) |
                        Q(color__name__icontains=term)
                    )
                
                query &= term_query
            
            # Récupérer les variantes
            similar_variants = Phone.objects.filter(query).select_related(
                'color'
            ).prefetch_related(
                Prefetch('price_entries', 
                        queryset=PriceEntry.objects.filter(
                            is_active=True
                        ).select_related('city')
                        .order_by('-created_at'))
            ).order_by(
                'brand',
                'model',
                'ram',
                'storage'
            )
            
            # Pagination
            paginator = Paginator(similar_variants, 5)
            try:
                variants_page = paginator.page(page)
            except Http404:
                variants_page = paginator.page(1)
            
            results = []
            for variant in variants_page:
                prices_by_city = {}
                for price_entry in variant.price_entries.all():
                    if price_entry.city not in prices_by_city:
                        # Utiliser la nouvelle méthode get_average_price
                        avg_price_info = PriceEntry.get_average_price(
                            product=variant.product,
                            variant=variant,
                            city=price_entry.city
                        )
                        
                        prices_by_city[price_entry.city] = {
                            'price': avg_price_info['average_price'] if avg_price_info['count'] > 1 else price_entry.price,
                            'price_change': price_entry.price_change,
                            'price_change_percentage': price_entry.price_change_percentage,
                            'updated_at': price_entry.created_at,
                            'is_average': avg_price_info['count'] > 1,
                            'count': avg_price_info['count'],
                            'supplier_name': price_entry.supplier_name,
                            'supplier_phone': price_entry.supplier_phone,
                            'supplier_address': price_entry.supplier_address,
                            'proof_image': price_entry.proof_image.url if price_entry.proof_image else None,
                            'source': 'Utilisateur' if price_entry.user else 'Admin'
                        }
                
                results.append({
                    'product': variant,
                    'ram': variant.ram,
                    'storage': variant.storage,
                    'color': variant.color,
                    'prices_by_city': prices_by_city
                })
            
            return render(request, 'price_checker/partials/price_results.html', {
                'results': results,
                'page_obj': variants_page,
                'paginator': paginator,
                'is_paginated': paginator.num_pages > 1
            })
                
        except Exception as e:
            return render(request, 'price_checker/partials/price_results.html', {
                'results': [],
                'empty_search': False
            })
    
    # Pour les requêtes normales
    return render(request, 'price_checker/check_price.html') 