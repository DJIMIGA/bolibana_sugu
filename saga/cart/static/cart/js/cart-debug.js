// Script de debug pour le panier
console.log('Cart Debug: Script chargé');

// Fonction pour tester le panier
window.testCart = () => {
    console.log('=== Test du Panier ===');
    console.log('Largeur de l\'écran:', window.innerWidth);
    console.log('Breakpoint mobile:', window.innerWidth < 1024);
    
    if (cartSidebarInstance) {
        console.log('Instance du panier:', !!cartSidebarInstance);
        console.log('État ouvert:', cartSidebarInstance.isOpen);
        console.log('État mobile:', cartSidebarInstance.isMobile);
        
        // Tester l'ouverture
        console.log('Test d\'ouverture...');
        cartSidebarInstance.open();
        
        setTimeout(() => {
            console.log('État après ouverture:', cartSidebarInstance.isOpen);
            
            // Tester la fermeture
            console.log('Test de fermeture...');
            cartSidebarInstance.close();
            
            setTimeout(() => {
                console.log('État après fermeture:', cartSidebarInstance.isOpen);
                console.log('=== Test terminé ===');
            }, 600);
        }, 600);
    } else {
        console.error('Instance du panier non trouvée');
    }
};

// Fonction pour simuler un redimensionnement
window.simulateResize = (width) => {
    console.log('Simulation de redimensionnement à', width, 'px');
    
    // Sauvegarder la largeur originale
    const originalWidth = window.innerWidth;
    
    // Simuler le redimensionnement
    Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: width
    });
    
    // Déclencher l'événement resize
    window.dispatchEvent(new Event('resize'));
    
    // Restaurer la largeur originale après un délai
    setTimeout(() => {
        Object.defineProperty(window, 'innerWidth', {
            writable: true,
            configurable: true,
            value: originalWidth
        });
        window.dispatchEvent(new Event('resize'));
    }, 1000);
};

console.log('Cart Debug: Fonctions de test disponibles (testCart, simulateResize)'); 