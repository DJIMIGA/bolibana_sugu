import { updateCartCount } from './cart-utils.js';

class CartSidebar {
    constructor() {
        console.log('CartSidebar: Initialisation...');
        
        this.sidebar = document.getElementById('cart-sidebar');
        this.overlay = document.getElementById('cart-overlay');
        this.container = document.getElementById('cart-container');
        this.closeButton = document.getElementById('closeCartButton');
        
        // Log des éléments trouvés
        console.log('CartSidebar: Éléments trouvés:', {
            sidebar: !!this.sidebar,
            overlay: !!this.overlay,
            container: !!this.container,
            closeButton: !!this.closeButton
        });

        if (!this.sidebar || !this.overlay || !this.container || !this.closeButton) {
            console.error('CartSidebar: Éléments manquants!');
            return;
        }

        // Initialiser l'overlay
        this.overlay.style.pointerEvents = 'none';
        this.overlay.classList.add('opacity-0');

        this.isMobile = window.innerWidth < 1024; // lg breakpoint
        this.bindEvents();
        this.bindResize();
        console.log('CartSidebar: Initialisation terminée');
    }

    bindEvents() {
        console.log('CartSidebar: Liaison des événements...');
        
        this.closeButton.addEventListener('click', () => {
            console.log('CartSidebar: Clic sur le bouton fermer');
            this.close();
        });
        
        this.overlay.addEventListener('click', () => {
            console.log('CartSidebar: Clic sur overlay');
            this.close();
        });
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                console.log('CartSidebar: Touche Escape pressée');
                this.close();
            }
        });

        console.log('CartSidebar: Événements liés');
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
        console.log('CartSidebar: Ouverture...');
        this.isOpen = true;
        
        // Activer les interactions
        this.sidebar.classList.remove('pointer-events-none');
        
        if (!this.isMobile) {
            // Overlay uniquement sur desktop
            this.overlay.classList.remove('opacity-0');
            this.overlay.classList.add('opacity-100');
            this.overlay.style.pointerEvents = 'auto';
        }
        
        // Animation du container
        this.container.classList.remove('translate-x-full');
        this.container.classList.add('translate-x-0');
        
        document.body.style.overflow = 'hidden';
    }

    close() {
        console.log('CartSidebar: Fermeture...');
        this.isOpen = false;
        
        // Désactiver les interactions
        if (!this.isMobile) {
            this.overlay.classList.remove('opacity-100');
            this.overlay.classList.add('opacity-0');
            this.overlay.style.pointerEvents = 'none';
        }
        
        this.container.classList.remove('translate-x-0');
        this.container.classList.add('translate-x-full');
        
        setTimeout(() => {
            this.sidebar.classList.add('pointer-events-none');
            document.body.style.overflow = '';
        }, 500);
    }
}

console.log('CartSidebar: Script chargé');

let cartSidebarInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    console.log('CartSidebar: DOM chargé, création de l\'instance');
    cartSidebarInstance = new CartSidebar();
});

window.openCart = () => {
    console.log('CartSidebar: Appel à openCart avec instance:', !!cartSidebarInstance);
    if (!cartSidebarInstance) {
        console.error('CartSidebar: Instance non initialisée');
        return;
    }
    cartSidebarInstance.open();
};

window.closeCart = () => {
    console.log('CartSidebar: Appel à closeCart');
    cartSidebarInstance?.close();
};

export default CartSidebar; 