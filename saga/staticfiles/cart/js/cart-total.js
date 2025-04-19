// Gestion du total du panier
document.addEventListener('DOMContentLoaded', function() {
    window.updateCartTotal = function() {
        const cartItems = document.querySelectorAll('#cart-content .cart-item');
        let total = 0;

        cartItems.forEach(item => {
            const price = parseFloat(item.dataset.price);
            const quantity = parseInt(item.dataset.quantity);
            if (!isNaN(price) && !isNaN(quantity)) {
                total += price * quantity;
            }
        });

        const totalElement = document.getElementById('cart-total');
        if (totalElement) {
            totalElement.textContent = `${total.toLocaleString()} FCFA`;
        }
    };

    // Mise à jour du total après chaque action HTMX
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        if (evt.detail.target.id === 'cart-content' || 
            evt.detail.target.closest('#cart-content')) {
            updateCartTotal();
        }
    });
}); 