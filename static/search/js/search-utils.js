/**
 * Utilitaires pour la fonctionnalité de recherche
 */

// Fonction pour scroll vers le haut des résultats
function scrollToTop(container) {
    if (container && container.scrollTop !== undefined) {
        container.scrollTop = 0;
    }
}

// Fonction pour vérifier si un élément est visible dans le viewport
function isElementInViewport(el) {
    if (!el) return false;
    
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// Fonction pour gérer le scroll automatique vers un élément
function scrollToElement(element, offset = 0) {
    if (!element) return;
    
    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;
    
    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}

// Fonction pour détecter si l'utilisateur est sur mobile
function isMobile() {
    return window.innerWidth <= 768;
}

// Fonction pour optimiser le scroll sur mobile
function optimizeMobileScroll(container) {
    if (!isMobile() || !container) return;
    
    // Ajouter une classe pour optimiser le scroll sur mobile
    container.classList.add('mobile-scroll-optimized');
    
    // Désactiver le scroll horizontal sur mobile
    container.style.overflowX = 'hidden';
}

// Fonction pour gérer les résultats de recherche
function handleSearchResults(resultsContainer, searchInput) {
    if (!resultsContainer || !searchInput) return;
    
    // Scroll vers le haut des résultats
    scrollToTop(resultsContainer);
    
    // Optimiser le scroll sur mobile
    optimizeMobileScroll(resultsContainer);
    
    // Ajouter une classe pour l'animation
    resultsContainer.classList.add('search-results-loaded');
    
    // Retirer la classe après l'animation
    setTimeout(() => {
        resultsContainer.classList.remove('search-results-loaded');
    }, 300);
}

// Fonction pour gérer les erreurs de recherche
function handleSearchError(error) {
    console.error('Erreur de recherche:', error);
    
    // Afficher un message d'erreur à l'utilisateur
    const errorMessage = document.createElement('div');
    errorMessage.className = 'search-error-message';
    errorMessage.innerHTML = `
        <div class="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
            <div class="w-8 h-8 mx-auto mb-2 text-red-500">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
            </div>
            <p class="text-red-700 text-sm">Une erreur s'est produite lors de la recherche. Veuillez réessayer.</p>
        </div>
    `;
    
    return errorMessage;
}

// Export des fonctions pour utilisation dans d'autres scripts
window.SearchUtils = {
    scrollToTop,
    isElementInViewport,
    scrollToElement,
    isMobile,
    optimizeMobileScroll,
    handleSearchResults,
    handleSearchError
}; 