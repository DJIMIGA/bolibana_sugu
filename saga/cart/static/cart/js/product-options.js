export default class ProductOptions {
    constructor() {
        this.sidebar = document.getElementById('product-options-sidebar');
        this.overlay = document.getElementById('product-options-overlay');
        this.container = document.getElementById('product-options-container');
        
        this.init();
    }

    init() {
        // Gestionnaire d'événements pour les requêtes HTMX
        document.addEventListener('htmx:afterRequest', this.handleHtmxResponse.bind(this));
        
        // Fermeture avec Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.close();
        });

        // Fermeture en cliquant sur l'overlay
        this.overlay?.addEventListener('click', () => this.close());

        // Gestion des formulaires dynamiques
        document.body.addEventListener('htmx:afterSwap', this.handleFormSwap.bind(this));
    }

    open(productId) {
        this.sidebar?.classList.remove('pointer-events-none');
        this.overlay?.classList.remove('opacity-0', 'pointer-events-none');
        this.container?.classList.remove('translate-x-full');
        document.body.style.overflow = 'hidden';

        // Utiliser le chemin complet avec le préfixe /cart/
        htmx.ajax('GET', `/cart/product-options/${productId}/`, {
            target: '#product-options-content',
            swap: 'innerHTML',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
    }

    close() {
        this.overlay?.classList.add('opacity-0', 'pointer-events-none');
        this.container?.classList.add('translate-x-full');
        
        setTimeout(() => {
            this.sidebar?.classList.add('pointer-events-none');
            document.body.style.overflow = '';
        }, 500);
    }

    handleHtmxResponse(evt) {
        // Options produit chargées
    }

    handleFormSwap(e) {
        if (e.detail.target.id === 'product-options-content') {
            const form = e.detail.target.querySelector('form');
            if (form) {
                form.addEventListener('htmx:afterRequest', (e) => {
                    if (e.detail.successful) {
                        setTimeout(() => this.close(), 500);
                    }
                });
            }
        }
    }
}

// Initialiser et exposer globalement
window.productOptions = new ProductOptions();
window.openProductOptions = (productId) => window.productOptions.open(productId);
window.closeProductOptions = () => window.productOptions.close(); 