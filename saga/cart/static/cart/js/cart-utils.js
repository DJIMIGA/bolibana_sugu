// Utilitaires partagés pour le panier
export const updateCartCount = () => {
    const cartCount = document.getElementById('cart-count');
    const cartItems = document.querySelectorAll('#cart-content .cart-item');
    
    if (cartCount) {
        const itemCount = cartItems.length;
        cartCount.textContent = itemCount;
        cartCount.classList.toggle('hidden', itemCount === 0);
    }
};

export const formatPrice = (price) => {
    return `${price.toLocaleString()} FCFA`;
}; 