/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        canvas: "#f7f5ef",
        sidebar: "#0d0e12",
        card: "#ffffff",
        border: "#e5e1d5",
        brand: {
          gold: "#b8860b",
          goldLight: "#fffbeb",
          goldDark: "#92400e",
          cyan: "#0d9488",
          cyanLight: "#f0fdfa",
        },
      },
    },
  },
  plugins: [],
};
