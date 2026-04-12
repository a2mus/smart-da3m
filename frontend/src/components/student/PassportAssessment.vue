<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { remediationService, type PassportQuestion, type PassportEvaluation } from '@/services/remediationService'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const competencyId = computed(() => route.params.competencyId as string)

const questions = ref<PassportQuestion[]>([])
const currentIndex = ref(0)
const answers = ref<Map<string, string>>(new Map())
const selectedAnswer = ref('')
const isLoading = ref(true)
const isSubmitting = ref(false)
const error = ref<string | null>(null)
const results = ref<PassportEvaluation | null>(null)
const startTime = ref<number>(Date.now())

const currentQuestion = computed(() => questions.value[currentIndex.value])
const progress = computed(() => ((currentIndex.value + 1) / questions.value.length) * 100)
const canSubmit = computed(() => !!selectedAnswer.value)

const loadQuestions = async () => {
  isLoading.value = true
  error.value = null
  try {
    const response = await remediationService.getPassportQuestions(competencyId.value)
    questions.value = response.questions
    startTime.value = Date.now()
  } catch (err) {
    error.value = t('passport.error')
    console.error('Failed to load passport questions:', err)
  } finally {
    isLoading.value = false
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
  isSubmitting.value = true
  error.value = null

  try {
    const answerArray = questions.value.map((q, index) => ({
      question_id: q.id,
      answer: answers.value.get(q.id) || '',
      time_ms: index === questions.value.length - 1 ? finalTimeMs : 10000,
    }))

    results.value = await remediationService.evaluatePassport(competencyId.value, answerArray)
  } catch (err) {
    error.value = t('passport.submitError')
    console.error('Failed to submit passport:', err)
  } finally {
    isSubmitting.value = false
  }
}

const finishAssessment = () => {
  router.push('/student/dashboard')
}

const retryAssessment = () => {
  results.value = null
  currentIndex.value = 0
  answers.value.clear()
  selectedAnswer.value = ''
  loadQuestions()
}

onMounted(loadQuestions)
</script>

<template>
  <div class="min-h-screen p-4 md:p-6" data-testid="passport-assessment">
    <div class="max-w-3xl mx-auto">
      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="animate-spin inline-block w-10 h-10 border-4 border-primary-500 border-t-transparent rounded-full"></div>
        <p class="mt-3 text-warm-600">{{ t('passport.loading') }}</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-4">
        {{ error }}
      </div>

      <!-- Results Screen -->
      <div v-else-if="results" class="text-center py-8">
        <!-- Success State -->
        <div v-if="results.passed" class="mb-8">
          <div class="text-7xl mb-4">🏆</div>
          <h2 class="text-3xl font-bold text-green-600 mb-2">{{ t('passport.congratulations') }}</h2>
          <p class="text-warm-600">{{ results.message }}</p>
        </div>

        <!-- Failure State -->
        <div v-else class="mb-8">
          <div class="text-7xl mb-4">💪</div>
          <h2 class="text-2xl font-bold text-warm-700 mb-2">{{ t('passport.keepTrying') }}</h2>
          <p class="text-warm-600">{{ results.message }}</p>
        </div>

        <!-- Results Card -->
        <div class="bg-white rounded-2xl p-6 shadow-soft mb-6 text-left">
          <div class="grid grid-cols-2 gap-4 mb-6">
            <div class="text-center p-4 bg-warm-50 rounded-xl">
              <div class="text-3xl font-bold" :class="results.passed ? 'text-green-600' : 'text-warm-600'">
                {{ Math.round(results.accuracy * 100) }}%
              </div>
              <div class="text-sm text-warm-600">{{ t('passport.accuracy') }}</div>
            </div>
            <div class="text-center p-4 bg-warm-50 rounded-xl">
              <div class="text-3xl font-bold text-primary-600">{{ results.correct_count }}/{{ results.total_questions }}</div>
              <div class="text-sm text-warm-600">{{ t('passport.questions') }}</div>
            </div>
          </div>

          <div class="border-t border-warm-200 pt-4">
            <div class="flex justify-between items-center mb-2">
              <span class="text-warm-600">{{ t('passport.previousLevel') }}</span>
              <span class="font-medium">{{ results.previous_mastery_level }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-warm-600">{{ t('passport.newLevel') }}</span>
              <span class="font-bold text-primary-600">{{ results.new_mastery_level }}</span>
            </div>
          </div>

          <!-- Badge Earned -->
          <div v-if="results.badge_earned" class="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-xl text-center">
            <div class="text-2xl mb-1">⭐</div>
            <div class="font-semibold text-yellow-700">{{ t('passport.badgeEarned') }}</div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-3 justify-center">
          <button
            v-if="!results.passed"
            @click="retryAssessment"
            class="px-6 py-3 bg-warm-200 hover:bg-warm-300 text-warm-700 font-semibold rounded-xl transition-colors"
          >
            {{ t('passport.retry') }}
          </button>
          <button
            @click="finishAssessment"
            class="px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white font-semibold rounded-xl transition-colors"
          >
            {{ t('passport.finish') }}
          </button>
        </div>
      </div>

      <!-- Question Screen -->
      <div v-else-if="currentQuestion" class="bg-white rounded-2xl p-6 shadow-soft">
        <!-- Header -->
        <div class="mb-6">
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm text-warm-600">{{ t('passport.question') }} {{ currentIndex + 1 }} {{ t('passport.of') }} {{ questions.length }}</span>
            <span class="text-sm text-warm-600">{{ Math.round(progress) }}%</span>
          </div>
          <div class="h-2 bg-warm-200 rounded-full overflow-hidden">
            <div class="h-full bg-primary-500 rounded-full transition-all duration-300" :style="{ width: `${progress}%` }"></div>
          </div>
        </div>

        <!-- Passport Badge -->
        <div class="flex items-center gap-2 mb-6 p-3 bg-yellow-50 rounded-xl">
          <span class="text-2xl">🛂</span>
          <span class="font-semibold text-yellow-700">{{ t('passport.assessmentBadge') }}</span>
        </div>

        <!-- Question -->
        <div class="mb-8">
          <h2 class="text-xl font-semibold text-warm-800 mb-4">{{ currentQuestion.content.text }}</h2>

          <!-- Multiple Choice -->
          <div v-if="currentQuestion.content.type === 'multiple_choice'" class="space-y-3">
            <button
              v-for="(option, index) in currentQuestion.content.options"
              :key="index"
              @click="selectedAnswer = option"
              :class="[
                'w-full p-4 text-left rounded-xl border-2 transition-all min-h-[60px]',
                selectedAnswer === option
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-warm-200 hover:border-primary-300'
              ]"
            >
              {{ option }}
            </button>
          </div>

          <!-- Text Input -->
          <div v-else class="space-y-3">
            <input
              v-model="selectedAnswer"
              type="text"
              class="w-full p-4 rounded-xl border-2 border-warm-200 focus:border-primary-500 outline-none transition-all"
              :placeholder="t('passport.enterAnswer')"
            />
          </div>
        </div>

        <!-- Submit -->
        <button
          @click="submitAnswer"
          :disabled="!canSubmit || isSubmitting"
          class="w-full py-4 bg-primary-500 hover:bg-primary-600 disabled:bg-warm-300 text-white font-semibold rounded-xl transition-colors flex justify-center items-center gap-2"
        >
          <span v-if="isSubmitting" class="animate-spin">⟳</span>
          {{ isSubmitting ? t('passport.submitting') : (currentIndex < questions.length - 1 ? t('passport.next') : t('passport.finish')) }}
        </button>
      </div>
    </div>
  </div>
</template>
