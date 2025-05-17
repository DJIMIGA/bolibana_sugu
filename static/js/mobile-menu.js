/**
 * Gestion du menu mobile
 * Fonctionnalités :
 * - Ouverture/fermeture du menu
 * - Gestion des animations
 * - Gestion des événements clavier
 */

document.addEventListener('DOMContentLoaded', function() {
    const mobileMenu = document.getElementById('mobileMenu');
    const openMenuButton = document.getElementById('openMenuButton');
    const closeMenuButton = document.getElementById('closeMenuButton');
    const subcategoriesMenu = document.getElementById('subcategoriesMenu');

    if (!mobileMenu || !openMenuButton || !closeMenuButton) return;

    function openMobileMenu() {
        mobileMenu.classList.remove('-translate-x-full');
        mobileMenu.classList.add('translate-x-0');
        document.body.classList.add('overflow-hidden');
    }

    function closeMobileMenu() {
        mobileMenu.classList.remove('translate-x-0');
        mobileMenu.classList.add('-translate-x-full');
        document.body.classList.remove('overflow-hidden');
    }

    // Gestion des événements HTMX
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        if (evt.detail.target.id === 'subcategoriesMenu') {
            subcategoriesMenu.classList.remove('translate-x-full');
            subcategoriesMenu.classList.add('translate-x-0');
        }
    });

    openMenuButton.addEventListener('click', (e) => {
        e.preventDefault();
        openMobileMenu();
    });

    closeMenuButton.addEventListener('click', (e) => {
        e.preventDefault();
        closeMobileMenu();
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeMobileMenu();
            if (subcategoriesMenu) {
                subcategoriesMenu.classList.remove('translate-x-0');
                subcategoriesMenu.classList.add('translate-x-full');
            }
        }
    });
}); 