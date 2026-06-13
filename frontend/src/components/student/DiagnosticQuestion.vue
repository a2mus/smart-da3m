<script setup lang="ts">
import { computed } from 'vue'

export interface QuestionData {
  id: string
  text: string
  difficulty_level: number
  options?: string[]
  type: 'multiple_choice' | 'numeric'
}

const props = defineProps<{
  question: QuestionData
  questionNumber: number
  totalQuestions: number
}>()

const emit = defineEmits<{
  answer: [answer: string | number]
}>()

const difficultyLabel = computed(() => {
  const d = props.question.difficulty_level
  if (d <= 3) return 'سهل'
  if (d <= 6) return 'متوسط'
  return 'صعب'
})
</script>

<template>
  <div class="bg-surface-container rounded-[2.5rem] p-8 md:p-12 shadow-lg max-w-2xl mx-auto">
    <!-- Question header -->
    <div class="flex items-center justify-between mb-6">
      <span class="bg-primary/10 text-primary px-4 py-1.5 rounded-full text-sm font-bold">
        سؤال {{ questionNumber }}
      </span>
      <span class="text-xs text-on-surface-variant bg-surface-container-highest px-3 py-1 rounded-full">
        {{ difficultyLabel }}
      </span>
    </div>

    <!-- Question text -->
    <p class="text-xl md:text-2xl font-bold text-on-surface text-center mb-8 leading-relaxed">
      {{ question.text }}
    </p>

    <!-- Multiple choice options -->
    <div
      v-if="question.type === 'multiple_choice' && question.options"
      class="grid gap-4"
    >
      <button
        v-for="(option, i) in question.options"
        :key="i"
        class="w-full bg-surface-container-lowest border-2 border-outline-variant hover:border-primary
               rounded-2xl p-5 text-lg font-medium text-on-surface text-center
               hover:bg-primary/5 active:scale-[0.98] transition-all duration-200"
        @click="emit('answer', i)"
      >
        {{ option }}
      </button>
    </div>

    <!-- Numeric input -->
    <div
      v-else
      class="text-center"
    >
      <input
        type="number"
        class="w-32 h-16 text-center text-3xl font-bold rounded-2xl border-2 border-outline-variant
               bg-surface-container-lowest text-on-surface focus:border-primary focus:ring-4
               focus:ring-primary/20 outline-none transition-all font-['Inter','Tajawal']"
        placeholder="?"
        @keyup.enter="emit('answer', ($event.target as HTMLInputElement).value)"
      >
      <button
        class="block mx-auto mt-4 bg-primary text-on-primary px-8 py-3 rounded-xl font-bold
               hover:bg-primary/90 active:scale-95 transition-all"
        @click="emit('answer', 0)"
      >
        تأكيد
      </button>
    </div>
  </div>
</template>
