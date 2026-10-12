import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#F4F6F1",
        surface: "#FFFFFF",
        primary: {
          DEFAULT: "#2F5D46",
          hover: "#254B38",
          light: "#EBF2EC",
          dark: "#1E3C2D",
        },
        editorial: {
          bg: "#F4F6F1",
          card: "#FFFFFF",
          border: "#E3E8E2",
          text: "#1F2A24",
          muted: "#607166",
          subtle: "#8C9B90",
        },
        accent: {
          chart: "#818CF8",
          purple: "#A78BFA",
          blue: "#38BDF8",
          amber: "#F59E0B",
          rose: "#F43F5E",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        editorial: ["Newsreader", "Georgia", "Cambria", "Times New Roman", "serif"],
      },
      borderRadius: {
        "2xl": "18px",
        "3xl": "24px",
      },
      boxShadow: {
        card: "0 1px 3px 0 rgba(31, 42, 36, 0.04), 0 1px 2px -1px rgba(31, 42, 36, 0.03)",
        elevated: "0 10px 25px -5px rgba(31, 42, 36, 0.06), 0 8px 10px -6px rgba(31, 42, 36, 0.04)",
      },
    },
  },
  plugins: [],
};

export default config;
