import { createApp, watch } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'

import App from './App.vue'
import router from './router'

// Import global styles
import './assets/main.css'

// Import locale messages
import ar from './locales/ar.json'
import fr from './locales/fr.json'

// Detect initial language from localStorage or browser
const savedLang = localStorage.getItem('language')
const browserLang = navigator.language.startsWith('ar') ? 'ar' : 'fr'
const initialLocale = savedLang || browserLang

// Set initial direction
const initialDir = initialLocale === 'ar' ? 'rtl' : 'ltr'
document.documentElement.setAttribute('dir', initialDir)
document.documentElement.setAttribute('lang', initialLocale)

// Create i18n instance
const i18n = createI18n({
  legacy: false,
  locale: initialLocale,
  fallbackLocale: 'fr',
  messages: {
    ar,
    fr
  }
})

// Watch for locale changes and update direction
watch(
  () => i18n.global.locale.value,
  (newLocale: string) => {
    const newDir = newLocale === 'ar' ? 'rtl' : 'ltr'
    document.documentElement.setAttribute('dir', newDir)
    document.documentElement.setAttribute('lang', newLocale)
    localStorage.setItem('language', newLocale)
  }
)

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

app.mount('#app')