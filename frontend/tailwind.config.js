/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        panel: {
          900: '#0f1729',
          800: '#141e33',
          700: '#1a2744',
          600: '#213154',
          500: '#2a3d6b',
        },
        accent: {
          blue: '#3b82f6',
          cyan: '#06b6d4',
          green: '#10b981',
          yellow: '#f59e0b',
          red: '#ef4444',
        },
      },
    },
  },
  plugins: [],
};
