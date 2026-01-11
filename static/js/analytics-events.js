/**
 * Script pour les événements d'engagement Google Analytics
 * Gère les événements côté client comme les clics, scrolls, etc.
 */

(function() {
    'use strict';
    
    // Vérifier si Google Analytics est disponible
    if (typeof gtag === 'undefined') {
        return;
    }
    
    // Initialisation des événements d'engagement Google Analytics
    
    // Configuration
    const SCROLL_THRESHOLDS = [25, 50, 75, 90]; // Pourcentages de scroll
    const ENGAGEMENT_TIMEOUT = 30000; // 30 secondes pour considérer l'engagement
    
    let scrollTracked = new Set();
    let engagementStartTime = Date.now();
    let engagementTracked = false;
    
    // Fonction utilitaire pour envoyer des événements
    function sendEvent(eventName, parameters = {}) {
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, {
                'event_category': 'engagement',
                'event_label': window.location.pathname,
                'page_title': document.title,
                ...parameters
            });
            console.log('📊 Événement envoyé:', eventName, parameters);
        }
    }
    
    // Tracking du scroll
    function trackScroll() {
        const scrollPercent = Math.round((window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100);
        
        SCROLL_THRESHOLDS.forEach(threshold => {
            if (scrollPercent >= threshold && !scrollTracked.has(threshold)) {
                scrollTracked.add(threshold);
                sendEvent('scroll', {
                    'scroll_percentage': threshold,
                    'scroll_depth': scrollPercent
                });
            }
        });
    }
    
    // Tracking de l'engagement (temps passé sur la page)
    function trackEngagement() {
        if (!engagementTracked) {
            const timeSpent = Math.round((Date.now() - engagementStartTime) / 1000);
            sendEvent('engagement', {
                'time_spent_seconds': timeSpent,
                'engagement_level': timeSpent > 60 ? 'high' : timeSpent > 30 ? 'medium' : 'low'
            });
            engagementTracked = true;
        }
    }
    
    // Tracking des clics sur les boutons importants
    function trackButtonClicks() {
        const buttons = document.querySelectorAll('button, .btn, [role="button"]');
        
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                const buttonText = this.textContent.trim() || this.getAttribute('aria-label') || 'Unknown';
                const buttonClass = this.className;
                const buttonId = this.id;
                
                sendEvent('button_click', {
                    'button_text': buttonText.substring(0, 50), // Limiter la longueur
                    'button_class': buttonClass.substring(0, 100),
                    'button_id': buttonId,
                    'button_type': this.tagName.toLowerCase()
                });
            });
        });
    }
    
    // Tracking des clics sur les liens
    function trackLinkClicks() {
        const links = document.querySelectorAll('a[href]');
        
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                const linkText = this.textContent.trim() || this.getAttribute('aria-label') || 'Unknown';
                const linkHref = this.href;
                const isExternal = this.hostname !== window.location.hostname;
                
                sendEvent('link_click', {
                    'link_text': linkText.substring(0, 50),
                    'link_url': linkHref,
                    'is_external': isExternal,
                    'link_type': this.getAttribute('data-link-type') || 'general'
                });
            });
        });
    }
    
    // Tracking des soumissions de formulaires
    function trackFormSubmissions() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const formId = this.id || 'unknown';
                const formAction = this.action;
                const formMethod = this.method;
                
                sendEvent('form_submit', {
                    'form_id': formId,
                    'form_action': formAction,
                    'form_method': formMethod,
                    'form_type': this.getAttribute('data-form-type') || 'general'
                });
            });
        });
    }
    
    // Tracking des interactions avec les produits
    function trackProductInteractions() {
        // Clics sur les images de produits
        const productImages = document.querySelectorAll('.product-image, [data-product-image]');
        productImages.forEach(img => {
            img.addEventListener('click', function(e) {
                const productId = this.getAttribute('data-product-id') || this.closest('[data-product-id]')?.getAttribute('data-product-id');
                if (productId) {
                    sendEvent('product_image_click', {
                        'product_id': productId,
                        'image_src': this.src
                    });
                }
            });
        });
        
        // Clics sur les favoris
        const favoriteButtons = document.querySelectorAll('[data-favorite], .favorite-button');
        favoriteButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                const productId = this.getAttribute('data-product-id') || this.closest('[data-product-id]')?.getAttribute('data-product-id');
                if (productId) {
                    sendEvent('favorite_toggle', {
                        'product_id': productId,
                        'action': this.classList.contains('favorited') ? 'remove' : 'add'
                    });
                }
            });
        });
    }
    
    // Tracking des erreurs JavaScript
    function trackErrors() {
        window.addEventListener('error', function(e) {
            sendEvent('javascript_error', {
                'error_message': e.message,
                'error_filename': e.filename,
                'error_lineno': e.lineno,
                'error_colno': e.colno
            });
        });
        
        window.addEventListener('unhandledrejection', function(e) {
            sendEvent('promise_rejection', {
                'error_message': e.reason?.message || e.reason,
                'error_stack': e.reason?.stack
            });
        });
    }
    
    // Tracking de la performance
    function trackPerformance() {
        if ('performance' in window) {
            window.addEventListener('load', function() {
                setTimeout(() => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    if (perfData) {
                        sendEvent('page_performance', {
                            'load_time': Math.round(perfData.loadEventEnd - perfData.loadEventStart),
                            'dom_content_loaded': Math.round(perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart),
                            'first_paint': Math.round(performance.getEntriesByName('first-paint')[0]?.startTime || 0),
                            'first_contentful_paint': Math.round(performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0)
                        });
                    }
                }, 1000);
            });
        }
    }
    
    // Initialisation
    function init() {
        // Événements de scroll
        window.addEventListener('scroll', trackScroll, { passive: true });
        
        // Événements de clic
        trackButtonClicks();
        trackLinkClicks();
        
        // Événements de formulaire
        trackFormSubmissions();
        
        // Interactions produits
        trackProductInteractions();
        
        // Tracking d'erreurs
        trackErrors();
        
        // Performance
        trackPerformance();
        
        // Engagement après 30 secondes
        setTimeout(trackEngagement, ENGAGEMENT_TIMEOUT);
        
        // Engagement au moment de quitter la page
        window.addEventListener('beforeunload', trackEngagement);
    }
    
    // Démarrer quand le DOM est prêt
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Exposer des fonctions pour un usage externe
    window.AnalyticsEvents = {
        sendEvent: sendEvent,
        trackScroll: trackScroll,
        trackEngagement: trackEngagement
    };
    
})(); 