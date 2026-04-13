<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  modelValue: string | number
  label?: string
  type?: string
  placeholder?: string
  disabled?: boolean
  error?: string
  id?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void
}>()

const inputId = computed(() => props.id || `input-${Math.random().toString(36).substring(2, 9)}`)
</script>

<template>
  <div class="w-full flex flex-col gap-1.5">
    <label v-if="label" :for="inputId" class="text-sm font-medium text-ink-700 mx-1">
      {{ label }}
    </label>
    
    <input
      :id="inputId"
      :type="type || 'text'"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      class="input-soft"
      :class="{ 'border-rose-500 focus:border-rose-500 focus:ring-rose-100': error }"
    />
    
    <span v-if="error" class="text-xs text-rose-600 mx-1">
      {{ error }}
    </span>
  </div>
</template>
