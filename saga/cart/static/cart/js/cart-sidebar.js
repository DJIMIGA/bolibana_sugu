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

        this.bindEvents();
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

    open() {
        console.log('CartSidebar: Ouverture...');
        console.log('Classes avant ouverture:', {
            sidebar: this.sidebar.className,
            overlay: this.overlay.className,
            container: this.container.className
        });

        // Activer les interactions
        this.sidebar.classList.remove('pointer-events-none');
        this.overlay.classList.remove('opacity-0');
        this.overlay.classList.add('opacity-100');
        this.container.classList.remove('translate-x-full');
        this.container.classList.add('translate-x-0');
        document.body.style.overflow = 'hidden';

        console.log('Classes après ouverture:', {
            sidebar: this.sidebar.className,
            overlay: this.overlay.className,
            container: this.container.className
        });
    }

    close() {
        console.log('CartSidebar: Fermeture...');
        
        // Désactiver les interactions
        this.overlay.classList.remove('opacity-100');
        this.overlay.classList.add('opacity-0');
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