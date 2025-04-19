// onglet lateral pour le panier
document.addEventListener("DOMContentLoaded", () => {
    const openCartButton = document.getElementById("cart-button");
    const cartSidebar = document.getElementById("cart-sidebar");
    const closeCartButton = document.getElementById("closeCartButton");
    const cartContent = cartSidebar?.querySelector('.fixed');
    const body = document.body;

    if (!openCartButton || !cartSidebar || !closeCartButton || !cartContent) {
        console.error("Un ou plusieurs éléments du panier n'ont pas été trouvés");
        return;
    }

    const toggleCart = (open) => {
        cartSidebar.classList.toggle("hidden", !open);
        cartContent.classList.toggle("translate-x-full", !open);
        body.style.overflow = open ? "hidden" : "";
    };

    openCartButton.addEventListener("click", () => toggleCart(true));
    closeCartButton.addEventListener("click", () => toggleCart(false));

    // Fermer le panier si l'utilisateur clique à l'extérieur
    cartSidebar.addEventListener("click", (event) => {
        if (event.target === cartSidebar) {
            toggleCart(false);
        }
    });

    // Fermer le panier avec la touche Échap
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && !cartSidebar.classList.contains('hidden')) {
            toggleCart(false);
        }
    });
});

function openProductOptions() {
    const sidebar = document.getElementById('cart-sidebar');
    const cartContent = document.getElementById('cart-content');
    const optionsContent = document.getElementById('product-options-content');
    const cartTitle = document.getElementById('cart-title');
    const optionsTitle = document.getElementById('options-title');

    if (sidebar) {
        // Afficher la sidebar
        sidebar.classList.remove('hidden');
        sidebar.querySelector('.max-w-md').classList.remove('translate-x-full');
        
        // Basculer entre le contenu du panier et les options
        cartContent.classList.add('hidden');
        optionsContent.classList.remove('hidden');
        
        // Mettre à jour le titre
        cartTitle.classList.add('hidden');
        optionsTitle.classList.remove('hidden');
    }
}

function closeProductOptions() {
    const sidebar = document.getElementById('cart-sidebar');
    const cartContent = document.getElementById('cart-content');
    const optionsContent = document.getElementById('product-options-content');
    const cartTitle = document.getElementById('cart-title');
    const optionsTitle = document.getElementById('options-title');

    if (sidebar) {
        // Masquer la sidebar
        sidebar.querySelector('.max-w-md').classList.add('translate-x-full');
        setTimeout(() => {
            sidebar.classList.add('hidden');
            
            // Réinitialiser l'état
            cartContent.classList.remove('hidden');
            optionsContent.classList.add('hidden');
            cartTitle.classList.remove('hidden');
            optionsTitle.classList.add('hidden');
        }, 300);
    }
}

// Ajouter un gestionnaire pour fermer le sidebar
document.addEventListener('DOMContentLoaded', function() {
    const closeButtons = document.querySelectorAll('#closeCartButton, #cart-sidebar .bg-opacity-75');
    
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const cartSidebar = document.getElementById('cart-sidebar');
            const sidebarContent = cartSidebar.querySelector('.transform');
            
            sidebarContent.classList.add('translate-x-full');
            setTimeout(() => {
                cartSidebar.classList.add('hidden');
            }, 300);
        });
    });
});