<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  variant?: 'soft' | 'nurturing' | 'cloud'
  hover?: boolean
  padding?: string
}>()

const cardClasses = computed(() => {
  const base = ['bg-surface-bright', 'transition-all', 'duration-300']
  
  if (props.hover) {
    base.push('card-hover')
  }

  switch (props.variant) {
    case 'nurturing':
      base.push('card-nurturing', 'border', 'border-#faf9f6/50')
      break
    case 'cloud':
      base.push('rounded-cloud', 'shadow-soft')
      break
    case 'soft':
    default:
      base.push('card-soft')
      break
  }
  
  return base
})

const paddingClass = computed(() => {
  return props.padding || 'p-6'
})
</script>

<template>
  <div :class="[cardClasses, paddingClass]">
    <slot />
  </div>
</template>
