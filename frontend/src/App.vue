<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

const isRTL = computed(() => locale.value === 'ar')
</script>

<template>
  <div 
    class="min-h-screen bg-surface transition-colors duration-normal ease-out-quart"
    :class="{ 'font-arabic': isRTL, 'font-sans': !isRTL }"
    :dir="isRTL ? 'rtl' : 'ltr'"
  >
    <router-view v-slot="{ Component }">
      <transition 
        name="fade" 
        mode="out-in"
      >
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<style>
/* Global Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s cubic-bezier(0.25, 1, 0.5, 1),
              transform 0.3s cubic-bezier(0.25, 1, 0.5, 1);
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* Ensure body takes full height and uses brand background */
body {
  @apply bg-surface;
  margin: 0;
}
</style>
