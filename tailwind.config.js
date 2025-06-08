/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './saga/templates/**/*.html',  // ✅ Inclure les templates Django
    './saga/**/templates/**/*.html',  // ✅ Pour toutes les apps Django
    './static/**/*.js',  // ✅ Inclure les fichiers JS si vous avez du DOM dynamic
    './static/**/*.css',  // ✅ Optionnel, si vous avez des styles CSS personnalisés
  ],
  theme: {
    extend: {
      colors: {
        new: '#22C55E', // green-500
        promo: '#EF4444', // red-500
        popular: '#FACC15', // yellow-400
        clothing: '#3B82F6', // blue-500
        stock: '#9333EA', // purple-600
        phone: '#4F46E5', // indigo-600
        fabric: '#4F46E5', // indigo-600
        cultural: '#059669', // emerald-500
      },
      animation: {
        wiggle: 'wiggle 0.5s ease-in-out',
        spin: 'spin 0.5s ease-in-out',
        borderPulse: 'border-pulse 0.5s ease-in-out',
      },
      keyframes: {
        wiggle: {
          '0%': { transform: 'translateX(0)' },
          '25%': { transform: 'translateX(-5px)' },
          '50%': { transform: 'translateX(5px)' },
          '75%': { transform: 'translateX(-5px)' },
          '100%': { transform: 'translateX(0)' },
        },
        spin: {
          '0%': { transform: 'rotate(0deg)' },
          '50%': { transform: 'rotate(15deg)' },
          '100%': { transform: 'rotate(0deg)' },
        },
        borderPulse: {
          '0%': { borderColor: 'transparent' },
          '50%': { borderColor: '#FFD700' },
          '100%': { borderColor: '#50C878' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
    require('@tailwindcss/forms'),
  ],
} 