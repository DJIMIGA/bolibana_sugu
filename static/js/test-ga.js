/**
 * Script de test pour Google Analytics
 * Utilisé uniquement en mode développement
 */

(function() {
    'use strict';
    
    console.log('🔍 Test Google Analytics - Script chargé');
    
    // Vérifier si gtag est disponible
    if (typeof gtag === 'undefined') {
        console.warn('⚠️ Google Analytics (gtag) non disponible');
        return;
    }
    
    console.log('✅ Google Analytics (gtag) disponible');
    
    // Fonction pour tester les événements
    window.testGAEvent = function(eventName, parameters = {}) {
        if (typeof gtag === 'undefined') {
            console.warn('⚠️ gtag non disponible pour tester l\'événement:', eventName);
            return;
        }
        
        console.log('📊 Test événement GA:', eventName, parameters);
        gtag('event', eventName, parameters);
    };
    
    // Test automatique au chargement de la page
    document.addEventListener('DOMContentLoaded', function() {
        console.log('📊 Test automatique Google Analytics');
        
        // Test d'événement page_view
        setTimeout(function() {
            window.testGAEvent('test_page_view', {
                'custom_parameter': 'test_value',
                'page_title': document.title
            });
        }, 2000);
    });
    
    // Ajouter un bouton de test dans la console
    console.log('💡 Utilisez window.testGAEvent("nom_evenement", {parametres}) pour tester');
    
})(); 