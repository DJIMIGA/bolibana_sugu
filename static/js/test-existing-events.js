/**
 * Script pour tester les événements existants
 * Vérifie pourquoi les événements ne persistent pas après avoir quitté la page
 */

console.log('🔍 === TEST ÉVÉNEMENTS EXISTANTS ===');

// Fonction pour tester les événements existants
function testExistingEvents() {
    console.log('🧪 Test des événements existants...');
    
    if (typeof fbq === 'undefined') {
        console.log('❌ Facebook Pixel non disponible');
        return;
    }
    
    console.log('✅ Facebook Pixel disponible');
    
    // Test 1: ViewContent (déjà implémenté dans product_detail.html)
    console.log('📦 Test ViewContent (page produit)...');
    fbq('track', 'ViewContent', {
        value: 15000,
        currency: 'XOF',
        content_ids: [123],
        content_type: 'product',
        content_name: 'Test Product - Bazin Super Riche',
        content_category: 'Fabric'
    });
    
    // Test 2: AddToCart (déjà implémenté dans _add_to_cart_card_button.html)
    setTimeout(() => {
        console.log('🛒 Test AddToCart (ajout au panier)...');
        fbq('track', 'AddToCart', {
            value: 15000,
            currency: 'XOF',
            content_ids: [123],
            content_type: 'product',
            content_name: 'Test Product - Bazin Super Riche'
        });
    }, 2000);
    
    // Test 3: ViewCart (déjà implémenté dans cart.html)
    setTimeout(() => {
        console.log('🛍️ Test ViewCart (vue panier)...');
        fbq('track', 'ViewCart', {
            value: 15000,
            currency: 'XOF',
            content_type: 'product',
            content_ids: [123]
        });
    }, 4000);
    
    // Test 4: InitiateCheckout (déjà implémenté dans checkout.html)
    setTimeout(() => {
        console.log('💳 Test InitiateCheckout (début commande)...');
        fbq('track', 'InitiateCheckout', {
            value: 15000,
            currency: 'XOF',
            num_items: 1,
            content_ids: [123],
            content_type: 'product'
        });
    }, 6000);
    
    // Test 5: Purchase (déjà implémenté dans order_confirmation.html)
    setTimeout(() => {
        console.log('💰 Test Purchase (achat)...');
        fbq('track', 'Purchase', {
            value: 15000,
            currency: 'XOF',
            content_ids: [123],
            content_type: 'product',
            num_items: 1,
            order_id: 'test-order-123'
        });
    }, 8000);
    
    console.log('✅ Tous les tests programmés');
    console.log('📱 Vérifiez Meta Pixel Helper dans 10 secondes');
}

// Fonction pour vérifier les templates existants
function checkExistingTemplates() {
    console.log('🔍 === VÉRIFICATION TEMPLATES EXISTANTS ===');
    
    // Vérifier si on est sur une page produit
    const isProductPage = document.querySelector('[data-product-id]') || 
                         document.querySelector('.product-detail') ||
                         window.location.pathname.includes('/product/');
    
    if (isProductPage) {
        console.log('✅ Page produit détectée');
        console.log('📋 ViewContent devrait être envoyé automatiquement');
    }
    
    // Vérifier les boutons d'ajout au panier
    const addToCartButtons = document.querySelectorAll('[data-add-to-cart], .add-to-cart, button[onclick*="cart"]');
    console.log(`🛒 Boutons d'ajout au panier trouvés: ${addToCartButtons.length}`);
    
    // Vérifier les boutons panier
    const cartButtons = document.querySelectorAll('[data-cart], .cart-button, .cart-icon');
    console.log(`🛍️ Boutons panier trouvés: ${cartButtons.length}`);
    
    // Vérifier les boutons checkout
    const checkoutButtons = document.querySelectorAll('[data-checkout], .checkout-button, .proceed-to-checkout');
    console.log(`💳 Boutons checkout trouvés: ${checkoutButtons.length}`);
    
    // Vérifier les formulaires de recherche
    const searchForms = document.querySelectorAll('form[action*="search"], .search-form');
    console.log(`🔍 Formulaires de recherche trouvés: ${searchForms.length}`);
}

// Fonction pour simuler les actions utilisateur
function simulateUserActions() {
    console.log('🎭 === SIMULATION ACTIONS UTILISATEUR ===');
    
    // Simuler un clic sur un bouton d'ajout au panier
    const addToCartButton = document.querySelector('[data-add-to-cart], .add-to-cart, button[onclick*="cart"]');
    if (addToCartButton) {
        console.log('🖱️ Simulation clic sur bouton d\'ajout au panier...');
        addToCartButton.click();
    } else {
        console.log('❌ Aucun bouton d\'ajout au panier trouvé');
    }
    
    // Simuler un clic sur un bouton panier
    setTimeout(() => {
        const cartButton = document.querySelector('[data-cart], .cart-button, .cart-icon');
        if (cartButton) {
            console.log('🖱️ Simulation clic sur bouton panier...');
            cartButton.click();
        } else {
            console.log('❌ Aucun bouton panier trouvé');
        }
    }, 2000);
}

// Fonction pour vérifier les événements côté serveur
function checkServerEvents() {
    console.log('🖥️ === VÉRIFICATION ÉVÉNEMENTS CÔTÉ SERVEUR ===');
    
    // Vérifier les cookies de consentement
    const cookies = document.cookie.split(';').map(c => c.trim());
    const marketingConsent = cookies.find(c => c.includes('marketing'));
    const analyticsConsent = cookies.find(c => c.includes('analytics'));
    
    console.log('🍪 Cookies de consentement:');
    console.log(`   Marketing: ${marketingConsent ? '✅' : '❌'}`);
    console.log(`   Analytics: ${analyticsConsent ? '✅' : '❌'}`);
    
    // Vérifier les scripts Facebook
    const fbScripts = Array.from(document.querySelectorAll('script[src*="facebook"]'));
    console.log(`📜 Scripts Facebook chargés: ${fbScripts.length}`);
    
    // Vérifier les variables Django
    console.log('🐍 Variables Django disponibles:');
    console.log(`   request.cookie_consent: ${typeof request !== 'undefined' ? '✅' : '❌'}`);
    console.log(`   request.cookie_consent.marketing: ${typeof request !== 'undefined' && request.cookie_consent && request.cookie_consent.marketing ? '✅' : '❌'}`);
}

// Fonction pour diagnostiquer le problème de persistance
function diagnosePersistenceIssue() {
    console.log('🔍 === DIAGNOSTIC PROBLÈME PERSISTANCE ===');
    
    // Vérifier si les événements sont envoyés mais pas persistés
    console.log('💡 Causes possibles du problème de persistance:');
    console.log('   1. Événements envoyés mais non reçus par Facebook');
    console.log('   2. Configuration incorrecte dans Events Manager');
    console.log('   3. Filtres dans Meta Pixel Helper');
    console.log('   4. Problème de timing (événements envoyés trop rapidement)');
    console.log('   5. Données d\'événements incorrectes');
    
    // Vérifier la configuration actuelle
    console.log('\n📋 Configuration actuelle:');
    console.log(`   URL: ${window.location.href}`);
    console.log(`   fbq disponible: ${typeof fbq !== 'undefined'}`);
    console.log(`   Consentement marketing: ${document.cookie.includes('marketing')}`);
    
    // Suggestions de résolution
    console.log('\n💡 Suggestions de résolution:');
    console.log('   1. Vérifier Events Manager > Test Events');
    console.log('   2. Attendre 15-30 minutes pour voir les événements');
    console.log('   3. Vérifier les filtres dans Meta Pixel Helper');
    console.log('   4. Tester avec des données d\'événements plus simples');
}

// Exposer les fonctions globalement
window.testExistingEvents = testExistingEvents;
window.checkExistingTemplates = checkExistingTemplates;
window.simulateUserActions = simulateUserActions;
window.checkServerEvents = checkServerEvents;
window.diagnosePersistenceIssue = diagnosePersistenceIssue;

// Auto-exécution au chargement
setTimeout(() => {
    checkExistingTemplates();
    checkServerEvents();
    diagnosePersistenceIssue();
}, 1000);

console.log('📋 Commandes disponibles:');
console.log('  - testExistingEvents() : Tester les événements existants');
console.log('  - checkExistingTemplates() : Vérifier les templates');
console.log('  - simulateUserActions() : Simuler les actions utilisateur');
console.log('  - checkServerEvents() : Vérifier les événements côté serveur');
console.log('  - diagnosePersistenceIssue() : Diagnostiquer le problème de persistance'); 