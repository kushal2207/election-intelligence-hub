/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bgMain: '#000000',
        bgCard: '#0A0A0A',
        bgElevated: '#111111',
        borderHard: '#333333',
        borderSoft: '#1A1A1A',
        textMain: '#FFFFFF',
        textSecondary: '#D4D4D4',
        textMuted: '#737373',
        accentPrimary: '#C0FF00',   // Neon green from template
        accentCyan: '#22D3EE',      // Cyan gradient pair
        accentHigh: '#16A34A',      // Success
        accentMedium: '#EAB308',    // Warning
        accentLow: '#DC2626',       // Danger
      },
      fontFamily: {
        heading: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'hype-gradient': 'linear-gradient(90deg, #C0FF00 0%, #22D3EE 100%)',
        'hype-gradient-hover': 'linear-gradient(90deg, #d4ff4d 0%, #67e8f9 100%)',
      },
      boxShadow: {
        'hype-glow': '0 0 20px rgba(192, 255, 0, 0.2)',
        'hype-glow-lg': '0 0 40px rgba(192, 255, 0, 0.4)',
        'hype-cyan-glow': '0 0 20px rgba(34, 211, 238, 0.2)',
      }
    },
  },
  plugins: [],
}
