document.addEventListener('DOMContentLoaded', function() {
    const searchToggle = document.getElementById('searchToggle');
    const searchModal = document.getElementById('searchModal');
    const closeSearch = document.getElementById('closeSearch');
    const searchInput = document.getElementById('searchInput');

    if (!searchToggle || !searchModal || !closeSearch || !searchInput) {
        console.log('Éléments de recherche non trouvés');
        return;
    }

    // Ouvrir la recherche
    searchToggle.addEventListener('click', function() {
        searchModal.classList.remove('hidden');
        searchInput.focus();
        document.body.style.overflow = 'hidden';
    });

    // Fermer la recherche
    function closeSearchModal() {
        searchModal.classList.add('hidden');
        searchInput.value = '';
        document.body.style.overflow = '';
    }

    closeSearch.addEventListener('click', closeSearchModal);

    // Fermer avec la touche Escape
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && !searchModal.classList.contains('hidden')) {
            closeSearchModal();
        }
    });
});
