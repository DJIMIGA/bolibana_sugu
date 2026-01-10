/**
 * Gestion du bouton de profil mobile
 * Fonctionnalités :
 * - Ouverture/fermeture du menu
 * - Animation du menu
 */

document.addEventListener('DOMContentLoaded', () => {
    const profileButton = document.getElementById('profileButtonMobile');
    const profileMenu = document.getElementById('profileMenuMobile');

    if (!profileButton || !profileMenu) {
        return;
    }

    function openMenu() {
        profileMenu.classList.remove('hidden');
        // Force un reflow pour que l'animation fonctionne
        void profileMenu.offsetWidth;
        profileMenu.classList.remove('opacity-0', 'scale-95');
        profileMenu.classList.add('opacity-100', 'scale-100');
    }

    function closeMenu() {
        profileMenu.classList.remove('opacity-100', 'scale-100');
        profileMenu.classList.add('opacity-0', 'scale-95');
        setTimeout(() => {
            profileMenu.classList.add('hidden');
        }, 300);
    }

    // Gestion du clic sur le bouton
    profileButton.addEventListener('click', (e) => {
        e.stopPropagation();
        if (profileMenu.classList.contains('hidden')) {
            openMenu();
        } else {
            closeMenu();
        }
    });

    // Fermer le menu en cliquant en dehors
    document.addEventListener('click', (e) => {
        if (!profileMenu.contains(e.target) && !profileButton.contains(e.target)) {
            closeMenu();
        }
    });

    // Fermer le menu avec la touche Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !profileMenu.classList.contains('hidden')) {
            closeMenu();
        }
    });

    // Empêcher la propagation des événements dans le menu
    profileMenu.addEventListener('click', (e) => {
        e.stopPropagation();
    });
}); 