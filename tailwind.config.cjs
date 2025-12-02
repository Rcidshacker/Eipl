const { fontFamily } = require('tailwindcss/defaultTheme');

module.exports = {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        chlorophyll: '#0F3B1D',
        leaf: '#1C7C4D',
        loam: '#8B7355',
        slate: '#4A4E4D',
        burntOchre: '#C5521F',
        alertOrange: '#E86A33',
        parchment: '#F2E8CF',
        dusk: '#1B1F1B',
      },
      fontFamily: {
        serif: ['"Bitter"', ...fontFamily.serif],
        sans: ['"Nunito Sans"', ...fontFamily.sans],
        numeric: ['"Barlow Condensed"', ...fontFamily.sans],
      },
      boxShadow: {
        canopy: '0 25px 50px rgba(15, 59, 29, 0.45)',
        slab: '0 18px 35px rgba(74, 78, 77, 0.35)',
      },
      backgroundImage: {
        parchment: 'radial-gradient(circle at 20% 20%, rgba(255,255,255,0.06), transparent 50%), radial-gradient(circle at 80% 0%, rgba(255,255,255,0.06), transparent 45%), linear-gradient(135deg, rgba(242,232,207,0.95), rgba(215,198,170,0.85))',
        slateTexture: 'repeating-linear-gradient(45deg, rgba(15,59,29,0.08), rgba(15,59,29,0.08) 10px, transparent 10px, transparent 20px)',
      },
    },
  },
  plugins: [],
};
