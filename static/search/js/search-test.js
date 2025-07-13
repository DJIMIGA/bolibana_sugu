/**
 * Script de test pour le système de suggestions de recherche
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 Système de suggestions de recherche initialisé');
    
    // Test des éléments de recherche
    const searchInputs = document.querySelectorAll('input[id*="search"]');
    console.log(`📝 ${searchInputs.length} champs de recherche trouvés`);
    
    // Test des conteneurs de résultats
    const resultsContainers = document.querySelectorAll('#results-desktop, #searchResults');
    console.log(`📦 ${resultsContainers.length} conteneurs de résultats trouvés`);
    
    // Fonction de test des suggestions
    function testSuggestions() {
        const suggestions = document.querySelectorAll('.suggestion-item');
        console.log(`💡 ${suggestions.length} suggestions trouvées`);
        
        suggestions.forEach((suggestion, index) => {
            const text = suggestion.querySelector('.text-sm')?.textContent || 'N/A';
            const url = suggestion.getAttribute('href') || 'N/A';
            console.log(`  ${index + 1}. "${text}" → ${url}`);
        });
    }
    
    // Écouter les événements HTMX pour tester les suggestions
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.elt.id && evt.detail.elt.id.includes('search')) {
            console.log('🔄 Requête de recherche terminée');
            setTimeout(testSuggestions, 100);
        }
    });
    
    // Test de la navigation clavier
    document.addEventListener('keydown', function(e) {
        if (e.key === 'F12') {
            e.preventDefault();
            console.log('🧪 Test de navigation clavier activé');
            const searchInput = document.querySelector('#search-input-desktop, #searchInput');
            if (searchInput) {
                searchInput.focus();
                searchInput.value = 'test';
                searchInput.dispatchEvent(new Event('input'));
            }
        }
        
        // Test des suggestions (F11)
        if (e.key === 'F11') {
            e.preventDefault();
            console.log('🧪 Test des suggestions activé');
            const searchInput = document.querySelector('#search-input-desktop, #searchInput');
            if (searchInput) {
                searchInput.focus();
                searchInput.value = 'iphone';
                searchInput.dispatchEvent(new Event('input'));
            }
        }
    });
    
    // Afficher les informations de test
    console.log('✅ Système de test prêt');
    console.log('💡 Appuyez sur F12 pour tester la navigation');
    console.log('🔍 Tapez dans un champ de recherche pour voir les suggestions');
    console.log('🧪 Appuyez sur F11 pour tester les suggestions');
    console.log('📱 Test de responsive design activé');
    
    // Test de débordement des cartes
    function testCardOverflow() {
        const cards = document.querySelectorAll('.product-card-wrapper');
        console.log(`📦 ${cards.length} cartes de produits trouvées`);
        
        cards.forEach((card, index) => {
            const cardRect = card.getBoundingClientRect();
            const containerRect = card.parentElement.getBoundingClientRect();
            
            if (cardRect.width > containerRect.width) {
                console.warn(`⚠️ Carte ${index + 1} déborde: ${cardRect.width}px > ${containerRect.width}px`);
            } else {
                console.log(`✅ Carte ${index + 1} OK: ${cardRect.width}px <= ${containerRect.width}px`);
            }
        });
    }
    
    // Test de débordement au chargement
    window.addEventListener('load', testCardOverflow);
    
    // Test de débordement au redimensionnement
    window.addEventListener('resize', testCardOverflow);
}); 