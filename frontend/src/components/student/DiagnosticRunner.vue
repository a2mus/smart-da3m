<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { diagnosticService, type Question, type AnswerSubmitResponse } from '@/services/diagnosticService'
import { offlineStore } from '@/stores/offlineModule'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const moduleId = computed(() => route.params.moduleId as string)
const sessionId = ref<string>('')
const currentQuestion = ref<Question | null>(null)
const questionNumber = ref(1)
const selectedAnswer = ref('')
const isLoading = ref(true)
const isSubmitting = ref(false)
const error = ref<string | null>(null)
const isComplete = ref(false)
const results = ref<AnswerSubmitResponse | null>(null)
const startTime = ref<number>(0)

const canSubmit = computed(() => !!selectedAnswer.value && !isSubmitting.value)
const progress = computed(() => Math.min(100, (questionNumber.value / 10) * 100))

const startDiagnostic = async () => {
  isLoading.value = true
  error.value = null
  try {
    const response = await diagnosticService.startDiagnostic(moduleId.value)
    sessionId.value = response.session_id
    currentQuestion.value = response.question
    questionNumber.value = response.question_number
    startTime.value = Date.now()

    await offlineStore.createOfflineSession({
      id: sessionId.value,
      student_id: 'current-student',
      module_id: moduleId.value,
      status: 'IN_PROGRESS',
      started_at: new Date(),
      answers: [],
    })
  } catch (err) {
    error.value = t('diagnostic.error')
    console.error('Failed to start diagnostic:', err)
  } finally {
    isLoading.value = false
  }
}

const submitAnswer = async () => {
  if (!canSubmit.value || !currentQuestion.value) return

  isSubmitting.value = true
  const timeMs = Date.now() - startTime.value

  try {
    const response = await diagnosticService.submitAnswer({
      session_id: sessionId.value,
      question_id: currentQuestion.value.id,
      answer: selectedAnswer.value,
      time_ms: timeMs,
    })

    await offlineStore.updateSessionAnswers(sessionId.value, [
      {
        question_id: currentQuestion.value.id,
        answer: selectedAnswer.value,
        is_correct: response.is_correct,
        time_ms: timeMs,
        answered_at: new Date(),
      },
    ])

    if (response.is_complete) {
      isComplete.value = true
      results.value = response
      await offlineStore.completeOfflineSession(sessionId.value)
    } else if (response.next_question) {
      currentQuestion.value = response.next_question
      questionNumber.value++
      selectedAnswer.value = ''
      startTime.value = Date.now()
    }
  } catch (err) {
    error.value = t('diagnostic.error')
    console.error('Failed to submit answer:', err)
  } finally {
    isSubmitting.value = false
  }
}

const finishDiagnostic = () => {
  router.push('/student/dashboard')
}

onMounted(startDiagnostic)
</script>

<template>
  <div data-testid="diagnostic-runner" class="min-h-screen p-4 md:p-6">
    <div class="max-w-3xl mx-auto">
      <div v-if="isLoading" data-testid="loading-state" class="text-center py-12">
        <div class="animate-spin inline-block w-10 h-10 border-4 border-primary-500 border-t-transparent rounded-full"></div>
        <p class="mt-3 text-warm-600">{{ t('diagnostic.loading') }}</p>
      </div>

      <div v-else-if="error" class="bg-danger-50 border border-danger-200 text-danger-700 px-4 py-3 rounded-xl mb-4 flex items-center gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 flex-shrink-0">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span>{{ error }}</span>
      </div>

      <div v-else-if="isComplete && results" data-testid="results-screen" class="text-center py-12">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-16 h-16 text-success-500 mx-auto mb-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z" />
        </svg>
        <h2 class="text-2xl font-bold text-primary-700 mb-2">{{ t('diagnostic.congratulations') }}</h2>
        <p class="text-warm-600 mb-6">{{ t('diagnostic.completed') }}</p>
        <div class="bg-white rounded-xl p-6 shadow-soft mb-6">
          <div class="text-4xl font-bold text-primary-600 mb-2">{{ Math.round(results.accuracy * 100) }}%</div>
          <div class="text-warm-600">{{ t('diagnostic.accuracy') }}</div>
        </div>
        <button @click="finishDiagnostic" class="px-8 py-3 bg-primary-500 hover:bg-primary-600 text-white font-semibold rounded-xl transition-colors">
          {{ t('diagnostic.finish') }}
        </button>
      </div>

      <div v-else-if="currentQuestion" class="bg-white rounded-2xl p-6 shadow-soft">
        <div class="mb-6">
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm text-warm-600">{{ t('diagnostic.question') }} {{ questionNumber }}</span>
            <span class="text-sm text-warm-600">{{ Math.round(progress) }}%</span>
          </div>
          <div data-testid="progress-bar" class="h-2 bg-warm-200 rounded-full overflow-hidden">
            <div class="h-full bg-primary-500 rounded-full transition-all duration-300" :style="{ width: `${progress}%` }"></div>
          </div>
        </div>

        <div class="mb-8">
          <h2 class="text-xl font-semibold text-warm-800 mb-4">{{ currentQuestion.content.text }}</h2>

          <div v-if="currentQuestion.content.type === 'multiple_choice'" class="space-y-3">
            <button v-for="(option, index) in currentQuestion.content.options" :key="index"
              data-testid="answer-option"
              @click="selectedAnswer = option"
              :class="[
                'w-full p-4 text-left rounded-xl border-2 transition-all min-h-[60px]',
                selectedAnswer === option
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-warm-200 hover:border-primary-300'
              ]">
              {{ option }}
            </button>
          </div>

          <div v-else class="space-y-3">
            <input v-model="selectedAnswer" type="text"
              class="w-full p-4 rounded-xl border-2 border-warm-200 focus:border-primary-500 outline-none transition-all"
              :placeholder="t('diagnostic.enterAnswer')" />
          </div>
        </div>

        <button data-testid="submit-button" @click="submitAnswer" :disabled="!canSubmit"
          class="w-full py-4 bg-primary-500 hover:bg-primary-600 disabled:bg-warm-300 text-white font-semibold rounded-xl transition-colors flex justify-center items-center gap-2">
          <span v-if="isSubmitting" class="animate-spin">⟳</span>
          {{ isSubmitting ? t('diagnostic.submitting') : t('diagnostic.submit') }}
        </button>
      </div>
    </div>
  </div>
</template>
