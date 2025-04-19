/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',  // ✅ Inclure les templates Django
    './**/templates/**/*.html',  // ✅ Pour toutes les apps Django
    './static/**/*.js',  // ✅ Inclure les fichiers JS si vous avez du DOM dynamic
    './static/**/*.css',  // ✅ Optionnel, si vous avez des styles CSS personnalisés
  ],
  theme: {
    extend: {
      animation: {
        wiggle: 'wiggle 0.5s ease-in-out',
        spin: 'spin 0.5s ease-in-out',
        borderPulse: 'border-pulse 0.5s ease-in-out',
      },
      keyframes: {
        wiggle: {
          '0%': { transform: 'translateX(0)' },// Départ
          '25%': { transform: 'translateX(-5px)' },// 1er quart
          '50%': { transform: 'translateX(5px)' },
          '75%': { transform: 'translateX(-5px)' },
          '100%': { transform: 'translateX(0)' },
        },
        spin: {
          '0%': { transform: 'rotate(0deg)' },// Départ
          '50%': { transform: 'rotate(15deg)' },
          '100%': { transform: 'rotate(0deg)' },
        },
        borderPulse: {
          '0%': { borderColor: 'transparent' },
          '50%': { borderColor: '#FFD700' }, // Jaune doré
          '100%': { borderColor: '#50C878' }, // Vert émeraude
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
