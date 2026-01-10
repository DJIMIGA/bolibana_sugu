document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input-desktop');
    const resultsContainer = document.getElementById('results-desktop');
    const form = document.getElementById('form-desktop');

    if (!searchInput || !resultsContainer || !form) {
        return;
    }

    // Gérer la visibilité des résultats
    searchInput.addEventListener('focus', function() {
        if (this.value.trim() !== '') {
            resultsContainer.classList.remove('hidden');
        }
    });

    searchInput.addEventListener('blur', function() {
        // Petit délai pour permettre le clic sur les résultats
        setTimeout(() => {
            resultsContainer.classList.add('hidden');
        }, 200);
    });

    // Gérer la soumission du formulaire
    form.addEventListener('submit', function(e) {
        if (searchInput.value.trim() === '') {
            e.preventDefault();
        }
    });

    // Gérer les résultats HTMX
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.elt.id === 'search-input-desktop') {
            if (searchInput.value.trim() !== '') {
                resultsContainer.classList.remove('hidden');
                
                // Utiliser les utilitaires de recherche
                const resultsScrollContainer = resultsContainer.querySelector('.overflow-y-auto');
                if (window.SearchUtils && resultsScrollContainer) {
                    window.SearchUtils.handleSearchResults(resultsScrollContainer, searchInput);
                }
            } else {
                resultsContainer.classList.add('hidden');
            }
        }
    });

    // Gérer le clic en dehors pour fermer les résultats
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
            resultsContainer.classList.add('hidden');
        }
    });

    // Gérer les touches clavier
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            resultsContainer.classList.add('hidden');
            searchInput.blur();
        }
    });
}); 