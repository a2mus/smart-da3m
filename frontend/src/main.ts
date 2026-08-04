import { createApp, watch } from 'vue'
import { createPinia } from 'pinia'
import i18n from './i18n'

import App from './App.vue'
import router from './router'

// Import global styles
import './assets/main.css'

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