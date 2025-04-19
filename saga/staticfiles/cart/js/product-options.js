document.addEventListener("DOMContentLoaded", () => {
    const productOptionsSidebar = document.getElementById("product-options-sidebar");
    const closeOptionsButton = document.getElementById("closeOptionsButton");
    const optionsContent = productOptionsSidebar?.querySelector('.transform');
    const body = document.body;

    if (!productOptionsSidebar || !closeOptionsButton || !optionsContent) {
        console.error("Un ou plusieurs éléments des options n'ont pas été trouvés");
        return;
    }

    window.openProductOptions = () => {
        productOptionsSidebar.classList.remove("hidden");
        optionsContent.classList.remove("translate-x-full");
        body.style.overflow = "hidden";
        
        // Fermer le panier s'il est ouvert
        const cartSidebar = document.getElementById("cart-sidebar");
        if (cartSidebar && !cartSidebar.classList.contains("hidden")) {
            const cartContent = cartSidebar.querySelector('.transform');
            cartSidebar.classList.add("hidden");
            cartContent?.classList.add("translate-x-full");
        }
    };

    const closeProductOptions = () => {
        optionsContent.classList.add("translate-x-full");
        setTimeout(() => {
            productOptionsSidebar.classList.add("hidden");
            body.style.overflow = "";
        }, 300);
    };

    closeOptionsButton.addEventListener("click", closeProductOptions);

    // Fermer les options si l'utilisateur clique à l'extérieur
    productOptionsSidebar.addEventListener("click", (event) => {
        if (event.target === productOptionsSidebar) {
            closeProductOptions();
        }
    });

    // Fermer les options avec la touche Échap
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && !productOptionsSidebar.classList.contains('hidden')) {
            closeProductOptions();
        }
    });
}); 