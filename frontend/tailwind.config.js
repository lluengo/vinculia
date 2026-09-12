/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        vinculia: {
          bg: "#F8FAFC",
          primary: "#2563EB",
          "primary-hover": "#1D4ED8",
          success: "#10B981",
          text: "#0F172A",
          muted: "#64748B",
          border: "#E2E8F0",
        }
      },
      fontFamily: {
        sans: ['Inter', 'Lexend', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
