/**
 * Autocomplétion des produits pour le formulaire de soumission de prix
 */
class ProductAutocomplete {
    constructor() {
        this.searchInput = document.getElementById('product-search');
        this.productIdInput = document.getElementById('product-id');
        this.resultsContainer = null;
        this.debounceTimer = null;
        this.selectedIndex = -1;
        
        if (this.searchInput) {
            this.init();
        }
    }
    
    init() {
        // Créer le conteneur des résultats
        this.createResultsContainer();
        
        // Événements
        this.searchInput.addEventListener('input', (e) => this.handleInput(e));
        this.searchInput.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.searchInput.addEventListener('focus', () => this.showResults());
        this.searchInput.addEventListener('blur', () => this.hideResults());
        
        // Fermer les résultats en cliquant ailleurs
        document.addEventListener('click', (e) => {
            if (!this.searchInput.contains(e.target) && !this.resultsContainer.contains(e.target)) {
                this.hideResults();
            }
        });
    }
    
    createResultsContainer() {
        this.resultsContainer = document.createElement('div');
        this.resultsContainer.className = 'absolute z-50 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto hidden';
        this.resultsContainer.id = 'product-results';
        
        // Insérer après le champ de recherche
        this.searchInput.parentNode.style.position = 'relative';
        this.searchInput.parentNode.appendChild(this.resultsContainer);
    }
    
    handleInput(e) {
        const query = e.target.value.trim();
        
        // Réinitialiser l'index sélectionné
        this.selectedIndex = -1;
        
        // Effacer le timer précédent
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        // Masquer les résultats si la requête est trop courte
        if (query.length < 2) {
            this.hideResults();
            this.clearProductId();
            return;
        }
        
        // Débouncer la requête
        this.debounceTimer = setTimeout(() => {
            this.searchProducts(query);
        }, 300);
    }
    
    handleKeydown(e) {
        const results = this.resultsContainer.querySelectorAll('.product-result-item');
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, results.length - 1);
                this.updateSelection(results);
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelection(results);
                break;
                
            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0 && results[this.selectedIndex]) {
                    this.selectProduct(results[this.selectedIndex]);
                }
                break;
                
            case 'Escape':
                this.hideResults();
                break;
        }
    }
    
    updateSelection(results) {
        results.forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.classList.add('bg-green-50', 'border-green-200');
                item.classList.remove('hover:bg-gray-50');
            } else {
                item.classList.remove('bg-green-50', 'border-green-200');
                item.classList.add('hover:bg-gray-50');
            }
        });
    }
    
    async searchProducts(query) {
        try {
            const response = await fetch(`/price-checker/api/product-autocomplete/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            this.displayResults(data.results);
        } catch (error) {
            console.error('Erreur lors de la recherche:', error);
            this.displayError();
        }
    }
    
    displayResults(results) {
        if (results.length === 0) {
            this.resultsContainer.innerHTML = `
                <div class="p-4 text-center text-gray-500">
                    <svg class="mx-auto h-8 w-8 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                    </svg>
                    <p>Aucun produit trouvé</p>
                </div>
            `;
        } else {
            this.resultsContainer.innerHTML = results.map((product, index) => `
                <div class="product-result-item cursor-pointer p-3 border-b border-gray-100 hover:bg-gray-50 transition-colors duration-150 ${index === 0 ? 'rounded-t-lg' : ''} ${index === results.length - 1 ? 'rounded-b-lg border-b-0' : ''}" 
                     data-product-id="${product.id}" 
                     data-product-title="${product.title}">
                    <div class="flex items-center justify-between">
                        <div class="flex-1">
                            <div class="font-medium text-gray-900">${product.title}</div>
                            <div class="text-sm text-gray-500">${product.category} • ${product.supplier}</div>
                        </div>
                        <div class="ml-2">
                            <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                            </svg>
                        </div>
                    </div>
                </div>
            `).join('');
            
            // Ajouter les événements de clic
            this.resultsContainer.querySelectorAll('.product-result-item').forEach(item => {
                item.addEventListener('click', () => this.selectProduct(item));
            });
        }
        
        this.showResults();
    }
    
    displayError() {
        this.resultsContainer.innerHTML = `
            <div class="p-4 text-center text-red-500">
                <svg class="mx-auto h-8 w-8 text-red-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <p>Erreur lors de la recherche</p>
            </div>
        `;
        this.showResults();
    }
    
    selectProduct(item) {
        const productId = item.dataset.productId;
        const productTitle = item.dataset.productTitle;
        
        // Mettre à jour les champs
        this.searchInput.value = productTitle;
        this.productIdInput.value = productId;
        
        // Ajouter une classe pour indiquer la sélection
        this.searchInput.classList.add('border-green-500', 'ring-2', 'ring-green-200');
        
        // Masquer les résultats
        this.hideResults();
        
        // Déclencher un événement personnalisé
        this.searchInput.dispatchEvent(new CustomEvent('productSelected', {
            detail: { productId, productTitle }
        }));
    }
    
    clearProductId() {
        this.productIdInput.value = '';
        this.searchInput.classList.remove('border-green-500', 'ring-2', 'ring-green-200');
    }
    
    showResults() {
        this.resultsContainer.classList.remove('hidden');
    }
    
    hideResults() {
        // Délai pour permettre le clic sur les résultats
        setTimeout(() => {
            this.resultsContainer.classList.add('hidden');
        }, 150);
    }
}

// Initialiser l'autocomplétion quand le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
    new ProductAutocomplete();
}); 