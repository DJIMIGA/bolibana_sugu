/**
 * Gestionnaire d'erreurs pour la recherche
 */

document.addEventListener('DOMContentLoaded', function() {
    // Gérer les erreurs HTMX
    document.body.addEventListener('htmx:responseError', function(evt) {
        if (evt.detail.elt.id && evt.detail.elt.id.includes('search')) {
            const status = evt.detail.xhr?.status || 'N/A';
            console.error(`[Search] ❌ Erreur ${status}`);
            
            // Afficher un message d'erreur
            const target = evt.detail.target;
            if (target && window.SearchUtils) {
                const errorMessage = window.SearchUtils.handleSearchError(evt.detail);
                target.innerHTML = '';
                target.appendChild(errorMessage);
            }
        }
    });

    // Gérer les erreurs de réseau
    document.body.addEventListener('htmx:sendError', function(evt) {
        if (evt.detail.elt.id && evt.detail.elt.id.includes('search')) {
            console.error('[Search] ❌ Erreur de connexion');
            
            // Afficher un message d'erreur de connexion
            const target = evt.detail.target;
            if (target) {
                target.innerHTML = `
                    <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
                        <div class="w-8 h-8 mx-auto mb-2 text-yellow-500">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/>
                            </svg>
                        </div>
                        <p class="text-yellow-700 text-sm">Problème de connexion. Vérifiez votre connexion internet.</p>
                    </div>
                `;
            }
        }
    });

    // Gérer les timeouts
    document.body.addEventListener('htmx:timeout', function(evt) {
        if (evt.detail.elt.id && evt.detail.elt.id.includes('search')) {
            console.error('[Search] ⏱️ Timeout');
            
            // Afficher un message de timeout
            const target = evt.detail.target;
            if (target) {
                target.innerHTML = `
                    <div class="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
                        <div class="w-8 h-8 mx-auto mb-2 text-orange-500">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                        <p class="text-orange-700 text-sm">La recherche prend plus de temps que prévu. Veuillez réessayer.</p>
                    </div>
                `;
            }
        }
    });
}); 