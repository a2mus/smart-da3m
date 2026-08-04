<script setup lang="ts">
import { reactive, computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import DiagnosticQuestion, { type QuestionData } from '@/components/student/DiagnosticQuestion.vue'

const { t } = useI18n()

interface QuestionContent {
  text: string
  type: 'multiple_choice' | 'image_choice' | 'numeric' | 'text' | 'interactive'
  options?: string[]
  correct_answer?: string
}

interface QuestionForm {
  content: QuestionContent
  difficulty_level: number
  target_misconception_id: string
  estimated_time_sec: number
}

interface Props {
  moduleId: string
  moduleName?: string
  question?: {
    id: string
    content: QuestionContent
    difficulty_level: number
    target_misconception_id?: string
    estimated_time_sec: number
  }
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'save', data: QuestionForm): void
  (e: 'cancel'): void
}>()

const isEditMode = computed(() => !!props.question)
const showPreview = ref(false)
const isSaving = ref(false)

const form = reactive<QuestionForm>({
  content: {
    text: props.question?.content.text ?? '',
    type: props.question?.content.type ?? 'multiple_choice',
    options: props.question?.content.options ?? ['', ''],
    correct_answer: props.question?.content.correct_answer ?? '',
  },
  difficulty_level: props.question?.difficulty_level ?? 3,
  target_misconception_id: props.question?.target_misconception_id ?? '',
  estimated_time_sec: props.question?.estimated_time_sec ?? 60,
})

const optionsList = computed(() => form.content.options ?? [])

const previewQuestionData = computed<QuestionData>(() => ({
  id: props.question?.id ?? 'preview-1',
  text: form.content.text.trim() ? form.content.text : t('expert.questionPlaceholder', 'السؤال المعاين...'),
  difficulty_level: form.difficulty_level,
  options: optionsList.value,
  type: (form.content.type === 'image_choice' || form.content.type === 'numeric')
    ? form.content.type
    : 'multiple_choice',
}))

const errors = reactive<Partial<Record<string, string>>>({})

const validateForm = (): boolean => {
  let isValid = true
  Object.keys(errors).forEach((key) => delete errors[key])

  if (!form.content.text.trim()) {
    errors.content = t('validation.questionRequired')
    isValid = false
  }

  if (form.content.type === 'multiple_choice' || form.content.type === 'image_choice') {
    const validOptions = optionsList.value.filter((o: string) => o.trim())
    if (!validOptions || validOptions.length < 2) {
      errors.options = t('validation.minOptions')
      isValid = false
    }
    if (!form.content.correct_answer) {
      errors.correct_answer = t('validation.correctAnswerRequired')
      isValid = false
    }
  } else if (form.content.type === 'numeric') {
    if (!form.content.correct_answer || isNaN(Number(form.content.correct_answer))) {
      errors.correct_answer = t('validation.correctAnswerRequired')
      isValid = false
    }
  } else {
    if (!form.content.correct_answer) {
      errors.correct_answer = t('validation.correctAnswerRequired')
      isValid = false
    }
  }

  return isValid
}

const addOption = () => {
  if (!form.content.options) form.content.options = []
  form.content.options.push('')
}

const removeOption = (index: number) => {
  form.content.options?.splice(index, 1)
}

const handleSubmit = async () => {
  if (!validateForm()) return

  isSaving.value = true
  emit('save', { ...form })
  isSaving.value = false
}

const handleCancel = () => {
  emit('cancel')
}

const togglePreview = () => {
  showPreview.value = !showPreview.value
}
</script>

<template>
  <div
    data-testid="question-editor"
    class="bg-surface-bright rounded-2xl p-6 shadow-soft border border-outline-variant transition-all duration-300"
  >
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-primary text-start">
        {{ isEditMode ? t('expert.editQuestion') : t('expert.createQuestion') }}
      </h2>
      <div class="flex items-center gap-3">
        <span
          v-if="moduleName"
          class="text-sm text-on-surface-variant bg-surface-container px-3 py-1 rounded-full font-medium"
        >
          {{ moduleName }}
        </span>
        <button
          type="button"
          data-testid="preview-toggle"
          class="px-4 py-2 text-sm font-semibold rounded-xl transition-all flex items-center gap-2"
          :class="showPreview ? 'bg-primary text-on-primary shadow-sm' : 'bg-surface-container border border-outline-variant text-on-surface hover:bg-surface-container-high'"
          @click="togglePreview"
        >
          <span>{{ showPreview ? t('expert.hidePreview', 'إخفاء المعاينة') : t('expert.livePreview', 'معاينة مباشرة') }}</span>
        </button>
      </div>
    </div>

    <div :class="['grid gap-6', showPreview ? 'grid-cols-1 lg:grid-cols-2' : 'grid-cols-1']">
      <!-- Form Column -->
      <form
        class="space-y-5"
        @submit.prevent="handleSubmit"
      >
        <!-- Question Text -->
        <div>
          <label class="block text-sm font-medium text-on-surface mb-1 text-start">
            {{ t('expert.questionText') }}
          </label>
          <textarea
            v-model="form.content.text"
            data-testid="question-text-input"
            rows="3"
            class="w-full px-4 py-3 rounded-xl border border-outline-variant focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all bg-surface-container-low text-on-surface resize-none"
            :class="{ 'border-error': errors.content }"
            :placeholder="t('expert.questionPlaceholder')"
          />
          <p
            v-if="errors.content"
            class="text-error text-sm mt-1 text-start"
          >
            {{ errors.content }}
          </p>
        </div>

        <!-- Question Type -->
        <div>
          <label class="block text-sm font-medium text-on-surface mb-1 text-start">
            {{ t('expert.questionType') }}
          </label>
          <select
            v-model="form.content.type"
            data-testid="question-type-select"
            class="w-full px-4 py-2.5 rounded-xl border border-outline-variant focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all bg-surface-container-low text-on-surface"
          >
            <option value="multiple_choice">
              {{ t('expert.multipleChoice') }}
            </option>
            <option value="image_choice">
              Image Choice
            </option>
            <option value="numeric">
              Numeric
            </option>
            <option value="text">
              {{ t('expert.textAnswer') }}
            </option>
            <option value="interactive">
              {{ t('expert.interactive') }}
            </option>
          </select>
        </div>

        <!-- Multiple Choice / Image Choice Options -->
        <div v-if="form.content.type === 'multiple_choice' || form.content.type === 'image_choice'">
          <label class="block text-sm font-medium text-on-surface mb-2 text-start">
            {{ form.content.type === 'image_choice' ? 'Image URLs for Options' : t('expert.answerOptions') }}
          </label>
          <div class="space-y-2">
            <div
              v-for="(option, index) in optionsList"
              :key="index"
              class="flex gap-2"
            >
              <input
                v-model="form.content.options![index]"
                type="text"
                data-testid="option-input"
                class="flex-1 px-4 py-2 rounded-xl border border-outline-variant focus:border-primary outline-none transition-all bg-surface-container-low text-on-surface"
                :placeholder="form.content.type === 'image_choice' ? 'https://example.com/image.png' : t('expert.optionPlaceholder', { number: index + 1 })"
              >
              <input
                v-model="form.content.correct_answer"
                type="radio"
                :value="option"
                class="w-5 h-5 mt-2.5 accent-primary"
                :title="t('expert.markCorrect')"
              >
              <button
                v-if="optionsList.length > 2"
                type="button"
                class="px-3 py-2 text-error hover:bg-error-container/20 rounded-lg transition-colors"
                @click="removeOption(index)"
              >
                ×
              </button>
            </div>
          </div>
          <button
            type="button"
            data-testid="add-option-button"
            class="mt-2 text-primary hover:text-primary/80 text-sm font-medium"
            @click="addOption"
          >
            + {{ t('expert.addOption') }}
          </button>
          <p
            v-if="errors.options"
            class="text-error text-sm mt-1 text-start"
          >
            {{ errors.options }}
          </p>
          <p
            v-if="errors.correct_answer"
            class="text-error text-sm mt-1 text-start"
          >
            {{ errors.correct_answer }}
          </p>
        </div>

        <!-- Numeric Correct Answer -->
        <div v-else-if="form.content.type === 'numeric'">
          <label class="block text-sm font-medium text-on-surface mb-1 text-start">
            Correct Numeric Answer
          </label>
          <input
            v-model="form.content.correct_answer"
            type="number"
            step="any"
            data-testid="numeric-answer-input"
            class="w-full px-4 py-2.5 rounded-xl border border-outline-variant focus:border-primary outline-none transition-all bg-surface-container-low text-on-surface"
            placeholder="42"
          >
          <p
            v-if="errors.correct_answer"
            class="text-error text-sm mt-1 text-start"
          >
            {{ errors.correct_answer }}
          </p>
        </div>

        <!-- Metadata -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-on-surface mb-1 text-start">
              {{ t('expert.difficulty') }}
            </label>
            <select
              v-model="form.difficulty_level"
              data-testid="difficulty-select"
              class="w-full px-4 py-2.5 rounded-xl border border-outline-variant focus:border-primary outline-none transition-all bg-surface-container-low text-on-surface"
            >
              <option
                v-for="n in 10"
                :key="n"
                :value="n"
              >
                {{ n }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-on-surface mb-1 text-start">
              {{ t('expert.misconception') }}
            </label>
            <input
              v-model="form.target_misconception_id"
              type="text"
              data-testid="misconception-input"
              class="w-full px-4 py-2.5 rounded-xl border border-outline-variant focus:border-primary outline-none transition-all font-mono text-sm bg-surface-container-low text-on-surface"
              placeholder="MATH-FRAC-ADD-01"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-on-surface mb-1 text-start">
              {{ t('expert.timeEstimate') }}
            </label>
            <input
              v-model.number="form.estimated_time_sec"
              type="number"
              data-testid="time-input"
              min="5"
              step="5"
              class="w-full px-4 py-2.5 rounded-xl border border-outline-variant focus:border-primary outline-none transition-all bg-surface-container-low text-on-surface"
            >
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-3 pt-4">
          <button
            type="submit"
            data-testid="save-button"
            :disabled="isSaving"
            class="flex-1 px-6 py-3 bg-primary hover:bg-primary/90 disabled:bg-surface-container-highest text-on-primary font-semibold rounded-xl transition-colors shadow-soft flex justify-center items-center gap-2"
          >
            <span
              v-if="isSaving"
              class="animate-spin"
            >⟳</span>
            {{ isSaving ? t('expert.saving') : t('expert.save') }}
          </button>
          <button
            type="button"
            class="px-6 py-3 bg-surface-container hover:bg-surface-container-high text-on-surface font-semibold rounded-xl transition-colors"
            @click="handleCancel"
          >
            {{ t('expert.cancel') }}
          </button>
        </div>
      </form>

      <!-- Side-by-Side Live Preview Column -->
      <div
        v-if="showPreview"
        data-testid="question-preview"
        class="student-preview bg-surface-container-low rounded-2xl p-6 border-2 border-primary/20 sticky top-6 self-start shadow-soft"
      >
        <div class="flex items-center justify-between mb-4 border-b border-outline-variant/60 pb-3">
          <h3 class="text-lg font-bold text-primary flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-primary animate-pulse" />
            {{ t('expert.studentPreviewTitle', 'المعاينة المباشرة للتلميذ') }}
          </h3>
          <span class="text-xs text-on-surface-variant bg-surface-container px-2.5 py-1 rounded-full font-mono font-semibold">
            {{ form.content.type }}
          </span>
        </div>

        <div class="py-2">
          <DiagnosticQuestion
            :question="previewQuestionData"
            :question-number="1"
            :total-questions="1"
          />
        </div>
      </div>
    </div>
  </div>
</template>
