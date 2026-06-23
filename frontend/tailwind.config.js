/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        wellnessBg: "#F7FAF5",
        primaryGreen: "#2E8B57",
        accentGreen: "#6B8E23",
        darkGreen: "#1B4D3E",
        lightGreen: "#EBF0E4",
        borderGreen: "#DDE5D0",
      },
      fontFamily: {
        serif: ["Playfair Display", "Georgia", "serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
}
