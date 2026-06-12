<script setup lang="ts">
defineProps<{
  title: string
  description: string
  duration?: string
  priority?: string
}>()
</script>

<template>
  <div class="bg-surface-container rounded-2xl p-4 border border-ink-100 flex items-start gap-3">
    <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
      :class="priority === 'high' ? 'bg-rose-100 text-rose-600' : priority === 'medium' ? 'bg-amber-100 text-amber-600' : 'bg-teal-100 text-teal-600'">
      <span class="material-symbols-outlined text-xl">lightbulb</span>
    </div>
    <div class="flex-1 min-w-0">
      <div class="flex justify-between items-start gap-2">
        <p class="font-bold text-ink-800 text-sm">{{ title }}</p>
        <span v-if="duration" class="text-xs text-ink-400 whitespace-nowrap">{{ duration }}</span>
      </div>
      <p class="text-xs text-ink-500 mt-1 leading-relaxed">{{ description }}</p>
    </div>
  </div>
</template>
