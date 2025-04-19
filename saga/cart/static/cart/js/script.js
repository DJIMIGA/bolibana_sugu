// Gestionnaire d'événements pour les requêtes HTMX
document.addEventListener('htmx:afterRequest', function(evt) {
    if (evt.detail.target.id === 'product-options-content') {
        console.log('Réponse reçue:', evt.detail.xhr.responseText);
    }
});

// Fonction pour ouvrir le sidebar des options
function openProductOptions(productId) {
    const sidebar = document.getElementById('product-options-sidebar');
    const overlay = sidebar.querySelector('.absolute.inset-0.bg-black\\/40');
    const content = sidebar.querySelector('.transform');
    
    // Retirer les classes qui cachent le sidebar
    sidebar.classList.remove('pointer-events-none');
    overlay.classList.remove('opacity-0', 'pointer-events-none');
    content.classList.remove('translate-x-full');
    
    // Désactiver le scroll du body
    document.body.style.overflow = 'hidden';
    
    // Charger les options du produit avec HTMX
    htmx.ajax('GET', `/cart/product-options/${productId}/`, {
        target: '#product-options-content',
        swap: 'innerHTML',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    });
}

// Fonction pour fermer le sidebar des options
function closeProductOptions() {
    const sidebar = document.getElementById('product-options-sidebar');
    const overlay = sidebar.querySelector('.absolute.inset-0.bg-black\\/40');
    const content = sidebar.querySelector('.transform');
    
    // Ajouter les classes pour cacher le sidebar
    overlay.classList.add('opacity-0', 'pointer-events-none');
    content.classList.add('translate-x-full');
    
    // Réactiver le scroll du body après l'animation
    setTimeout(() => {
        sidebar.classList.add('pointer-events-none');
        document.body.style.overflow = '';
    }, 500);
}

// Initialisation au chargement du document
document.addEventListener('DOMContentLoaded', function() {
    // Fermeture avec la touche Escape
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeProductOptions();
        }
    });

    // Fermeture en cliquant sur l'overlay
    const overlay = document.getElementById('product-options-overlay');
    if (overlay) {
        overlay.addEventListener('click', closeProductOptions);
    }

    // Gestion des formulaires chargés dynamiquement
    document.body.addEventListener('htmx:afterSwap', function(e) {
        if (e.detail.target.id === 'product-options-content') {
            const form = e.detail.target.querySelector('form');
            if (form) {
                form.addEventListener('htmx:afterRequest', function(e) {
                    if (e.detail.successful) {
                        setTimeout(closeProductOptions, 500);
                    }
                });
            }
        }
    });
}); 