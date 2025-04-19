document.addEventListener('DOMContentLoaded', function() {
    // Récupération des éléments du DOM
    const cartSidebar = document.getElementById('cart-sidebar');
    const cartOverlay = document.getElementById('cart-overlay');
    const cartContainer = document.getElementById('cart-container');

    if (!cartSidebar || !cartOverlay || !cartContainer) {
        console.error('Éléments du panier non trouvés');
        return;
    }

    // Fonction pour ouvrir le panier
    window.openCart = function() {
        // Activer les interactions
        cartSidebar.classList.remove('pointer-events-none');
        cartOverlay.style.pointerEvents = 'auto'; // Activer les interactions sur l'overlay
        cartOverlay.classList.remove('opacity-0');
        cartContainer.classList.remove('translate-x-full');
        
        // Empêcher le défilement du body
        document.body.style.overflow = 'hidden';
        
        // Si le sidebar des options produit est ouvert, le fermer
        const productOptionsSidebar = document.getElementById('product-options-sidebar');
        if (productOptionsSidebar && !productOptionsSidebar.classList.contains('pointer-events-none')) {
            window.closeProductOptions();
        }
    };

    // Fonction pour fermer le panier
    window.closeCart = function() {
        // Désactiver les interactions
        cartOverlay.classList.add('opacity-0');
        cartContainer.classList.add('translate-x-full');
        
        // Attendre la fin de l'animation avant de cacher complètement
        setTimeout(() => {
            cartSidebar.classList.add('pointer-events-none');
            cartOverlay.style.pointerEvents = 'none'; // Désactiver les interactions sur l'overlay
            // Rétablir le défilement du body
            document.body.style.overflow = '';
        }, 500);
    };

    // Gestionnaire d'événements pour la touche Escape
    function handleEscapeKey(event) {
        if (event.key === 'Escape' && !cartSidebar.classList.contains('pointer-events-none')) {
            window.closeCart();
        }
    }

    // Ajouter les écouteurs d'événements
    document.addEventListener('keydown', handleEscapeKey);

    // Utiliser addEventListener au lieu de onclick dans le HTML
    cartOverlay.addEventListener('click', function(event) {
        // S'assurer que le clic est bien sur l'overlay et pas sur ses enfants
        if (event.target === cartOverlay) {
            window.closeCart();
        }
    });

    // Gestionnaire pour les mises à jour HTMX du panier
    document.addEventListener('htmx:afterSwap', function(evt) {
        if (evt.detail.target.id === 'cart-content') {
            // Mettre à jour le compteur du panier si nécessaire
            const cartCount = document.getElementById('cart-count');
            if (cartCount) {
                const itemCount = document.querySelectorAll('#cart-content .cart-item').length;
                cartCount.textContent = itemCount;
                
                if (itemCount > 0) {
                    cartCount.classList.remove('hidden');
                } else {
                    cartCount.classList.add('hidden');
                }
            }
        }
    });
}); 