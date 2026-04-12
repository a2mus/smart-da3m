<script setup lang="ts">
interface Props {
  title: string
  description: string
  duration: string
  priority: 'high' | 'medium' | 'low'
}

const props = defineProps<Props>()

const priorityConfig = {
  high: {
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    icon: '🔴',
    label: 'high'
  },
  medium: {
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    icon: '🟡',
    label: 'medium'
  },
  low: {
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    icon: '🔵',
    label: 'low'
  }
}

const config = priorityConfig[props.priority]
</script>

<template>
  <div 
    :class="[
      'p-4 rounded-xl border-2 transition-all hover:shadow-md',
      config.bgColor,
      config.borderColor
    ]"
    data-testid="insight-card"
  >
    <div class="flex items-start gap-3">
      <span class="text-xl">{{ config.icon }}</span>
      <div class="flex-1">
        <h4 class="font-semibold text-warm-800 text-sm">{{ title }}</h4>
        <p class="text-warm-600 text-xs mt-1 leading-relaxed">{{ description }}</p>
        <div class="flex items-center gap-2 mt-2">
          <span class="text-xs bg-white/60 px-2 py-0.5 rounded text-warm-600">
            ⏱ {{ duration }}
          </span>
          <span class="text-xs text-warm-500 capitalize">
            {{ $t(`priority.${config.label}`) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
