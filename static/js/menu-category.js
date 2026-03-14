document.addEventListener('DOMContentLoaded', function() {
    const categoryButtons = document.querySelectorAll('[data-category]');
    const subCategories = document.querySelectorAll('[id^="category-"][id$="-sub"]');
    const arrowIcon = document.getElementById('arrow-icon');
    const menuButton = document.querySelector('.group button');

    // Gérer la rotation de la flèche
    menuButton.addEventListener('mouseenter', function() {
        arrowIcon.classList.remove('arrow-rotate-reverse');
        arrowIcon.classList.add('arrow-rotate');
    });

    menuButton.addEventListener('mouseleave', function() {
        arrowIcon.classList.remove('arrow-rotate');
        arrowIcon.classList.add('arrow-rotate-reverse');
    });

    categoryButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            // Cacher toutes les sous-catégories
            subCategories.forEach(sub => sub.classList.add('hidden'));
            
            // Afficher la sous-catégorie correspondante
            const categoryId = this.getAttribute('data-category');
            const subCategory = document.getElementById(`category-${categoryId}-sub`);
            if (subCategory) {
                subCategory.classList.remove('hidden');
            }
        });
    });
}); 