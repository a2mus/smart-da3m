<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  current: number  // 1-10
  previous?: number
}>(), {
  previous: 5,
})

const segments = Array.from({ length: 10 }, (_, i) => i + 1)

function segmentColor(level: number): string {
  if (level <= 3) return 'bg-mint-400'
  if (level <= 6) return 'bg-amber-400'
  return 'bg-rose-400'
}

const activeColor = computed(() => segmentColor(props.current))
</script>

<template>
  <div class="w-full">
    <div class="flex justify-between items-center mb-2">
      <span class="text-xs text-on-surface-variant font-medium">سهل</span>
      <span
        class="text-sm font-bold"
        :class="current <= 3 ? 'text-mint-500' : current <= 6 ? 'text-amber-500' : 'text-rose-500'"
      >
        {{ current }}/10
      </span>
      <span class="text-xs text-on-surface-variant font-medium">صعب</span>
    </div>
    <div class="flex gap-1 h-3">
      <div
        v-for="s in segments"
        :key="s"
        class="flex-1 rounded-full transition-all duration-500"
        :class="[
          s <= current ? segmentColor(s) : 'bg-ink-100 dark:bg-ink-700',
          s === current ? 'ring-2 ring-offset-1 ring-current scale-y-125' : ''
        ]"
        :style="{ '--tw-ring-color': `var(--tw-${activeColor.replace('bg-', '')})` }"
      />
    </div>
    <p class="text-xs text-on-surface-variant/60 mt-1 text-center transition-all duration-300">
      {{ current <= 3 ? 'مستوى أساسي' : current <= 6 ? 'مستوى متوسط' : 'مستوى متقدم' }}
    </p>
  </div>
</template>
