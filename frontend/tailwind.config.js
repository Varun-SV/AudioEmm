/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#1a1a2e",
        panel:   "#16213e",
        accent:  "#e94560",
        muted:   "#a8a8b3",
      },
    },
  },
  plugins: [],
};
