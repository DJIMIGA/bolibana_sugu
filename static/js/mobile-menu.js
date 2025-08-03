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
        // Fermer le menu mobile principal
        mobileMenu.classList.remove('translate-x-0');
        mobileMenu.classList.add('-translate-x-full');
        document.body.classList.remove('overflow-hidden');
        
        // Réinitialiser complètement le menu des sous-catégories
        if (subcategoriesMenu) {
            subcategoriesMenu.classList.remove('translate-x-0');
            subcategoriesMenu.classList.add('translate-x-full');
            
            // Vider le contenu du menu des sous-catégories
            subcategoriesMenu.innerHTML = '';
        }
    }

    // Gestion des événements HTMX
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        if (evt.detail.target.id === 'subcategoriesMenu') {
            const subcategoriesMenu = document.getElementById('subcategoriesMenu');
            if (subcategoriesMenu) {
                // Vérifier le contenu chargé pour déterminer l'action
                const categoryTitle = subcategoriesMenu.querySelector('h2');
                
                if (categoryTitle) {
                    const titleText = categoryTitle.textContent.trim();
                    
                    if (titleText === 'Catégories') {
                        // On revient à l'arbre principal des catégories
                        // Afficher le menu des sous-catégories (première fois)
                        subcategoriesMenu.classList.remove('translate-x-full');
                        subcategoriesMenu.classList.add('translate-x-0');
                    } else {
                        // On navigue vers une sous-catégorie ou marque
                        // Garder le menu des sous-catégories visible
                        subcategoriesMenu.classList.remove('translate-x-full');
                        subcategoriesMenu.classList.add('translate-x-0');
                    }
                } else {
                    // Pas de titre trouvé, afficher par sécurité
                    subcategoriesMenu.classList.remove('translate-x-full');
                    subcategoriesMenu.classList.add('translate-x-0');
                }
            }
        }
    });

    // Gestion des clics sur les boutons
    openMenuButton.addEventListener('click', (e) => {
        e.preventDefault();
        openMobileMenu();
    });

    closeMenuButton.addEventListener('click', (e) => {
        e.preventDefault();
        closeMobileMenu();
    });

    // Fermeture avec la touche Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeMobileMenu();
        }
    });

    // Rendre la fonction closeMobileMenu accessible globalement
    window.closeMobileMenu = closeMobileMenu;
    
    // Fonction pour fermer le menu des sous-catégories
    function closeSubcategoriesMenu() {
        if (subcategoriesMenu) {
            subcategoriesMenu.classList.remove('translate-x-0');
            subcategoriesMenu.classList.add('translate-x-full');
            subcategoriesMenu.innerHTML = '';
        }
    }
    
    // Rendre la fonction closeSubcategoriesMenu accessible globalement
    window.closeSubcategoriesMenu = closeSubcategoriesMenu;
}); 