import { createI18n } from 'vue-i18n'
import ar from './locales/ar.json'
import fr from './locales/fr.json'

// Detect initial language from localStorage or browser
const savedLang = localStorage.getItem('language')
const browserLang = typeof navigator !== 'undefined' && navigator.language.startsWith('ar') ? 'ar' : 'fr'
const initialLocale = savedLang || browserLang

// Set initial direction
if (typeof document !== 'undefined') {
  const initialDir = initialLocale === 'ar' ? 'rtl' : 'ltr'
  document.documentElement.setAttribute('dir', initialDir)
  document.documentElement.setAttribute('lang', initialLocale)
}

// Create i18n instance
export const i18n = createI18n({
  legacy: false,
  locale: initialLocale,
  fallbackLocale: 'fr',
  messages: {
    ar,
    fr
  }
})

export default i18n
