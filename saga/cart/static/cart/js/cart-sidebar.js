import { updateCartCount } from './cart-utils.js';
import Swal from 'sweetalert2';

class CartSidebar {
    constructor() {
        this.sidebar = document.getElementById('cart-sidebar');
        this.overlay = document.getElementById('cart-overlay');
        this.container = document.getElementById('cart-container');
        this.closeButton = document.getElementById('closeCartButton');

        if (!this.sidebar || !this.overlay || !this.container || !this.closeButton) {
            console.error('[Cart] ⚠️ Éléments manquants');
            return;
        }

        this.isMobile = window.innerWidth < 1024; // lg breakpoint
        this.bindEvents();
        this.bindResize();
    }

    bindEvents() {
        this.closeButton.addEventListener('click', () => {
            this.close();
        });
        
        this.overlay.addEventListener('click', () => {
            this.close();
        });
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.close();
            }
        });
    }

    bindResize() {
        window.addEventListener('resize', () => {
            this.isMobile = window.innerWidth < 1024;
            if (this.isOpen) {
                this.open(); // Réappliquer les classes appropriées
            }
        });
    }

    open() {
        this.isOpen = true;
        
        // Activer les interactions
        this.sidebar.classList.remove('pointer-events-none');
        
        if (!this.isMobile) {
            // Overlay uniquement sur desktop
            this.overlay.classList.remove('opacity-0');
            this.overlay.classList.add('opacity-100');
        }
        
        // Animation du container
        this.container.classList.remove('translate-x-full');
        this.container.classList.add('translate-x-0');
        
        document.body.style.overflow = 'hidden';
    }

    close() {
        this.isOpen = false;
        
        // Désactiver les interactions
        if (!this.isMobile) {
            this.overlay.classList.remove('opacity-100');
            this.overlay.classList.add('opacity-0');
        }
        
        this.container.classList.remove('translate-x-0');
        this.container.classList.add('translate-x-full');
        
        setTimeout(() => {
            this.sidebar.classList.add('pointer-events-none');
            document.body.style.overflow = '';
        }, 500);
    }
}

let cartSidebarInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    cartSidebarInstance = new CartSidebar();
});

window.openCart = () => {
    if (!cartSidebarInstance) {
        console.error('[Cart] ⚠️ Instance non initialisée');
        return;
    }
    cartSidebarInstance.open();
};

// Fonction pour afficher l'animation d'ajout au panier
window.showAddToCartAnimation = (productName) => {
    window.showNotification.addToCart(productName);
};

window.closeCart = () => {
    cartSidebarInstance?.close();
};

export default CartSidebar; 