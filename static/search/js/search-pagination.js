/**
 * Gestionnaire de pagination pour les résultats de recherche
 */

document.addEventListener('DOMContentLoaded', function() {
    // Gérer la pagination des résultats de recherche
    document.body.addEventListener('click', function(e) {
        if (e.target.matches('[data-search-pagination]') || e.target.closest('[data-search-pagination]')) {
            e.preventDefault();
            
            const paginationLink = e.target.matches('[data-search-pagination]') ? 
                e.target : e.target.closest('[data-search-pagination]');
            
            const url = paginationLink.getAttribute('href');
            const target = paginationLink.getAttribute('data-target') || '#searchResults';
            const targetElement = document.querySelector(target);
            
            if (url && targetElement) {
                // Afficher un indicateur de chargement
                targetElement.innerHTML = `
                    <div class="flex items-center justify-center p-8">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500"></div>
                        <span class="ml-2 text-gray-600">Chargement...</span>
                    </div>
                `;
                
                // Faire la requête HTMX
                htmx.ajax('GET', url, {
                    target: target,
                    swap: 'innerHTML',
                    headers: {
                        'HX-Request': 'true'
                    }
                }).then(function() {
                    // Scroll vers le haut des résultats après le chargement
                    if (window.SearchUtils) {
                        window.SearchUtils.scrollToTop(targetElement);
                    }
                }).catch(function(error) {
                    console.error('Erreur de pagination:', error);
                    targetElement.innerHTML = `
                        <div class="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                            <p class="text-red-700 text-sm">Erreur lors du chargement de la page.</p>
                        </div>
                    `;
                });
            }
        }
    });

    // Gérer la pagination avec HTMX
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.elt && evt.detail.elt.hasAttribute('data-search-pagination')) {
            const target = evt.detail.target;
            if (target && window.SearchUtils) {
                // Scroll vers le haut des résultats
                window.SearchUtils.scrollToTop(target);
                
                // Mettre à jour l'URL sans recharger la page
                const url = evt.detail.elt.getAttribute('href');
                if (url) {
                    window.history.pushState({}, '', url);
                }
            }
        }
    });
}); 