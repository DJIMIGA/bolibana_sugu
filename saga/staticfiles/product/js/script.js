function openProductOptions() {
    document.getElementById('product-options-modal').classList.remove('hidden');
}

function closeProductOptions() {
    document.getElementById('product-options-modal').classList.add('hidden');
}

// Fermer la modal si on clique en dehors
document.addEventListener('click', function(event) {
    const modal = document.getElementById('product-options-modal');
    if (event.target === modal) {
        closeProductOptions();
    }
}); 