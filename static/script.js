// Ici, vous pouvez implémenter la logique pour ouvrir la vue rapide d'un produit
document.addEventListener('DOMContentLoaded', function() {
  const productItems = document.querySelectorAll('.product-item');

  productItems.forEach(item => {
    const quickViewBtn = item.querySelector('.quick-view-btn');
    const productLink = item.querySelector('.product-link');

    quickViewBtn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      openQuickView(this.href);
    });

    item.addEventListener('click', function(e) {
      if (e.target === quickViewBtn || quickViewBtn.contains(e.target)) {
        return;
      }
      productLink.click();
    });
  });


  function openQuickView(url) {

    // Par exemple, en utilisant une requête AJAX pour charger le contenu dans une modale
    fetch(url)
      .then(response => response.text())
      .then(html => {
        // Créez une modale et insérez le HTML reçu
        const modal = document.createElement('div');
        modal.innerHTML = html;
        modal.classList.add('modal');
        document.body.appendChild(modal);

        // Ajoutez la logique pour fermer la modale
        const closeBtn = modal.querySelector('.close-modal');
        if (closeBtn) {
          closeBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
          });
        }
      })
      .catch(error => console.error('Error:', error));
  }
});

// pour les étoiles de notation des produits formulaire de notation des produits
document.addEventListener('DOMContentLoaded', function() {
  const starRating = document.getElementById('star-rating');
  
  // Vérifier si l'élément existe avant de continuer
  if (!starRating) {
    return;
  }
  
  const ratingText = document.getElementById('rating-text');
  const stars = starRating.querySelectorAll('label');
  const inputs = starRating.querySelectorAll('input[type="radio"]');

  function updateStars(rating) {
    stars.forEach((star, index) => {
      if (index < rating) {
        star.textContent = '★'; // Étoile pleine
        star.classList.add('text-yellow-400');
      } else {
        star.textContent = '☆'; // Étoile vide
        star.classList.remove('text-yellow-400');
      }
    });
  }

// pour les étoiles de notation des produits formulaire de notation des produits
  function updateRatingText(rating) {
    const texts = ['Sélectionnez une note', 'Terrible', 'Mauvais', 'Correct', 'Bien', 'Excellent'];
    if (ratingText) {
      ratingText.textContent = texts[rating];
    }
  }

  starRating.addEventListener('mouseover', (e) => {
    if (e.target.tagName === 'LABEL') {
      const rating = parseInt(e.target.getAttribute('for').split('-')[0]);
      updateStars(rating);
      updateRatingText(rating);
    }
  });

  starRating.addEventListener('mouseout', () => {
    const checkedInput = Array.from(inputs).find(input => input.checked);
    const rating = checkedInput ? parseInt(checkedInput.value) : 0;
    updateStars(rating);
    updateRatingText(rating);
  });

  starRating.addEventListener('click', (e) => {
    if (e.target.tagName === 'LABEL') {
      const rating = parseInt(e.target.getAttribute('for').split('-')[0]);
      updateStars(rating);
      updateRatingText(rating);

      // Mettre à jour l'input radio correspondant
      const input = starRating.querySelector(`input[type="radio"][value="${rating}"]`);
      if (input) {
        input.checked = true; // Coche l'input radio correspondant
      }
    }
  });

  // Initialisation
  updateRatingText(0);
});


// pour les images de produits et la galerie d'images
function changeMainImage(imageUrl, button) {
    const mainImage = document.getElementById('main-image');
    if (!mainImage) {
      return;
    }

    mainImage.src = imageUrl;

    if (!button) {
      return;
    }

    const thumbs = document.querySelectorAll('.js-gallery-thumb');
    if (!thumbs.length) {
      return;
    }

    thumbs.forEach(thumb => {
      thumb.setAttribute('aria-selected', 'false');
      thumb.classList.remove('ring-2', 'ring-new', 'ring-green-500', 'ring-indigo-500');
    });

    const ringClass = button.dataset.ringClass || 'ring-new';
    button.setAttribute('aria-selected', 'true');
    button.classList.add('ring-2', ringClass);
  }

document.addEventListener('DOMContentLoaded', function() {
    const quickViewContent = document.getElementById('quick-view-content');

    document.body.addEventListener('click', function(event) {
        if (event.target.id === 'quick-view-btn' || event.target.closest('#quick-view-btn')) {
            if (quickViewContent) {
                quickViewContent.style.display = 'none';
            }
        }
    });
});





















