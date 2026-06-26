/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f4f9',
          100: '#e1e9f2',
          200: '#c3d3e6',
          300: '#94b3d3',
          400: '#5e8cba',
          500: '#1b365d', // core navy
          600: '#152b4b',
          700: '#102038',
          800: '#0b1626',
          900: '#070e17',
        },
      },
    },
  },
  plugins: [],
}
