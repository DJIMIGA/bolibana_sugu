document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input-desktop');
    const resultsContainer = document.getElementById('results-desktop');
    const form = document.getElementById('form-desktop');

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
            } else {
                resultsContainer.classList.add('hidden');
            }
        }
    });
}); 