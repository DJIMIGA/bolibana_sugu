/**
 * Gestionnaire pour les suggestions de recherche
 */

document.addEventListener('DOMContentLoaded', function() {
    // Gérer les clics sur les suggestions
    document.body.addEventListener('click', function(e) {
        const suggestionItem = e.target.closest('.suggestion-item');
        if (suggestionItem) {
            e.preventDefault();
            
            const url = suggestionItem.getAttribute('href');
            const suggestionText = suggestionItem.querySelector('.text-sm')?.textContent || '';
            
            if (url) {
                // Ajouter une animation de clic
                suggestionItem.style.transform = 'scale(0.95)';
                
                // Remplir le champ de recherche avec le texte de la suggestion
                const searchInput = document.querySelector('#search-input-desktop, #searchInput');
                if (searchInput) {
                    searchInput.value = suggestionText;
                }
                
                setTimeout(() => {
                    // Rediriger vers la page de résultats
                    window.location.href = url;
                }, 150);
            }
        }
    });

    // Gérer la navigation au clavier dans les suggestions
    document.body.addEventListener('keydown', function(e) {
        const searchInput = document.activeElement;
        const resultsContainer = document.querySelector('#results-desktop, #searchResults');
        
        if (!searchInput || !resultsContainer || !searchInput.id.includes('search')) {
            return;
        }
        
        const suggestions = resultsContainer.querySelectorAll('.suggestion-item');
        const currentIndex = Array.from(suggestions).findIndex(item => item.classList.contains('focused'));
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                navigateSuggestions(suggestions, currentIndex, 1);
                break;
            case 'ArrowUp':
                e.preventDefault();
                navigateSuggestions(suggestions, currentIndex, -1);
                break;
            case 'Enter':
                e.preventDefault();
                const focusedSuggestion = resultsContainer.querySelector('.suggestion-item.focused');
                if (focusedSuggestion) {
                    const url = focusedSuggestion.getAttribute('href');
                    const suggestionText = focusedSuggestion.querySelector('.text-sm')?.textContent || '';
                    
                    if (url) {
                        // Remplir le champ de recherche avec le texte de la suggestion
                        if (searchInput) {
                            searchInput.value = suggestionText;
                        }
                        
                        window.location.href = url;
                    }
                }
                break;
            case 'Escape':
                e.preventDefault();
                resultsContainer.classList.add('hidden');
                searchInput.blur();
                break;
        }
    });

    // Fonction pour naviguer dans les suggestions
    function navigateSuggestions(suggestions, currentIndex, direction) {
        if (suggestions.length === 0) return;
        
        // Retirer le focus actuel
        suggestions.forEach(item => item.classList.remove('focused'));
        
        let newIndex;
        if (currentIndex === -1) {
            newIndex = direction > 0 ? 0 : suggestions.length - 1;
        } else {
            newIndex = (currentIndex + direction + suggestions.length) % suggestions.length;
        }
        
        // Ajouter le focus au nouvel élément
        suggestions[newIndex].classList.add('focused');
        suggestions[newIndex].scrollIntoView({ block: 'nearest' });
    }

    // Gérer le survol des suggestions
    document.body.addEventListener('mouseenter', function(e) {
        const suggestionItem = e.target.closest('.suggestion-item');
        if (suggestionItem) {
            // Retirer le focus clavier lors du survol
            document.querySelectorAll('.suggestion-item').forEach(item => {
                item.classList.remove('focused');
            });
            
            // Optionnel : prévisualiser le texte dans le champ de recherche
            const suggestionText = suggestionItem.querySelector('.text-sm')?.textContent || '';
            const searchInput = document.querySelector('#search-input-desktop, #searchInput');
            if (searchInput && suggestionText) {
                // Créer un effet de prévisualisation temporaire
                searchInput.setAttribute('data-preview', suggestionText);
                searchInput.style.color = '#6b7280'; // Gris pour indiquer la prévisualisation
            }
        }
    }, true);

    // Gérer la sortie du survol
    document.body.addEventListener('mouseleave', function(e) {
        const suggestionItem = e.target.closest('.suggestion-item');
        if (suggestionItem) {
            const searchInput = document.querySelector('#search-input-desktop, #searchInput');
            if (searchInput) {
                // Restaurer la couleur normale
                searchInput.style.color = '';
                searchInput.removeAttribute('data-preview');
            }
        }
    }, true);

    // Améliorer l'accessibilité
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.elt.id && evt.detail.elt.id.includes('search')) {
            const resultsContainer = evt.detail.target;
            const suggestions = resultsContainer.querySelectorAll('.suggestion-item');
            
            // Ajouter les attributs d'accessibilité
            suggestions.forEach((item, index) => {
                item.setAttribute('role', 'button');
                item.setAttribute('tabindex', '0');
                item.setAttribute('aria-label', `Suggestion ${index + 1}: ${item.querySelector('.text-sm').textContent}`);
            });
        }
    });
}); 