document.addEventListener('DOMContentLoaded', function() {
    const searchToggle = document.getElementById('searchToggle');
    const searchModal = document.getElementById('searchModal');
    const closeSearch = document.getElementById('closeSearch');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');

    if (!searchToggle || !searchModal || !closeSearch || !searchInput) {
        console.log('Éléments de recherche mobile non trouvés');
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
        
        // Scroll vers le haut des résultats
        if (searchResults) {
            searchResults.scrollTop = 0;
        }
    }

    closeSearch.addEventListener('click', closeSearchModal);

    // Fermer avec la touche Escape
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && !searchModal.classList.contains('hidden')) {
            closeSearchModal();
        }
    });

    // Gérer les résultats HTMX
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.elt.id === 'searchInput') {
            // Utiliser les utilitaires de recherche
            if (window.SearchUtils && searchResults) {
                window.SearchUtils.handleSearchResults(searchResults, searchInput);
            }
        }
    });

    // Gérer le clic en dehors du modal pour fermer
    searchModal.addEventListener('click', function(e) {
        if (e.target === searchModal) {
            closeSearchModal();
        }
    });
});
