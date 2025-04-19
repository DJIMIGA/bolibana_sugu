// Gestion des quantités dans le panier
document.addEventListener('DOMContentLoaded', function() {
    // Mise à jour du total après changement de quantité
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        if (evt.detail.target.closest('li')) {
            updateCartTotal();
        }
    });

    // Mise à jour du compteur d'articles
    function updateCartCount() {
        const cartCount = document.getElementById('cart-count');
        const cartItems = document.querySelectorAll('#cart-content .cart-item');
        
        if (cartCount) {
            const itemCount = cartItems.length;
            cartCount.textContent = itemCount;
            cartCount.classList.toggle('hidden', itemCount === 0);
        }
    }

    // Gestionnaire d'erreurs HTMX
    document.body.addEventListener('htmx:responseError', function(evt) {
        console.error('Erreur lors de la mise à jour de la quantité:', evt.detail.error);
    });
}); 