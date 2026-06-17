/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        cream:  "#FDFBF7",
        gold:   "#b8860b",
        dark:   "#1C1711",
        muted:  "#8A8075",
        borde:  "#E8E3D9",
        card:   "#F5F1EB",
      },
      fontFamily: {
        sans: ['"Helvetica Neue"', "Helvetica", "Arial", "sans-serif"],
      },
    },
  },
  plugins: [],
};
