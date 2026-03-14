import { formatPrice } from './cart-utils.js';

class CartTotal {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        document.addEventListener('cart:quantityChanged', () => this.update());
        document.body.addEventListener('htmx:afterSwap', (evt) => {
            if (evt.detail.target.id === 'cart-content' || 
                evt.detail.target.closest('#cart-content')) {
                this.update();
            }
        });
    }

    update() {
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
            totalElement.textContent = formatPrice(total);
        }
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    new CartTotal();
}); 