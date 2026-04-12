<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale, t } = useI18n()

const isArabic = computed(() => locale.value === 'ar')

const toggleLanguage = () => {
  const newLang = isArabic.value ? 'fr' : 'ar'
  locale.value = newLang
  // Direction and localStorage are handled by the watcher in main.ts
}
</script>

<template>
  <button
    @click="toggleLanguage"
    class="flex items-center gap-2 px-4 py-2 rounded-soft bg-warm-100 hover:bg-warm-200 transition-colors touch-target"
    :aria-label="isArabic ? 'Switch to French' : 'Passer en arabe'"
  >
    <span class="text-lg">{{ isArabic ? '🇫🇷' : '🇸🇦' }}</span>
    <span class="font-medium text-warm-700">
      {{ isArabic ? t('language.french') : t('language.arabic') }}
    </span>
  </button>
</template>