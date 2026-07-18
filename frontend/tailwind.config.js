/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f0fdf4",
          100: "#dcfce7",
          400: "#4ade80",
          500: "#22c55e",
          600: "#16a34a",
          900: "#14532d",
        },
        dark: {
          bg: "#090d16",
          surface: "#111827",
          card: "#1f2937",
          border: "#374151",
        },
      },
      fontFamily: {
        sans: ["Outfit", "Inter", "system-ui", "sans-serif"],
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "glow-pulse": "glowPulse 2.5s infinite alternate",
      },
      keyframes: {
        glowPulse: {
          "0%": { boxShadow: "0 0 15px rgba(34, 197, 94, 0.2)" },
          "100%": { boxShadow: "0 0 35px rgba(34, 197, 94, 0.6)" },
        },
      },
    },
  },
  plugins: [],
};
