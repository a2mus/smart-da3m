<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

const isRTL = computed(() => locale.value === 'ar')
</script>

<template>
  <div :class="{ 'font-arabic': isRTL, 'font-sans': !isRTL }">
    <router-view />
  </div>
</template>

<style scoped>
/* Additional component-specific styles can go here */
</style>
