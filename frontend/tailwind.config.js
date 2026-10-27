/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#090d16',
        surface: {
          50: '#0f172a',
          100: '#141e33',
          200: '#1a2640',
          300: '#233354',
          400: '#334155',
        },
        border: {
          subtle: 'rgba(255, 255, 255, 0.08)',
          strong: 'rgba(255, 255, 255, 0.16)',
        },
        primary: {
          DEFAULT: '#38bdf8',
          hover: '#0ea5e9',
          muted: 'rgba(56, 189, 248, 0.12)',
        },
        verified: {
          DEFAULT: '#10b981',
          bg: 'rgba(16, 185, 129, 0.12)',
          border: 'rgba(16, 185, 129, 0.25)',
        },
        unverified: {
          DEFAULT: '#f59e0b',
          bg: 'rgba(245, 158, 11, 0.12)',
          border: 'rgba(245, 158, 11, 0.25)',
        },
        accent: {
          purple: '#8b5cf6',
          cyan: '#06b6d4',
          rose: '#f43f5e',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
      boxShadow: {
        'card-subtle': '0 4px 20px -2px rgba(0, 0, 0, 0.5)',
        'glow-primary': '0 0 25px -5px rgba(56, 189, 248, 0.25)',
        'glow-verified': '0 0 20px -5px rgba(16, 185, 129, 0.2)',
      }
    },
  },
  plugins: [],
}
