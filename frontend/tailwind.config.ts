import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        surface: "var(--surface)",
        primary: {
          DEFAULT: "var(--primary)",
          dark: "var(--primary-dark)",
        },
        secondary: "var(--secondary)",
        accent: "var(--accent)",
        danger: "var(--danger)",
        // Recallix Premium Palette
        recallix: {
          cream: "#F8F5EF",
          ivory: "#F3EFE7",
          card: "#FFFDF9",
          text: "#1A1A1A",
          muted: "#717171",
          graphite: "#333333",
          bronze: "#A68966",
          border: "#E8E2D9",
        }
      },
      borderRadius: {
        '3xl': '24px',
        '4xl': '32px',
      },
      backgroundImage: {
        'grid-light': "radial-gradient(circle, #E8E2D9 1px, transparent 1px)",
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic": "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};
export default config;
