"""
Vues pour la gestion de l'intégration avec l'app de gestion de stock
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import logging

from .models import ExternalProduct, ExternalCategory
from .services import ProductSyncService
from .tasks import sync_products_auto, sync_categories_auto

logger = logging.getLogger(__name__)


@login_required
def sync_products(request):
    """
    Vue pour déclencher une synchronisation manuelle des produits
    """
    if request.method == 'POST':
        force = request.POST.get('force', 'false') == 'true'
        try:
            # Utiliser la fonction de synchronisation automatique
            result = sync_products_auto(force=force)
            
            if result['success']:
                stats = result['stats']
                messages.success(
                    request,
                    f'Synchronisation terminée: {stats["created"]} créés, {stats["updated"]} mis à jour, {stats["errors"]} erreurs'
                )
            else:
                messages.warning(request, f'Synchronisation: {result["message"]}')
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation: {str(e)}")
            messages.error(request, f'Erreur lors de la synchronisation: {str(e)}')
        
        return redirect('inventory:sync_status')
    
    return render(request, 'inventory/sync_products.html')


@login_required
def sync_categories(request):
    """
    Vue pour déclencher une synchronisation manuelle des catégories
    """
    if request.method == 'POST':
        force = request.POST.get('force', 'false') == 'true'
        try:
            # Utiliser la fonction de synchronisation automatique
            result = sync_categories_auto(force=force)
            
            if result['success']:
                stats = result['stats']
                messages.success(
                    request,
                    f'Synchronisation des catégories terminée: {stats["created"]} créées, {stats["updated"]} mises à jour, {stats["errors"]} erreurs'
                )
            else:
                messages.warning(request, f'Synchronisation: {result["message"]}')
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation: {str(e)}")
            messages.error(request, f'Erreur lors de la synchronisation: {str(e)}')
        
        return redirect('inventory:sync_status')
    
    return render(request, 'inventory/sync_categories.html')


@login_required
def sync_status(request):
    """
    Vue pour voir le statut de synchronisation
    """
    # Statistiques
    stats = {
        'total_products': ExternalProduct.objects.count(),
        'synced_products': ExternalProduct.objects.filter(sync_status='synced').count(),
        'pending_products': ExternalProduct.objects.filter(sync_status='pending').count(),
        'error_products': ExternalProduct.objects.filter(sync_status='error').count(),
        'total_categories': ExternalCategory.objects.count(),
    }
    
    # Derniers produits synchronisés
    recent_products = ExternalProduct.objects.select_related('product').order_by('-last_synced_at')[:10]
    
    return render(request, 'inventory/sync_status.html', {
        'stats': stats,
        'recent_products': recent_products,
    })


# Vues API JSON pour les appels AJAX
@login_required
def api_sync_status(request):
    """
    API pour récupérer le statut de synchronisation en JSON
    """
    stats = {
        'total_products': ExternalProduct.objects.count(),
        'synced_products': ExternalProduct.objects.filter(sync_status='synced').count(),
        'pending_products': ExternalProduct.objects.filter(sync_status='pending').count(),
        'error_products': ExternalProduct.objects.filter(sync_status='error').count(),
    }
    
    return JsonResponse(stats)
