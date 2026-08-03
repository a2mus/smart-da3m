<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { diagnosticService, type Question, type AnswerSubmitResponse } from '@/services/diagnosticService'
import { offlineStore } from '@/stores/offlineModule'
import { useOfflineSync } from '@/composables/useOfflineSync'
import NetworkStatusIndicator from '@/components/NetworkStatusIndicator.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { isOnline, isSyncing, queueAnswer } = useOfflineSync()

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
const showFeedback = ref(false)
const lastAnswerCorrect = ref<boolean | null>(null)
const lastErrorClass = ref<string | null>(null)
const totalQuestions = ref(10)

const canSubmit = computed(() => !!selectedAnswer.value && !isSubmitting.value && !showFeedback.value)
const progress = computed(() => Math.min(100, (questionNumber.value / totalQuestions.value) * 100))

const errorClassLabels: Record<string, string> = {
  RESOURCE: 'راجع الأساسيات — هناك مفهوم سابق تحتاج إتقانه',
  PROCESS: 'اقرأ السؤال مرة أخرى — ربما فهمت المطلوب بطريقة مختلفة',
  INCIDENTAL: 'حاول مرة أخرى — ربما كان سهواً بسيطاً',
  NONE: '',
}

const groupLabels: Record<string, { label: string; icon: string; desc: string }> = {
  MASTERED: { label: 'المجموعة أ — إتقان', icon: 'workspace_premium', desc: 'أنت متقن! استمر في أنشطة الإثراء والتحدي' },
  PROFICIENT: { label: 'المجموعة أ — إتقان', icon: 'workspace_premium', desc: 'أنت متقن! استمر في أنشطة الإثراء والتحدي' },
  FAMILIAR: { label: 'المجموعة ب — إتقان جزئي', icon: 'lightbulb', desc: 'تحتاج لتقوية في بعض النقاط — أنت على الطريق الصحيح' },
  ATTEMPTED: { label: 'المجموعة ب — إتقان جزئي', icon: 'lightbulb', desc: 'تحتاج لتقوية في بعض النقاط — أنت على الطريق الصحيح' },
  NOT_STARTED: { label: 'المجموعة ج — يحتاج دعماً', icon: 'favorite', desc: 'سنبني معاً من البداية — لا تقلق، كل الأبطال بدأوا من هنا' },
}

const masteryLabels: Record<string, string> = {
  NOT_STARTED: 'لم يبدأ',
  ATTEMPTED: 'بدأ التعلم',
  FAMILIAR: 'متوسط',
  PROFICIENT: 'متقن',
  MASTERED: 'متمكن',
}

const startDiagnosticOffline = async () => {
  const firstQuestion = await diagnosticService.getNextQuestionOffline(moduleId.value, 0)
  if (firstQuestion) {
    sessionId.value = `offline-${Date.now()}`
    currentQuestion.value = firstQuestion
    questionNumber.value = 1
  } else {
    throw new Error('No cached questions available for offline session.')
  }
}

const startDiagnostic = async () => {
  isLoading.value = true
  error.value = null
  try {
    await diagnosticService.preFetchModuleQuestions(moduleId.value)

    if (typeof navigator !== 'undefined' && !navigator.onLine) {
      await startDiagnosticOffline()
    } else {
      try {
        const response = await diagnosticService.startDiagnostic(moduleId.value)
        sessionId.value = response.session_id
        currentQuestion.value = response.question
        questionNumber.value = response.question_number
      } catch (netErr) {
        console.warn('Starting online diagnostic failed, trying offline fallback:', netErr)
        await startDiagnosticOffline()
      }
    }

    startTime.value = Date.now()

    if (sessionId.value) {
      await offlineStore.createOfflineSession({
        id: sessionId.value,
        student_id: 'current-student',
        module_id: moduleId.value,
        status: 'IN_PROGRESS',
        started_at: new Date(),
        answers: [],
      })
    }
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
  const questionId = currentQuestion.value.id
  const answerVal = selectedAnswer.value

  let pendingId: number | null = null
  try {
    pendingId = await queueAnswer({
      session_id: sessionId.value,
      question_id: questionId,
      answer: answerVal,
      time_ms: timeMs,
      sync_status: 'PENDING',
    })
  } catch (queueErr) {
    console.error('Failed to queue answer in Dexie:', queueErr)
  }

  try {
    const response = await diagnosticService.submitAnswer({
      session_id: sessionId.value,
      question_id: questionId,
      answer: answerVal,
      time_ms: timeMs,
    })

    if (pendingId) {
      await offlineStore.markAnswerSynced(pendingId)
    }

    await offlineStore.updateSessionAnswers(sessionId.value, [
      {
        question_id: questionId,
        answer: answerVal,
        is_correct: response.is_correct,
        time_ms: timeMs,
        answered_at: new Date(),
      },
    ])

    const isCorrect = response.is_correct ?? true
    lastAnswerCorrect.value = isCorrect
    lastErrorClass.value = response.error_classification && response.error_classification !== 'NONE' ? response.error_classification : null
    showFeedback.value = !response.is_complete && !isCorrect

    if (response.is_complete || isCorrect) {
      advanceToNext(response)
    }
  } catch (err) {
    console.warn('Network submission failed, answer retained in offline queue:', err)
    showFeedback.value = false

    const nextQ = await diagnosticService.getNextQuestionOffline(moduleId.value, questionNumber.value)
    if (nextQ) {
      currentQuestion.value = nextQ
      questionNumber.value++
      selectedAnswer.value = ''
      startTime.value = Date.now()
    } else {
      isComplete.value = true
      results.value = {
        is_correct: true,
        error_classification: 'NONE',
        current_mastery: 0.8,
        mastery_level: 'PROFICIENT',
        next_question: null,
        is_complete: true,
        accuracy: 1.0,
      }
      await offlineStore.completeOfflineSession(sessionId.value)
    }
  } finally {
    isSubmitting.value = false
  }
}

const advanceToNext = (response: AnswerSubmitResponse) => {
  showFeedback.value = false
  lastAnswerCorrect.value = null
  lastErrorClass.value = null

  if (response.is_complete) {
    isComplete.value = true
    results.value = response
    offlineStore.completeOfflineSession(sessionId.value)
  } else if (response.next_question) {
    currentQuestion.value = response.next_question
    questionNumber.value++
    selectedAnswer.value = ''
    startTime.value = Date.now()
  }
}

const continueAfterFeedback = () => {
  if (results.value || !currentQuestion.value) return
  showFeedback.value = false
  lastAnswerCorrect.value = null
  lastErrorClass.value = null
  selectedAnswer.value = ''
  startTime.value = Date.now()
}

const finishDiagnostic = () => {
  router.push('/student')
}

onMounted(() => {
  startDiagnostic()
})
</script>

<template>
  <div
    data-testid="diagnostic-runner"
    class="min-h-screen p-4 md:p-6"
    dir="rtl"
  >
    <div class="max-w-3xl mx-auto">
      <!-- Network Status Indicator -->
      <NetworkStatusIndicator class="mb-4 rounded-xl overflow-hidden" />
      <!-- Loading State -->
      <div
        v-if="isLoading"
        data-testid="loading-state"
        class="text-center py-12"
      >
        <div class="animate-spin inline-block w-10 h-10 border-4 border-primary border-t-transparent rounded-full" />
        <p class="mt-3 text-on-surface-variant">
          {{ t('diagnostic.loading') }}
        </p>
      </div>

      <!-- Error State -->
      <div
        v-else-if="error"
        class="bg-rose-50 border border-rose-200 text-rose-600 px-4 py-3 rounded-xl mb-4 flex items-center gap-3"
      >
        <span class="material-symbols-outlined">error</span>
        <span>{{ error }}</span>
      </div>

      <!-- Results Screen -->
      <div
        v-else-if="isComplete && results"
        data-testid="results-screen"
        class="text-center py-8"
      >
        <!-- Star icon -->
        <div class="text-6xl mb-4">
          🌟
        </div>
        <h2 class="text-2xl font-black text-primary mb-2">
          {{ t('diagnostic.congratulations') }}
        </h2>
        <p class="text-on-surface-variant mb-8">
          {{ t('diagnostic.completed') }}
        </p>

        <!-- Group Placement -->
        <div
          v-if="results.mastery_level"
          class="bg-primary text-on-primary rounded-[2rem] p-8 text-center mb-6 shadow-lg"
        >
          <span class="material-symbols-outlined text-5xl mb-3 block">
            {{ groupLabels[results.mastery_level]?.icon || 'school' }}
          </span>
          <h2 class="text-2xl font-black mb-2">
            {{ groupLabels[results.mastery_level]?.label || masteryLabels[results.mastery_level] }}
          </h2>
          <p class="text-on-primary/80">
            {{ groupLabels[results.mastery_level]?.desc || '' }}
          </p>
        </div>

        <!-- Accuracy -->
        <div class="bg-surface-container rounded-2xl p-6 shadow-soft mb-6">
          <div class="text-4xl font-black text-primary mb-2">
            {{ Math.round(results.accuracy * 100) }}%
          </div>
          <div class="text-on-surface-variant">
            {{ t('diagnostic.accuracy') }}
          </div>
        </div>

        <!-- Mastery Level -->
        <div class="bg-surface-container rounded-2xl p-5 mb-6 text-start">
          <div class="flex justify-between items-center mb-3">
            <span class="font-bold text-on-surface">مستوى الإتقان</span>
            <span class="text-primary font-black">{{ masteryLabels[results.mastery_level] || results.mastery_level }}</span>
          </div>
          <div class="w-full h-3 bg-surface-container-highest rounded-full overflow-hidden">
            <div
              class="h-full bg-primary rounded-full transition-all duration-700"
              :style="{ width: `${(results.current_mastery || 0) * 100}%` }"
            />
          </div>
        </div>

        <!-- Error Classification -->
        <div
          v-if="results.error_classification && results.error_classification !== 'NONE'"
          class="bg-surface-container rounded-2xl p-5 mb-6 text-start"
        >
          <h3 class="font-bold text-on-surface mb-3">
            تحليل الأداء
          </h3>
          <p class="text-sm text-on-surface-variant">
            {{ errorClassLabels[results.error_classification] || '' }}
          </p>
        </div>

        <!-- Finish Button -->
        <button
          class="w-full py-4 bg-primary text-on-primary font-bold rounded-xl hover:bg-primary/90 active:scale-[0.98] transition-all min-h-[60px]"
          @click="finishDiagnostic"
        >
          {{ t('diagnostic.finish') }}
        </button>
      </div>

      <!-- Question Screen -->
      <div
        v-else-if="currentQuestion"
        class="bg-surface-container rounded-[2.5rem] p-6 md:p-10 shadow-soft"
      >
        <!-- Progress -->
        <div class="mb-6">
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm text-on-surface-variant">{{ t('diagnostic.question') }} {{ questionNumber }}</span>
            <span class="text-sm font-bold text-primary">{{ Math.round(progress) }}%</span>
          </div>
          <div class="h-3 bg-surface-container-highest rounded-full overflow-hidden">
            <div
              class="h-full bg-primary rounded-full transition-all duration-500 ease-out"
              :style="{ width: `${progress}%` }"
            />
          </div>
        </div>

        <!-- Feedback Overlay -->
        <div
          v-if="showFeedback"
          class="mb-6 p-4 rounded-2xl text-center transition-all duration-300"
          :class="lastAnswerCorrect ? 'bg-mint-50 border border-mint-200' : 'bg-amber-50 border border-amber-200'"
        >
          <div class="text-3xl mb-2">
            {{ lastAnswerCorrect ? '✅' : '❌' }}
          </div>
          <p
            class="font-bold text-lg mb-1"
            :class="lastAnswerCorrect ? 'text-mint-600' : 'text-amber-600'"
          >
            {{ lastAnswerCorrect ? 'إجابة صحيحة! أحسنت!' : 'ليس تماماً — لا تقلق!' }}
          </p>
          <p
            v-if="!lastAnswerCorrect && lastErrorClass"
            class="text-sm text-on-surface-variant"
          >
            {{ errorClassLabels[lastErrorClass] || '' }}
          </p>
          <button
            v-if="!lastAnswerCorrect"
            class="mt-3 px-6 py-2 bg-primary text-on-primary rounded-xl font-bold hover:bg-primary/90 active:scale-95 transition-all"
            @click="continueAfterFeedback"
          >
            تابع
          </button>
        </div>

        <!-- Question Text -->
        <div class="mb-8">
          <h2 class="text-xl md:text-2xl font-bold text-on-surface text-center mb-8 leading-relaxed">
            {{ currentQuestion.content.text }}
          </h2>

          <!-- Multiple Choice Options -->
          <div
            v-if="currentQuestion.content.type === 'multiple_choice'"
            class="space-y-3"
          >
            <button
              v-for="(option, index) in currentQuestion.content.options"
              :key="index"
              data-testid="answer-option"
              :class="[
                'w-full p-5 text-start rounded-2xl border-2 transition-all min-h-[60px] text-lg font-medium',
                selectedAnswer === option
                  ? 'border-primary bg-primary/5 text-primary'
                  : 'border-outline-variant text-on-surface hover:border-primary/40 hover:bg-surface-container-highest',
              ]"
              :disabled="showFeedback"
              @click="selectedAnswer = option"
            >
              {{ option }}
            </button>
          </div>

          <!-- Text Input -->
          <div
            v-else
            class="space-y-3"
          >
            <input
              v-model="selectedAnswer"
              type="text"
              :disabled="showFeedback"
              class="w-full p-5 rounded-2xl border-2 border-outline-variant bg-surface-container-lowest text-on-surface focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all text-lg font-['Inter','Tajawal'] text-center"
              :placeholder="t('diagnostic.enterAnswer')"
            >
          </div>
        </div>

        <!-- Submit Button -->
        <button
          v-if="!showFeedback"
          data-testid="submit-button"
          :disabled="!canSubmit"
          class="w-full py-4 bg-primary text-on-primary font-bold rounded-xl hover:bg-primary/90 active:scale-[0.98] transition-all disabled:opacity-40 disabled:cursor-not-allowed flex justify-center items-center gap-2 min-h-[60px]"
          @click="submitAnswer"
        >
          <span
            v-if="isSubmitting"
            class="animate-spin material-symbols-outlined"
          >progress_activity</span>
          {{ isSubmitting ? t('diagnostic.submitting') : t('diagnostic.submit') }}
        </button>
      </div>
    </div>
  </div>
</template>
