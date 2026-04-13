/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Soft modern palette - no pure whites/blacks
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        },
        // Nurturing soft tones
        soft: {
          cream: '#faf9f6',
          sand: '#f5f5f0',
          sage: '#e8efe8',
          rose: '#fdf2f4',
        },
        // Warm neutrals
        warm: {
          50: '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
          500: '#78716c',
          600: '#57534e',
          700: '#44403c',
          800: '#292524',
          900: '#1c1917',
        },
        // Semantic Nurturing Status Colors
        danger: {
          50: '#fdf2f4', // linked to soft.rose
          100: '#fce4e8',
          200: '#f9c5d1',
          300: '#f49cb1',
          400: '#ec6688',
          500: '#e13666',
          600: '#d12053',
        },
        warning: {
          50: '#fffbf0', // linked to a warm yellow
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
        },
        success: {
          50: '#f0fdf4', // linked to soft mint
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
        }
      },
      fontFamily: {
        // Arabic fonts
        arabic: ['Tajawal', 'Cairo', 'sans-serif'],
        // Latin fonts
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'soft': '0.75rem',
        'asymmetric': '2rem 0.5rem 2rem 0.5rem',
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
        'touch': '60px', // Minimum touch target
      },
      minHeight: {
        'touch': '60px',
      },
      minWidth: {
        'touch': '60px',
      }
    },
  },
  plugins: [],
}
