/**
 * Script pour forcer l'envoi d'événements Facebook Pixel
 * À utiliser pour tester en production
 */

// Fonction pour forcer l'envoi d'événements
function forceFacebookPixelEvents() {
    console.log('🚀 Force envoi d\'événements Facebook Pixel...');
    
    if (typeof fbq === 'undefined') {
        console.log('❌ Facebook Pixel non disponible');
        return;
    }
    
    // Forcer l'envoi d'événements e-commerce
    setTimeout(() => {
        // ViewContent
        fbq('track', 'ViewContent', {
            content_name: 'Bazin Super Riche - Test',
            content_category: 'Fabric',
            value: 15000,
            currency: 'XOF'
        });
        console.log('🎯 ViewContent forcé');
        
        // AddToCart
        setTimeout(() => {
            fbq('track', 'AddToCart', {
                content_name: 'Bazin Super Riche - Test',
                content_category: 'Fabric',
                value: 15000,
                currency: 'XOF',
                quantity: 1
            });
            console.log('🎯 AddToCart forcé');
        }, 1000);
        
    }, 2000);
}

// Exposer la fonction
window.forceFacebookPixelEvents = forceFacebookPixelEvents;

// Instructions
console.log(`
🚀 FORCE TEST FACEBOOK PIXEL:

Pour tester en production, tape dans la console:
forceFacebookPixelEvents()

Cela enverra des événements ViewContent et AddToCart
`); 