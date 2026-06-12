<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  current: number
  total: number
}>()

const pct = computed(() => Math.round((props.current / props.total) * 100))
</script>

<template>
  <div class="w-full max-w-md mx-auto mb-6">
    <div class="flex justify-between items-center mb-2">
      <span class="text-sm text-on-surface-variant font-medium">
        {{ current }} / {{ total }}
      </span>
      <span class="text-sm font-bold text-primary">{{ pct }}%</span>
    </div>
    <div class="w-full h-3 bg-surface-container-highest rounded-full overflow-hidden">
      <div
        class="h-full bg-primary rounded-full transition-all duration-500 ease-out"
        :style="{ width: pct + '%' }"
      />
    </div>
  </div>
</template>
