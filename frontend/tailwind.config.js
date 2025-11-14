/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f4ff',
          100: '#e3eaff',
          200: '#c5d7ff',
          300: '#99b8ff',
          400: '#6690ff',
          500: '#667eea',
          600: '#4f5ed1',
          700: '#3f4ab8',
          800: '#303da0',
          900: '#263187',
        },
      },
    },
  },
  plugins: [],
}
