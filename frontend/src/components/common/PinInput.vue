<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'

const props = withDefaults(defineProps<{
  length?: number
  modelValue?: string
}>(), {
  length: 6,
  modelValue: '',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  complete: [value: string]
}>()

const inputs = ref<HTMLInputElement[]>([])
const digits = ref<string[]>(Array(props.length).fill(''))

const isComplete = computed(() => digits.value.every(d => d !== ''))

function setRef(el: unknown, i: number) {
  if (el) inputs.value[i] = el as HTMLInputElement
}

function handleInput(index: number, event: Event) {
  const target = event.target as HTMLInputElement
  const val = target.value.replace(/\D/g, '').slice(-1)
  digits.value[index] = val
  target.value = val

  const pin = digits.value.join('')
  emit('update:modelValue', pin)

  if (val && index < props.length - 1) {
    nextTick(() => inputs.value[index + 1]?.focus())
  }

  if (isComplete.value) {
    emit('complete', pin)
  }
}

function handleKeydown(index: number, event: KeyboardEvent) {
  if (event.key === 'Backspace' && !digits.value[index] && index > 0) {
    digits.value[index - 1] = ''
    nextTick(() => inputs.value[index - 1]?.focus())
    emit('update:modelValue', digits.value.join(''))
  }
}

function handlePaste(event: ClipboardEvent) {
  event.preventDefault()
  const paste = event.clipboardData?.getData('text')?.replace(/\D/g, '').slice(0, props.length) || ''
  for (let i = 0; i < props.length; i++) {
    digits.value[i] = paste[i] || ''
  }
  emit('update:modelValue', digits.value.join(''))
  if (paste.length === props.length) {
    emit('complete', paste)
  }
}
</script>

<template>
  <div
    class="flex flex-row-reverse justify-center gap-3"
    @paste="handlePaste"
  >
    <input
      v-for="i in length"
      :key="i"
      :ref="(el) => setRef(el, i - 1)"
      type="text"
      inputmode="numeric"
      maxlength="1"
      :value="digits[i - 1]"
      class="w-12 h-14 text-center text-2xl font-bold rounded-xl border-2
             bg-surface-container-lowest text-on-surface
             border-outline-variant focus:border-primary focus:bg-primary/5
             outline-none transition-all duration-200
             font-['Inter','Tajawal']"
      :aria-label="`PIN digit ${i}`"
      @input="handleInput(i - 1, $event)"
      @keydown="handleKeydown(i - 1, $event)"
    >
  </div>
</template>
