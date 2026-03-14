import { updateCartCount, formatPrice } from './cart-utils.js';

class CartQuantity {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        document.body.addEventListener('htmx:afterSwap', (evt) => {
            if (evt.detail.target.closest('li')) {
                this.handleQuantityUpdate();
            }
        });

        document.body.addEventListener('htmx:responseError', (evt) => {
            const status = evt.detail?.xhr?.status || 'N/A';
            console.error(`[Cart] ❌ Erreur ${status} lors de la mise à jour`);
        });
    }

    handleQuantityUpdate() {
        updateCartCount();
        this.updateCartTotal();
    }

    updateCartTotal() {
        const event = new CustomEvent('cart:quantityChanged');
        document.dispatchEvent(event);
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    new CartQuantity();
}); 