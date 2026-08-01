<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useRemediationStore } from '@/stores/remediationStore'
import type { PassportEvaluation } from '@/services/remediationService'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const remediationStore = useRemediationStore()

const props = defineProps<{
  competencyId?: string
}>()

const emit = defineEmits<{
  (e: 'completed', evaluation: PassportEvaluation): void
  (e: 'close'): void
}>()

const activeCompetencyId = computed(() => props.competencyId || (route.params.competencyId as string) || '')

const questions = computed(() => remediationStore.passportQuestions)
const currentIndex = ref(0)
const answers = ref<Map<string, string>>(new Map())
const selectedAnswer = ref('')
const startTime = ref<number>(Date.now())

const isLoading = computed(() => remediationStore.loading)
const isSubmitting = computed(() => remediationStore.actionLoading)
const error = computed(() => remediationStore.error)
const results = computed(() => remediationStore.passportEvaluation)

const currentQuestion = computed(() => questions.value[currentIndex.value])
const progress = computed(() => ((currentIndex.value + 1) / (questions.value.length || 1)) * 100)
const canSubmit = computed(() => !!selectedAnswer.value)

const loadQuestions = async () => {
  if (!activeCompetencyId.value) return
  try {
    await remediationStore.fetchPassportQuestions(activeCompetencyId.value)
    startTime.value = Date.now()
  } catch (err) {
    console.error('Failed to load passport questions:', err)
  }
}

const submitAnswer = async () => {
  if (!currentQuestion.value || !selectedAnswer.value) return

  const timeMs = Date.now() - startTime.value
  answers.value.set(currentQuestion.value.id, selectedAnswer.value)

  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
    selectedAnswer.value = ''
    startTime.value = Date.now()
  } else {
    await submitPassport(timeMs)
  }
}

const submitPassport = async (finalTimeMs: number) => {
  try {
    const answerArray = questions.value.map((q, index) => ({
      question_id: q.id,
      answer: answers.value.get(q.id) || '',
      time_ms: index === questions.value.length - 1 ? finalTimeMs : 10000,
    }))

    const evaluation = await remediationStore.evaluatePassport(activeCompetencyId.value, answerArray)
    emit('completed', evaluation)
  } catch (err) {
    console.error('Failed to submit passport:', err)
  }
}

const finishAssessment = () => {
  emit('close')
  router.push('/student')
}

const retryAssessment = () => {
  currentIndex.value = 0
  answers.value.clear()
  selectedAnswer.value = ''
  loadQuestions()
}

onMounted(loadQuestions)
</script>

<template>
  <div
    class="min-h-screen p-4 md:p-6 bg-surface text-on-surface"
    data-testid="passport-assessment"
  >
    <div class="max-w-3xl mx-auto">
      <!-- Loading State -->
      <div
        v-if="isLoading"
        class="text-center py-12"
      >
        <div class="animate-spin inline-block w-10 h-10 border-4 border-primary border-t-transparent rounded-full" />
        <p class="mt-3 text-on-surface-variant">
          {{ t('passport.loading', 'جاري تحميل اختبار الجواز...') }}
        </p>
      </div>

      <!-- Error -->
      <div
        v-else-if="error"
        class="bg-error-container border border-error text-error px-4 py-3 rounded-xl mb-4"
      >
        {{ error }}
      </div>

      <!-- Results Screen -->
      <div
        v-else-if="results"
        class="text-center py-8"
      >
        <!-- Success State -->
        <div
          v-if="results.passed"
          class="mb-8"
        >
          <div class="text-7xl mb-4">
            🏆
          </div>
          <h2 class="text-3xl font-bold text-tertiary mb-2">
            {{ t('passport.congratulations', 'مبروك! اجتزت التقييم بنجاح') }}
          </h2>
          <p class="text-on-surface-variant">
            {{ results.message }}
          </p>
        </div>

        <!-- Failure State -->
        <div
          v-else
          class="mb-8"
        >
          <div class="text-7xl mb-4">
            💪
          </div>
          <h2 class="text-2xl font-bold text-on-surface mb-2">
            {{ t('passport.keepTrying', 'واصل المحاولة! أنت على وشك الإتقان') }}
          </h2>
          <p class="text-on-surface-variant">
            {{ results.message }}
          </p>
        </div>

        <!-- Results Card -->
        <div class="bg-surface-bright rounded-2xl p-6 shadow-sm border border-outline-variant mb-6 text-start">
          <div class="grid grid-cols-2 gap-4 mb-6">
            <div class="text-center p-4 bg-surface-container rounded-xl">
              <div
                class="text-3xl font-bold"
                :class="results.passed ? 'text-tertiary' : 'text-on-surface'"
              >
                {{ Math.round(results.accuracy * 100) }}%
              </div>
              <div class="text-sm text-on-surface-variant">
                {{ t('passport.accuracy', 'نسبة الدقة') }}
              </div>
            </div>
            <div class="text-center p-4 bg-surface-container rounded-xl">
              <div class="text-3xl font-bold text-primary">
                {{ results.correct_count }}/{{ results.total_questions }}
              </div>
              <div class="text-sm text-on-surface-variant">
                {{ t('passport.questions', 'الأسئلة الصحيحة') }}
              </div>
            </div>
          </div>

          <div class="border-t border-outline-variant pt-4">
            <div class="flex justify-between items-center mb-2">
              <span class="text-on-surface-variant">{{ t('passport.previousLevel', 'المستوى السابق') }}</span>
              <span class="font-medium text-on-surface">{{ results.previous_mastery_level }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-on-surface-variant">{{ t('passport.newLevel', 'المستوى الجديد') }}</span>
              <span class="font-bold text-primary">{{ results.new_mastery_level }}</span>
            </div>
          </div>

          <!-- Badge Earned -->
          <div
            v-if="results.badge_earned"
            class="mt-4 p-4 bg-secondary-container border border-secondary rounded-xl text-center"
          >
            <div class="text-2xl mb-1">
              ⭐
            </div>
            <div class="font-semibold text-secondary">
              {{ t('passport.badgeEarned', 'حصلت على شارة الإتقان!') }}
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-3 justify-center">
          <button
            v-if="!results.passed"
            class="px-6 py-3 bg-surface-container hover:bg-surface-container-high text-on-surface font-semibold rounded-xl transition-colors"
            @click="retryAssessment"
          >
            {{ t('passport.retry', 'إعادة المحاولة') }}
          </button>
          <button
            class="px-6 py-3 bg-primary hover:opacity-90 text-on-primary font-semibold rounded-xl transition-colors"
            @click="finishAssessment"
          >
            {{ t('passport.finish', 'إنهاء التقييم') }}
          </button>
        </div>
      </div>

      <!-- Question Screen -->
      <div
        v-else-if="currentQuestion"
        class="bg-surface-bright rounded-2xl p-6 shadow-sm border border-outline-variant"
      >
        <!-- Header -->
        <div class="mb-6">
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm text-on-surface-variant">{{ t('passport.question', 'السؤال') }} {{ currentIndex + 1 }} {{ t('passport.of', 'من') }} {{ questions.length }}</span>
            <span class="text-sm text-on-surface-variant">{{ Math.round(progress) }}%</span>
          </div>
          <div class="h-2 bg-surface-container rounded-full overflow-hidden">
            <div
              class="h-full bg-primary rounded-full transition-all duration-300"
              :style="{ width: `${progress}%` }"
            />
          </div>
        </div>

        <!-- Passport Badge -->
        <div class="flex items-center gap-2 mb-6 p-3 bg-primary-container rounded-xl">
          <span class="text-2xl">🛂</span>
          <span class="font-semibold text-primary">{{ t('passport.assessmentBadge', 'اختبار الجواز البيداغوجي') }}</span>
        </div>

        <!-- Question -->
        <div class="mb-8">
          <h2 class="text-xl font-semibold text-on-surface mb-4">
            {{ currentQuestion.content.text }}
          </h2>

          <!-- Multiple Choice -->
          <div
            v-if="currentQuestion.content.type === 'multiple_choice'"
            class="space-y-3"
          >
            <button
              v-for="(option, index) in currentQuestion.content.options"
              :key="index"
              :class="[
                'w-full p-4 text-start rounded-xl border-2 transition-all min-h-[60px]',
                selectedAnswer === option
                  ? 'border-primary bg-primary-container text-primary font-bold'
                  : 'border-outline-variant hover:border-primary bg-surface'
              ]"
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
              class="w-full p-4 rounded-xl border-2 border-outline-variant focus:border-primary bg-surface outline-none transition-all"
              :placeholder="t('passport.enterAnswer', 'أدخل إجابتك هنا...')"
            >
          </div>
        </div>

        <!-- Submit -->
        <button
          :disabled="!canSubmit || isSubmitting"
          class="w-full py-4 bg-primary hover:opacity-90 disabled:bg-surface-container-highest text-on-primary font-semibold rounded-xl transition-colors flex justify-center items-center gap-2"
          @click="submitAnswer"
        >
          <span
            v-if="isSubmitting"
            class="animate-spin"
          >⟳</span>
          {{ isSubmitting ? t('passport.submitting', 'جاري التسجيل...') : (currentIndex < questions.length - 1 ? t('passport.next', 'التالي') : t('passport.finish', 'إنهاء')) }}
        </button>
      </div>
    </div>
  </div>
</template>
