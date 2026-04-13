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
    bgColor: 'bg-danger-50',
    borderColor: 'border-danger-200',
    iconColor: 'text-danger-600',
    label: 'high'
  },
  medium: {
    bgColor: 'bg-warning-50',
    borderColor: 'border-warning-200',
    iconColor: 'text-warning-600',
    label: 'medium'
  },
  low: {
    bgColor: 'bg-primary-50',
    borderColor: 'border-primary-200',
    iconColor: 'text-primary-600',
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
      <div :class="config.iconColor" class="mt-0.5 flex-shrink-0">
        <!-- High Priority: Exclamation Triangle -->
        <svg v-if="priority === 'high'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
        <!-- Medium Priority: Information Circle -->
        <svg v-else-if="priority === 'medium'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" /></svg>
        <!-- Low Priority: Light Bulb -->
        <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.829 1.508-2.336 1.149-.687 2.242-1.67 2.242-3.472a6 6 0 10-12 0c0 1.802 1.093 2.785 2.242 3.472.85.507 1.508 1.353 1.508 2.336v.192" /></svg>
      </div>
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
