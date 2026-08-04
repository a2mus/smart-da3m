<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

const isArabic = computed(() => locale.value === 'ar')

const toggleLanguage = () => {
  const newLang = isArabic.value ? 'fr' : 'ar'
  locale.value = newLang
}
</script>

<template>
  <button
    type="button"
    class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant text-on-surface text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-primary/20 cursor-pointer"
    :aria-label="isArabic ? 'Passer en français' : 'التغيير إلى العربية'"
    @click="toggleLanguage"
  >
    <span class="text-base me-0.5">🌐</span>
    <span class="font-bold text-xs tracking-wide">
      {{ isArabic ? 'Français' : 'العربية' }}
    </span>
    <span class="text-[10px] text-on-surface-variant opacity-75 ms-0.5">
      ({{ isArabic ? 'LTR' : 'RTL' }})
    </span>
  </button>
</template>