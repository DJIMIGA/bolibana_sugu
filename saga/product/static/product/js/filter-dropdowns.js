/**
 * Gestionnaire pour les menus déroulants avec scroll
 * Améliore l'expérience utilisateur des filtres
 */

class FilterDropdownManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupScrollIndicators();
        this.setupKeyboardNavigation();
        this.setupTouchScrolling();
        this.optimizePerformance();
    }

    /**
     * Configure les indicateurs visuels pour les sections avec scroll
     */
    setupScrollIndicators() {
        const scrollableSections = document.querySelectorAll('.mobile-filter-section, .filter-dropdown-container');
        
        scrollableSections.forEach(section => {
            this.addScrollIndicator(section);
            
            // Vérifier si le contenu dépasse
            this.checkOverflow(section);
            
            // Écouter les changements de contenu
            const observer = new MutationObserver(() => {
                this.checkOverflow(section);
            });
            
            observer.observe(section, {
                childList: true,
                subtree: true
            });
        });
    }

    /**
     * Ajoute un indicateur visuel pour les sections avec scroll
     */
    addScrollIndicator(section) {
        if (!section.classList.contains('filter-section-indicator')) {
            section.classList.add('filter-section-indicator');
        }
    }

    /**
     * Vérifie si une section a du contenu qui dépasse
     */
    checkOverflow(section) {
        const hasOverflow = section.scrollHeight > section.clientHeight;
        
        if (hasOverflow) {
            section.classList.add('has-overflow');
        } else {
            section.classList.remove('has-overflow');
        }
    }

    /**
     * Configure la navigation au clavier pour les filtres
     */
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            const activeElement = document.activeElement;
            
            if (activeElement.classList.contains('filter-option') || 
                activeElement.closest('.mobile-filter-section')) {
                
                switch(e.key) {
                    case 'ArrowDown':
                        e.preventDefault();
                        this.navigateNext(activeElement);
                        break;
                    case 'ArrowUp':
                        e.preventDefault();
                        this.navigatePrevious(activeElement);
                        break;
                    case 'Enter':
                    case ' ':
                        e.preventDefault();
                        this.selectOption(activeElement);
                        break;
                    case 'Escape':
                        this.closeDropdown(activeElement);
                        break;
                }
            }
        });
    }

    /**
     * Navigation vers l'option suivante
     */
    navigateNext(currentElement) {
        const container = currentElement.closest('.mobile-filter-section, .filter-dropdown-container');
        const options = container.querySelectorAll('.filter-option, input[type="radio"]');
        const currentIndex = Array.from(options).indexOf(currentElement);
        const nextIndex = (currentIndex + 1) % options.length;
        
        options[nextIndex].focus();
        this.scrollToElement(options[nextIndex], container);
    }

    /**
     * Navigation vers l'option précédente
     */
    navigatePrevious(currentElement) {
        const container = currentElement.closest('.mobile-filter-section, .filter-dropdown-container');
        const options = container.querySelectorAll('.filter-option, input[type="radio"]');
        const currentIndex = Array.from(options).indexOf(currentElement);
        const prevIndex = currentIndex === 0 ? options.length - 1 : currentIndex - 1;
        
        options[prevIndex].focus();
        this.scrollToElement(options[prevIndex], container);
    }

    /**
     * Fait défiler vers un élément dans le conteneur
     */
    scrollToElement(element, container) {
        const elementRect = element.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        
        if (elementRect.bottom > containerRect.bottom) {
            container.scrollTop += elementRect.bottom - containerRect.bottom + 10;
        } else if (elementRect.top < containerRect.top) {
            container.scrollTop -= containerRect.top - elementRect.top + 10;
        }
    }

    /**
     * Sélectionne une option
     */
    selectOption(element) {
        if (element.tagName === 'INPUT') {
            element.checked = true;
            element.dispatchEvent(new Event('change', { bubbles: true }));
        } else if (element.tagName === 'A') {
            element.click();
        }
    }

    /**
     * Ferme le dropdown
     */
    closeDropdown(element) {
        const dropdown = element.closest('.filter-dropdown-container, .mobile-filter-section');
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    }

    /**
     * Configure le scroll tactile pour mobile
     */
    setupTouchScrolling() {
        const scrollableElements = document.querySelectorAll('.mobile-filter-section, .filter-dropdown-container');
        
        scrollableElements.forEach(element => {
            let isScrolling = false;
            let startY = 0;
            let startScrollTop = 0;

            element.addEventListener('touchstart', (e) => {
                startY = e.touches[0].clientY;
                startScrollTop = element.scrollTop;
                isScrolling = true;
            }, { passive: true });

            element.addEventListener('touchmove', (e) => {
                if (!isScrolling) return;
                
                const currentY = e.touches[0].clientY;
                const diff = startY - currentY;
                element.scrollTop = startScrollTop + diff;
                
                e.preventDefault();
            }, { passive: false });

            element.addEventListener('touchend', () => {
                isScrolling = false;
            }, { passive: true });
        });
    }

    /**
     * Optimise les performances pour les grandes listes
     */
    optimizePerformance() {
        // Utiliser Intersection Observer pour les éléments visibles
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, {
            threshold: 0.1
        });

        // Observer les options de filtres
        document.querySelectorAll('.filter-option').forEach(option => {
            observer.observe(option);
        });

        // Debounce pour les événements de scroll
        let scrollTimeout;
        document.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                this.updateScrollIndicators();
            }, 100);
        }, { passive: true });
    }

    /**
     * Met à jour les indicateurs de scroll
     */
    updateScrollIndicators() {
        const scrollableSections = document.querySelectorAll('.filter-section-indicator');
        
        scrollableSections.forEach(section => {
            const isAtTop = section.scrollTop === 0;
            const isAtBottom = section.scrollTop + section.clientHeight >= section.scrollHeight;
            
            section.classList.toggle('at-top', isAtTop);
            section.classList.toggle('at-bottom', isAtBottom);
        });
    }

    /**
     * Ouvre une section de filtre avec animation
     */
    static openSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.remove('collapsed');
            section.classList.add('expanded');
            
            // Focus sur le premier élément interactif
            const firstInteractive = section.querySelector('input, button, a');
            if (firstInteractive) {
                setTimeout(() => firstInteractive.focus(), 300);
            }
        }
    }

    /**
     * Ferme une section de filtre avec animation
     */
    static closeSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.remove('expanded');
            section.classList.add('collapsed');
        }
    }

    /**
     * Recherche dans les options de filtres
     */
    static searchInFilters(searchTerm, containerSelector) {
        const container = document.querySelector(containerSelector);
        if (!container) return;

        const options = container.querySelectorAll('.filter-option, input[type="radio"]');
        const searchLower = searchTerm.toLowerCase();

        options.forEach(option => {
            const text = option.textContent || option.value || '';
            const matches = text.toLowerCase().includes(searchLower);
            
            if (option.tagName === 'INPUT') {
                option.closest('.flex').style.display = matches ? 'flex' : 'none';
            } else {
                option.style.display = matches ? 'block' : 'none';
            }
        });
    }
}

// Initialisation automatique
document.addEventListener('DOMContentLoaded', () => {
    window.filterDropdownManager = new FilterDropdownManager();
});

// Export pour utilisation dans d'autres modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FilterDropdownManager;
} 