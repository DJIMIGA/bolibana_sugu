from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, DeleteView, TemplateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Q, Prefetch, Count, Avg, Max, Min
from django.core.paginator import Paginator
from django.http import Http404
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from .models import (
    PriceEntry, PriceSubmission, City, Product,
    PriceValidation, ProductStatus
)
from product.models import Product as ProductModel
from .forms import PriceSubmissionForm, CityForm

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
            # Recherche des produits similaires
            search_terms = product_name.split()
            query = Q()
            
            for term in search_terms:
                term_query = (
                    Q(title__icontains=term) |
                    Q(brand__icontains=term) |
                    Q(description__icontains=term) |
                    Q(category__name__icontains=term)
                )
                
                # Ajouter des recherches spécifiques pour les téléphones
                if hasattr(ProductModel, 'phone'):
                    term_query |= (
                        Q(phone__brand__icontains=term) |
                        Q(phone__model__icontains=term) |
                        Q(phone__operating_system__icontains=term) |
                        Q(phone__processor__icontains=term)
                    )
                
                query &= term_query
            
            # Récupérer les produits
            similar_products = ProductModel.objects.filter(query).select_related(
                'category',
                'supplier'
            ).prefetch_related(
                Prefetch('price_entries', 
                        queryset=PriceEntry.objects.filter(
                            is_active=True
                        ).select_related('city')
                        .order_by('-created_at'))
            ).order_by('title')
            
            # Pagination
            paginator = Paginator(similar_products, 5)
            try:
                products_page = paginator.page(page)
            except Http404:
                products_page = paginator.page(1)
            
            results = []
            for product in products_page:
                prices_by_city = {}
                for price_entry in product.price_entries.all():
                    if price_entry.city not in prices_by_city:
                        # Utiliser la nouvelle méthode get_average_price
                        avg_price_info = PriceEntry.get_average_price(
                            product=product,
                            city=price_entry.city
                        )
                        
                        prices_by_city[price_entry.city] = {
                            'price': avg_price_info['average_price'] if avg_price_info['count'] > 1 else price_entry.price,
                            'price_change': price_entry.price_change,
                            'price_change_percentage': price_entry.price_change_percentage,
                            'updated_at': price_entry.created_at,
                            'is_average': avg_price_info['count'] > 1,
                            'count': avg_price_info['count']
                        }
                
                results.append({
                    'product': product,
                    'prices_by_city': prices_by_city
                })
            
            return render(request, 'price_checker/partials/price_results.html', {
                'results': results,
                'page_obj': products_page,
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

class UserDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'price_checker/user_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Récupérer les statistiques des soumissions
        submissions = PriceSubmission.objects.filter(user=user)
        context['total_submissions'] = submissions.count()
        context['pending_submissions'] = submissions.filter(status='PENDING').count()
        context['approved_submissions'] = submissions.filter(status='APPROVED').count()
        
        # Récupérer les dernières soumissions
        context['recent_submissions'] = submissions.select_related(
            'product', 'city'
        ).order_by('-created_at')[:5]
        
        return context

class PriceSubmissionListView(LoginRequiredMixin, ListView):
    model = PriceSubmission
    template_name = 'price_checker/price_submission_list.html'
    context_object_name = 'submissions'
    paginate_by = 10

    def get_queryset(self):
        return PriceSubmission.objects.filter(user=self.request.user).select_related(
            'product', 'city'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Récupérer les statistiques des soumissions
        submissions = PriceSubmission.objects.filter(user=user)
        context['total_submissions'] = submissions.count()
        context['pending_submissions'] = submissions.filter(status='PENDING').count()
        context['approved_submissions'] = submissions.filter(status='APPROVED').count()
        
        return context

class PriceSubmissionCreateView(LoginRequiredMixin, CreateView):
    model = PriceSubmission
    form_class = PriceSubmissionForm
    template_name = 'price_checker/price_submission_form.html'
    success_url = reverse_lazy('price_checker:price_submission_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {
            'user': self.request.user
        }
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 'PENDING'
        
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Votre soumission a été enregistrée avec succès.')
            return response
        except Exception as e:
            messages.error(self.request, f'Une erreur est survenue: {str(e)}')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Récupérer les statistiques des soumissions
        submissions = PriceSubmission.objects.filter(user=user)
        context['total_submissions'] = submissions.count()
        context['pending_submissions'] = submissions.filter(status='PENDING').count()
        context['approved_submissions'] = submissions.filter(status='APPROVED').count()
        
        context['cities'] = City.objects.filter(is_active=True)
        context['is_update'] = False
        return context

class PriceSubmissionDeleteView(LoginRequiredMixin, DeleteView):
    model = PriceSubmission
    success_url = reverse_lazy('price_checker:price_submission_list')
    template_name = 'price_checker/price_submission_confirm_delete.html'

    def get_queryset(self):
        # Ne permettre la suppression que des soumissions en attente et appartenant à l'utilisateur
        return PriceSubmission.objects.filter(
            user=self.request.user,
            status='PENDING'
        )

    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, 'La soumission a été supprimée avec succès.')
            return response
        except Exception as e:
            messages.error(request, f'Une erreur est survenue: {str(e)}')
            return self.get(request, *args, **kwargs)

class PriceSubmissionUpdateView(LoginRequiredMixin, UpdateView):
    model = PriceSubmission
    form_class = PriceSubmissionForm
    template_name = 'price_checker/price_submission_form.html'
    success_url = reverse_lazy('price_checker:price_submission_list')

    def get_queryset(self):
        # Ne permettre la modification que des soumissions en attente et appartenant à l'utilisateur
        return PriceSubmission.objects.filter(
            user=self.request.user,
            status='PENDING'
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {
            'user': self.request.user
        }
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Désactiver les champs qui ne peuvent pas être modifiés
        form.fields['product'].disabled = True
        form.fields['city'].disabled = True
        return form

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'La soumission a été mise à jour avec succès.')
            return response
        except Exception as e:
            messages.error(self.request, f'Une erreur est survenue: {str(e)}')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cities'] = City.objects.filter(is_active=True)
        context['is_update'] = True
        return context

# Vues admin
class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'price_checker/admin/dashboard.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques générales
        context['pending_submissions'] = PriceSubmission.objects.filter(status='PENDING').count()
        context['total_submissions'] = PriceSubmission.objects.count()
        context['total_cities'] = City.objects.count()
        context['total_products'] = Product.objects.count()
        
        # Dernières soumissions en attente
        context['recent_submissions'] = PriceSubmission.objects.filter(
            status='PENDING'
        ).select_related(
            'product', 'city', 'user'
        ).order_by('-created_at')[:5]
        
        # Derniers prix validés
        context['recent_prices'] = PriceEntry.objects.filter(
            is_active=True
        ).select_related(
            'product', 'city', 'user'
        ).order_by('-created_at')[:5]
        
        return context

class AdminPriceSubmissionListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = PriceSubmission
    template_name = 'price_checker/admin/price_submission_list.html'
    context_object_name = 'submissions'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = PriceSubmission.objects.select_related(
            'product', 'city', 'user', 'validated_by'
        )

        # Filtres
        status = self.request.GET.get('status')
        user = self.request.GET.get('user')
        city = self.request.GET.get('city')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if status:
            queryset = queryset.filter(status=status)
        if user:
            queryset = queryset.filter(user__username__icontains=user)
        if city:
            queryset = queryset.filter(city__name__icontains=city)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer les valeurs des filtres
        context['filters'] = {
            'status': self.request.GET.get('status', ''),
            'user': self.request.GET.get('user', ''),
            'city': self.request.GET.get('city', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', '')
        }
        
        # Récupérer les villes uniques pour le filtre
        context['cities'] = City.objects.values_list('name', flat=True).distinct().order_by('name')
        
        # Statistiques
        context['total_submissions'] = PriceSubmission.objects.count()
        context['pending_submissions'] = PriceSubmission.objects.filter(status='PENDING').count()
        context['approved_submissions'] = PriceSubmission.objects.filter(status='APPROVED').count()
        context['rejected_submissions'] = PriceSubmission.objects.filter(status='REJECTED').count()
        
        return context

def approve_price_submission(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse_lazy('price_checker:admin_price_submission_list'))
    
    submission = PriceSubmission.objects.get(pk=pk)
    submission.status = 'APPROVED'
    submission.validated_by = request.user
    submission.save()
    
    # Créer une entrée de prix
    PriceEntry.objects.create(
        product=submission.product,
        city=submission.city,
        price=submission.price,
        user=submission.user,
        validated_by=request.user
    )
    
    messages.success(request, 'La soumission a été approuvée avec succès.')
    return HttpResponseRedirect(reverse_lazy('price_checker:admin_price_submission_list'))

def reject_price_submission(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse_lazy('price_checker:admin_price_submission_list'))
    
    submission = PriceSubmission.objects.get(pk=pk)
    submission.status = 'REJECTED'
    submission.validated_by = request.user
    submission.save()
    
    messages.success(request, 'La soumission a été rejetée avec succès.')
    return HttpResponseRedirect(reverse_lazy('price_checker:admin_price_submission_list'))

class AdminPriceEntryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = PriceEntry
    template_name = 'price_checker/admin/price_entry_list.html'
    context_object_name = 'price_entries'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return PriceEntry.objects.filter(is_active=True).select_related(
            'product', 'city', 'user', 'submission', 'submission__validated_by'
        ).order_by('-created_at')

class AdminProductStatusListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = ProductModel
    template_name = 'price_checker/admin/product_status_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = ProductModel.objects.select_related(
            'status',
            'category'
        )

        # Filtres
        brand = self.request.GET.get('brand')
        category = self.request.GET.get('category')
        status = self.request.GET.get('status')

        if brand:
            queryset = queryset.filter(brand__icontains=brand)
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if status == 'salam':
            queryset = queryset.filter(is_salam=True)
        elif status == 'no_salam':
            queryset = queryset.filter(is_salam=False)

        return queryset.order_by('title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer les valeurs des filtres
        context['filters'] = {
            'brand': self.request.GET.get('brand', ''),
            'category': self.request.GET.get('category', ''),
            'status': self.request.GET.get('status', '')
        }
        
        # Récupérer les marques uniques pour le filtre
        context['brands'] = ProductModel.objects.values_list(
            'brand', flat=True
        ).distinct().order_by('brand')
        
        # Récupérer les catégories uniques
        context['categories'] = ProductModel.objects.values_list(
            'category__name', flat=True
        ).distinct().order_by('category__name')
        
        return context

def toggle_product_status(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse_lazy('price_checker:admin_product_status_list'))
    
    product = ProductModel.objects.get(pk=pk)
    product.is_salam = not product.is_salam
    product.save()
    
    messages.success(request, f'Le statut Salam du produit a été {"activé" if product.is_salam else "désactivé"} avec succès.')
    return HttpResponseRedirect(reverse_lazy('price_checker:admin_product_status_list'))

class AdminCityListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = City
    template_name = 'price_checker/admin/city_list.html'
    context_object_name = 'cities'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return City.objects.all().order_by('name')

def add_city(request):
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse_lazy('price_checker:admin_city_list'))
    
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'La ville a été ajoutée avec succès.')
            return HttpResponseRedirect(reverse_lazy('price_checker:admin_city_list'))
    else:
        form = CityForm()
    
    return render(request, 'price_checker/admin/city_form.html', {
        'form': form,
        'city': None
    })

def update_city(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse_lazy('price_checker:admin_city_list'))
    
    city = City.objects.get(pk=pk)
    
    if request.method == 'POST':
        form = CityForm(request.POST, instance=city)
        if form.is_valid():
            form.save()
            messages.success(request, 'La ville a été mise à jour avec succès.')
            return HttpResponseRedirect(reverse_lazy('price_checker:admin_city_list'))
    else:
        form = CityForm(instance=city)
    
    return render(request, 'price_checker/admin/city_form.html', {
        'form': form,
        'city': city
    })

def delete_city(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse_lazy('price_checker:admin_city_list'))
    
    city = City.objects.get(pk=pk)
    city.delete()
    
    messages.success(request, 'La ville a été supprimée avec succès.')
    return HttpResponseRedirect(reverse_lazy('price_checker:admin_city_list'))

@require_GET
def get_products_by_brand(request):
    brand = request.GET.get('brand', '')
    if not brand:
        return JsonResponse({'products': []})
    
    products = ProductModel.objects.filter(
        brand__icontains=brand
    ).values_list('id', 'title')
    
    return JsonResponse({
        'products': list(products)
    })

@require_GET
def get_product_details(request):
    product_id = request.GET.get('product_id')
    if not product_id:
        return JsonResponse({'product': None})
    
    try:
        product = ProductModel.objects.get(id=product_id)
        product_data = {
            'id': product.id,
            'title': product.title,
            'brand': product.brand,
            'category': product.category.name if product.category else '',
            'price': str(product.price),
            'description': product.description or ''
        }
        return JsonResponse({'product': product_data})
    except ProductModel.DoesNotExist:
        return JsonResponse({'product': None})

@login_required
@user_passes_test(lambda u: u.is_staff)
def toggle_salam(request, product_id):
    try:
        product = ProductModel.objects.get(pk=product_id)
        product.is_salam = not product.is_salam
        product.save()
        return redirect('price_checker:admin_product_status_list')
    except ProductModel.DoesNotExist:
        return redirect('price_checker:admin_product_status_list')

class PriceEntryListView(ListView):
    model = PriceEntry
    template_name = 'price_checker/price_entry_list.html'
    context_object_name = 'price_entries'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        city = self.request.GET.get('city')
        
        if search_query:
            queryset = queryset.filter(
                Q(product__title__icontains=search_query) |
                Q(city__name__icontains=search_query)
            )
        
        if city:
            queryset = queryset.filter(city__name=city)
        
        return queryset.select_related('product', 'city').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cities'] = City.objects.filter(is_active=True)
        return context

class PriceEntryDetailView(DetailView):
    model = PriceEntry
    template_name = 'price_checker/price_entry_detail.html'
    context_object_name = 'price_entry'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        price_entry = self.get_object()
        
        # Récupérer l'historique des prix pour ce produit et cette ville
        price_history = PriceEntry.objects.filter(
            product=price_entry.product,
            city=price_entry.city,
            is_active=True
        ).order_by('-created_at')
        
        context['price_history'] = price_history
        context['average_price'] = PriceEntry.get_average_price(
            product=price_entry.product,
            city=price_entry.city
        )
        
        return context

@login_required
def add_price_entry(request):
    if request.method == 'POST':
        form = PriceEntryForm(request.POST)
        if form.is_valid():
            price_entry = form.save(commit=False)
            price_entry.user = request.user
            price_entry.save()
            messages.success(request, 'Prix ajouté avec succès.')
            return redirect('price_checker:price_entry_list')
    else:
        form = PriceEntryForm()
    
    return render(request, 'price_checker/price_entry_form.html', {
        'form': form
    })

def get_product_prices(request):
    product_id = request.GET.get('product_id')
    if not product_id:
        return JsonResponse({'prices': []})
    
    try:
        product = ProductModel.objects.get(id=product_id)
        prices = PriceEntry.objects.filter(
            product=product,
            is_active=True
        ).select_related('city').order_by('-created_at')
        
        price_data = []
        for price in prices:
            avg_price_info = PriceEntry.get_average_price(
                product=product,
                city=price.city
            )
            
            price_data.append({
                'city': price.city.name,
                'price': str(price.price),
                'average_price': str(avg_price_info['average_price']) if avg_price_info['average_price'] else None,
                'count': avg_price_info['count'],
                'updated_at': price.created_at.isoformat()
            })
        
        return JsonResponse({'prices': price_data})
    except ProductModel.DoesNotExist:
        return JsonResponse({'prices': []}) 