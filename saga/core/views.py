from django.shortcuts import render
from django.views.generic import TemplateView
from .models import SiteConfiguration
from product.models import ShippingMethod
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import CookieConsent
from django.http import Http404

class TermsConditionsView(TemplateView):
    """Vue pour la page 'Mentions légales'"""
    template_name = 'components/_terms_conditions.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = SiteConfiguration.get_config()
        return context

class CGVView(TemplateView):
    """Vue pour la page 'Conditions générales de vente'"""
    template_name = 'components/_cgv.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = SiteConfiguration.get_config()
        return context

class AboutView(TemplateView):
    """Vue pour la page principale 'À propos'"""
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = SiteConfiguration.get_config()
        return context

class AboutStoryView(TemplateView):
    """Vue pour la page 'Notre histoire'"""
    template_name = 'core/about_story.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = SiteConfiguration.get_config()
        return context

class AboutValuesView(TemplateView):
    """Vue pour la page 'Nos valeurs'"""
    template_name = 'core/about_values.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = SiteConfiguration.get_config()
        return context

class ServiceLoyaltyView(TemplateView):
    """Vue pour la page 'Fidélité Bolibana'"""
    template_name = 'core/service_loyalty.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = SiteConfiguration.get_config()
        
        # Données de fidélité pour utilisateurs connectés
        if self.request.user.is_authenticated:
            from cart.models import Order
            
            # Compter les commandes de l'utilisateur
            total_orders = Order.objects.filter(
                user=self.request.user,
                status__in=['delivered', 'shipped', 'processing', 'confirmed']
            ).count()
            
            # Calculer les points de fidélité (1 point par 1000 FCFA dépensés)
            total_spent = Order.objects.filter(
                user=self.request.user,
                status='delivered'
            ).aggregate(
                total=models.Sum('total')
            )['total'] or 0
            
            loyalty_points = int(total_spent / 1000)  # 1 point par 1000 FCFA
            
            # Déterminer le niveau de fidélité
            if loyalty_points >= 100:
                loyalty_level = "Diamant"
            elif loyalty_points >= 50:
                loyalty_level = "Or"
            elif loyalty_points >= 20:
                loyalty_level = "Argent"
            else:
                loyalty_level = "Bronze"
            
            context.update({
                'total_orders': total_orders,
                'loyalty_points': loyalty_points,
                'loyalty_level': loyalty_level,
                'total_spent': total_spent,
            })
        
        return context

class ServiceExpressView(TemplateView):
    """Vue pour la page 'Livraison express'"""
    template_name = 'core/service_express.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = SiteConfiguration.get_config()
        
        # Récupérer toutes les méthodes de livraison disponibles
        shipping_methods = ShippingMethod.objects.all().order_by('price')
        context['shipping_methods'] = shipping_methods
        
        # Récupérer spécifiquement la méthode de livraison express
        express_method = ShippingMethod.objects.filter(
            name__icontains='express'
        ).first()
        context['express_method'] = express_method
        
        # Calculer les statistiques pour l'affichage
        if shipping_methods.exists():
            context['min_price'] = shipping_methods.first().price
            context['max_price'] = shipping_methods.last().price
            context['total_methods'] = shipping_methods.count()
        else:
            context['min_price'] = 0
            context['max_price'] = 0
            context['total_methods'] = 0
        
        return context

class HelpCenterView(TemplateView):
    """Vue pour la page 'Centre d'aide'"""
    template_name = 'core/help_center.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = SiteConfiguration.get_config()
        return context

class HelpReturnsView(TemplateView):
    """Vue pour la page 'Retours faciles'"""
    template_name = 'core/help_returns.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = SiteConfiguration.get_config()
        return context

class HelpWarrantyView(TemplateView):
    """Vue pour la page 'Garantie qualité'"""
    template_name = 'core/help_warranty.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = SiteConfiguration.get_config()
        return context 

@csrf_exempt
def save_cookie_consent(request):
    if request.method == 'POST':
        analytics = request.POST.get('analytics') == 'true'
        marketing = request.POST.get('marketing') == 'true'
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key or request.session._get_or_create_session_key()

        print(f"🔍 API - Analytics: {analytics}, Marketing: {marketing}")
        print(f"🔍 API - User: {user}, Session: {session_id[:10]}...")

        # Mettre à jour ou créer le consentement
        consent, created = CookieConsent.objects.update_or_create(
            user=user,
            session_id=session_id,
            defaults={
                'analytics': analytics,
                'marketing': marketing
            }
        )
        
        print(f"🔍 API - Consent créé: {created}, ID: {consent.id}")
        
        response_data = {'success': True, 'message': 'Consentement enregistré'}
        return JsonResponse(response_data)
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405) 

def test_404_view(request):
    """Vue de test pour la page 404"""
    raise Http404("Page de test 404")

def test_500_view(request):
    """Vue de test pour la page 500"""
    raise Exception("Erreur de test 500")

def test_403_view(request):
    """Vue de test pour la page 403"""
    from django.core.exceptions import PermissionDenied
    raise PermissionDenied("Accès interdit de test") 

# Vues d'erreur personnalisées
def custom_404(request, exception):
    """Vue personnalisée pour l'erreur 404"""
    return render(request, '404.html', status=404)

def custom_500(request):
    """Vue personnalisée pour l'erreur 500"""
    return render(request, '500.html', status=500)

def custom_403(request, exception):
    """Vue personnalisée pour l'erreur 403"""
    return render(request, '403.html', status=403) 