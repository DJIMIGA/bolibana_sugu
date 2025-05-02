from django.shortcuts import render
from django.views.generic import ListView, CreateView, DeleteView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Q, Prefetch, Count, Avg, Max, Min
from django.core.paginator import Paginator
from django.http import Http404
from django.views.decorators.http import require_GET
from .models import (
    PriceEntry, PriceSubmission, City, Product,
    PriceValidation, ProductStatus
)
from product.models import Phone, PhoneVariant
from .forms import PriceSubmissionForm, CityForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect

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
                        Q(phone__brand__icontains=term) |
                        Q(phone__model__icontains=term) |
                        Q(phone__operating_system__icontains=term) |
                        Q(phone__processor__icontains=term) |
                        Q(color__name__icontains=term) |
                        Q(ram=numeric_value) |
                        Q(storage=numeric_value)
                    )
                except ValueError:
                    term_query = (
                        Q(phone__brand__icontains=term) |
                        Q(phone__model__icontains=term) |
                        Q(phone__operating_system__icontains=term) |
                        Q(phone__processor__icontains=term) |
                        Q(color__name__icontains=term)
                    )
                
                query &= term_query
            
            # Récupérer les variantes
            similar_variants = PhoneVariant.objects.filter(query).select_related(
                'phone',
                'color'
            ).prefetch_related(
                Prefetch('price_entries', 
                        queryset=PriceEntry.objects.filter(
                            is_active=True
                        ).select_related('city')
                        .order_by('-created_at'))
            ).order_by(
                'phone__brand',
                'phone__model',
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
                            product=variant.phone.product,
                            variant=variant,
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
                    'product': variant.phone,
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
            'product', 'variant', 'city'
        ).order_by('-created_at')[:5]
        
        return context

class PriceSubmissionListView(LoginRequiredMixin, ListView):
    model = PriceSubmission
    template_name = 'price_checker/price_submission_list.html'
    context_object_name = 'submissions'
    paginate_by = 10

    def get_queryset(self):
        return PriceSubmission.objects.filter(user=self.request.user).select_related(
            'product', 'variant', 'city'
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
        form.fields['variant'].disabled = True
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
            'product', 'variant', 'city', 'user'
        ).order_by('-created_at')[:5]
        
        # Derniers prix validés
        context['recent_prices'] = PriceEntry.objects.filter(
            is_active=True
        ).select_related(
            'product', 'variant', 'city', 'user'
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
            'product', 'variant', 'city', 'user', 'validated_by'
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
        variant=submission.variant,
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
            'product', 'variant', 'city', 'user', 'submission', 'submission__validated_by'
        ).order_by('-created_at')

class AdminProductStatusListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = PhoneVariant
    template_name = 'price_checker/admin/product_status_list.html'
    context_object_name = 'variants'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = PhoneVariant.objects.select_related(
            'phone__product__status',
            'phone__product',
            'color'
        )

        # Filtres
        brand = self.request.GET.get('brand')
        model = self.request.GET.get('model')
        storage = self.request.GET.get('storage')
        ram = self.request.GET.get('ram')
        status = self.request.GET.get('status')

        if brand:
            queryset = queryset.filter(phone__brand__iexact=brand)
        if model:
            queryset = queryset.filter(phone__model__icontains=model)
        if storage:
            queryset = queryset.filter(storage=storage)
        if ram:
            queryset = queryset.filter(ram=ram)
        if status == 'salam':
            queryset = queryset.filter(disponible_salam=True)
        elif status == 'no_salam':
            queryset = queryset.filter(disponible_salam=False)

        return queryset.order_by('phone__product__title', 'storage', 'ram')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer les valeurs des filtres
        context['filters'] = {
            'brand': self.request.GET.get('brand', ''),
            'model': self.request.GET.get('model', ''),
            'storage': self.request.GET.get('storage', ''),
            'ram': self.request.GET.get('ram', ''),
            'status': self.request.GET.get('status', '')
        }
        
        # Récupérer les marques uniques pour le filtre
        context['brands'] = PhoneVariant.objects.values_list(
            'phone__brand', flat=True
        ).distinct().order_by('phone__brand')
        
        # Récupérer les valeurs de stockage uniques
        context['storages'] = PhoneVariant.objects.values_list(
            'storage', flat=True
        ).distinct().order_by('storage')
        
        # Récupérer les valeurs de RAM uniques
        context['rams'] = PhoneVariant.objects.values_list(
            'ram', flat=True
        ).distinct().order_by('ram')
        
        return context

def toggle_product_status(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse_lazy('price_checker:admin_product_status_list'))
    
    product = Product.objects.get(pk=pk)
    product.status.is_active = not product.status.is_active
    product.status.save()
    
    messages.success(request, f'Le statut du produit a été {"activé" if product.status.is_active else "désactivé"} avec succès.')
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
    
    products = Phone.objects.filter(
        brand__iexact=brand
    ).values_list('id', 'model')
    
    return JsonResponse({
        'products': list(products)
    })

@require_GET
def get_phone_variants(request):
    product_id = request.GET.get('product_id')
    if not product_id:
        return JsonResponse({'variants': []})
    
        variants = PhoneVariant.objects.filter(
        phone_id=product_id
    ).select_related('color').values(
        'id',
        'ram',
        'storage',
        'color__name'
    )
    
    return JsonResponse({
        'variants': list(variants)
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def toggle_salam(request, variant_id):
    try:
        variant = PhoneVariant.objects.get(pk=variant_id)
        variant.disponible_salam = not variant.disponible_salam
        variant.save()
        return redirect('price_checker:admin_product_status_list')
    except PhoneVariant.DoesNotExist:
        return redirect('price_checker:admin_product_status_list') 