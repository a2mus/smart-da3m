/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ── ui-spec §1.1 ─────────────────────────────────────────────
        // Backgrounds: warm & safe — no pure white/black
        surface: {
          DEFAULT: '#faf9f6',   // Surface Bright
          container: '#efeeeb', // Surface Container
        },
        "secondary-fixed": "#ffdbce",
        "on-primary-fixed-variant": "#004f56",
        "primary-fixed-dim": "#82d3de",
        "surface-container-lowest": "#faf9f6",
        "primary-fixed": "#9ff0fb",
        "secondary": "#8c4e35",
        "primary": "#00535b",
        "primary-container": "#006d77",
        "on-error": "#faf9f6",
        "on-error-container": "#93000a",
        "surface-bright": "#faf9f6",
        "on-primary": "#faf9f6",
        "on-surface": "#1a1c1a",
        "tertiary-fixed": "#acefe7",
        "on-tertiary-fixed-variant": "#00504b",
        "inverse-primary": "#82d3de",
        "on-tertiary-fixed": "#00201e",
        "inverse-surface": "#2f312f",
        "on-secondary-container": "#793f27",
        "secondary-container": "#ffad8f",
        "outline-variant": "#bec8ca",
        "on-surface-variant": "#3e494a",
        "error-container": "#ffdad6",
        "outline": "#6f797a",
        "on-tertiary": "#faf9f6",
        "surface-container-highest": "#e3e2e0",
        "error": "#ba1a1a",
        "background": "#faf9f6",
        "surface-dim": "#dbdad7",
        "surface-container-low": "#f4f3f1",
        "tertiary-fixed-dim": "#90d3cb",
        "tertiary": "#01544f",
        "on-secondary-fixed-variant": "#6f3720",
        "on-secondary-fixed": "#380d00",
        "on-secondary": "#faf9f6",
        "on-background": "#1a1c1a",
        "surface-tint": "#006972",
        "surface-container-high": "#e9e8e5",
        "on-primary-fixed": "#001f23",
        "secondary-fixed-dim": "#ffb59a",
        "surface-variant": "#e3e2e0",
        "on-tertiary-container": "#a9ece4",
        "on-primary-container": "#9becf7",
        "tertiary-container": "#286d67",
        "inverse-on-surface": "#f2f1ee",

        // Primary: Intelligent & Calm — Deep Turquoise/Teal
        teal: {
          50:  '#e8f4f5',
          100: '#c5e4e7',
          200: '#9fd0d5',
          300: '#6fbbc2',
          400: '#3fabaf',  // hover/light
          500: '#007a85',
          600: '#006d77',  // spec: #006d77
          700: '#00535b',  // spec: #00535b  ← primary action color
          800: '#003d44',
          900: '#002c31',
        },

        // Secondary: Playful Accent — Humic Ochre / Soft Coral
        ochre: {
          50:  '#fdf5f2',
          100: '#fbdfd5',
          200: '#f7c4ad',
          300: '#f0a07f',
          400: '#ffad8f',  // spec: #ffad8f  Soft Coral
          500: '#c8683a',
          600: '#8c4e35',  // spec: #8c4e35  Humic Ochre
          700: '#6b3726',
        },

        // Ink: warm neutral text scale (replaces generic gray)
        ink: {
          primary: '#292524',
          secondary: '#57534e',
          muted: '#a8a29e',
          50:  '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
          500: '#78716c',
          600: '#57534e',
          700: '#44403c',
          800: '#292524',  // default body text
          900: '#1c1917',
        },

        // Semantic status — §1.1: no harsh neons/reds
        mint: {
          50:  '#f0fdf8',
          100: '#ccfbee',
          200: '#99f6dc',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6',  // Success: Soft Mint Green
        },
        amber: {
          50:  '#fffbf0',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',  // Warning: Gentle Amber
        },
        rose: {
          50:  '#fdf2f4',  // spec: linked to soft rose background
          100: '#fce4e8',
          200: '#f9c5d1',
          300: '#f49cb1',
          400: '#ec6688',
          500: '#e13666',  // Error / Remediation: Soft Rose
          600: '#93000a',  // spec: #93000a  On-Error
        },
      },

      fontFamily: {
        // ui-spec §1.2
        arabic: ['Tajawal', 'Cairo', 'sans-serif'],
        sans:   ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
        headline: ["Tajawal", "sans-serif"],
        body: ["Inter", "Cairo", "sans-serif"],
        label: ["Inter", "sans-serif"],
      },

      borderRadius: {
        // ui-spec §1.5
        'soft':        '0.75rem',
        'cloud':       '3rem',              // student dashboard ultra-safe
        'asymmetric':  '2rem 0.75rem 2rem 0.75rem',  // nurturing callout cards
      },

      spacing: {
        // 4pt grid base — ui-spec §1.3
        '18':    '4.5rem',
        '22':    '5.5rem',
        'touch': '44px',   // WCAG minimum; student targets use min-w-[60px]
      },

      minHeight: { 'touch': '44px' },
      minWidth:  { 'touch': '44px' },

      // ui-spec §1.5: brand-hue tinted shadows
      boxShadow: {
        'teal':  '0 10px 30px rgba(0, 83, 91, 0.10)',
        'ochre': '0 10px 30px rgba(140, 78, 53, 0.08)',
        'soft':  '0 4px 20px rgba(26, 28, 26, 0.05)',
      },

      // ui-spec §1.4: calm motion tokens
      transitionDuration: {
        'instant': '100ms',
        'fast':    '200ms',
        'normal':  '300ms',
      },
      transitionTimingFunction: {
        'out-quart': 'cubic-bezier(0.25, 1, 0.5, 1)',
      },
    },
  },
  plugins: [],
}
