<script setup lang="ts">
import { reactive, computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface QuestionContent {
  text: string
  type: 'multiple_choice' | 'text' | 'interactive'
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

const errors = reactive<Partial<Record<string, string>>>({})

const validateForm = (): boolean => {
  let isValid = true
  Object.keys(errors).forEach((key) => delete errors[key])

  if (!form.content.text.trim()) {
    errors.content = t('validation.questionRequired')
    isValid = false
  }

  if (form.content.type === 'multiple_choice') {
    const validOptions = form.content.options?.filter((o) => o.trim())
    if (!validOptions || validOptions.length < 2) {
      errors.options = t('validation.minOptions')
      isValid = false
    }
    if (!form.content.correct_answer) {
      errors.correct_answer = t('validation.correctAnswerRequired')
      isValid = false
    }
  }

  return isValid
}

const addOption = () => {
  form.content.options?.push('')
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
  <div data-testid="question-editor" class="bg-warm-50 rounded-2xl p-6 shadow-soft">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-primary-700">
        {{ isEditMode ? t('expert.editQuestion') : t('expert.createQuestion') }}
      </h2>
      <span v-if="moduleName" class="text-sm text-warm-600 bg-warm-100 px-3 py-1 rounded-full">
        {{ moduleName }}
      </span>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-5">
      <!-- Question Text -->
      <div>
        <label class="block text-sm font-medium text-warm-700 mb-1">
          {{ t('expert.questionText') }}
        </label>
        <textarea
          v-model="form.content.text"
          data-testid="question-text-input"
          rows="3"
          class="w-full px-4 py-3 rounded-xl border-2 border-warm-200 focus:border-primary-400 focus:ring-2 focus:ring-primary-100 outline-none transition-all bg-white resize-none"
          :class="{ 'border-red-400': errors.content }"
          :placeholder="t('expert.questionPlaceholder')"
        />
        <p v-if="errors.content" class="text-red-500 text-sm mt-1">
          {{ errors.content }}
        </p>
      </div>

      <!-- Question Type -->
      <div>
        <label class="block text-sm font-medium text-warm-700 mb-1">
          {{ t('expert.questionType') }}
        </label>
        <select
          v-model="form.content.type"
          data-testid="question-type-select"
          class="w-full px-4 py-2.5 rounded-xl border-2 border-warm-200 focus:border-primary-400 focus:ring-2 focus:ring-primary-100 outline-none transition-all bg-white"
        >
          <option value="multiple_choice">{{ t('expert.multipleChoice') }}</option>
          <option value="text">{{ t('expert.textAnswer') }}</option>
          <option value="interactive">{{ t('expert.interactive') }}</option>
        </select>
      </div>

      <!-- Multiple Choice Options -->
      <div v-if="form.content.type === 'multiple_choice'">
        <label class="block text-sm font-medium text-warm-700 mb-2">
          {{ t('expert.answerOptions') }}
        </label>
        <div class="space-y-2">
          <div
            v-for="(option, index) in form.content.options"
            :key="index"
            class="flex gap-2"
          >
            <input
              v-model="form.content.options[index]"
              type="text"
              data-testid="option-input"
              class="flex-1 px-4 py-2 rounded-xl border-2 border-warm-200 focus:border-primary-400 outline-none transition-all"
              :placeholder="t('expert.optionPlaceholder', { number: index + 1 })"
            />
            <input
              v-model="form.content.correct_answer"
              type="radio"
              :value="option"
              class="w-5 h-5 mt-2.5 accent-primary-500"
              :title="t('expert.markCorrect')"
            />
            <button
              v-if="form.content.options.length > 2"
              type="button"
              @click="removeOption(index)"
              class="px-3 py-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
            >
              ×
            </button>
          </div>
        </div>
        <button
          type="button"
          data-testid="add-option-button"
          @click="addOption"
          class="mt-2 text-primary-600 hover:text-primary-700 text-sm font-medium"
        >
          + {{ t('expert.addOption') }}
        </button>
        <p v-if="errors.options" class="text-red-500 text-sm mt-1">
          {{ errors.options }}
        </p>
        <p v-if="errors.correct_answer" class="text-red-500 text-sm mt-1">
          {{ errors.correct_answer }}
        </p>
      </div>

      <!-- Metadata -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-warm-700 mb-1">
            {{ t('expert.difficulty') }}
          </label>
          <select
            v-model="form.difficulty_level"
            data-testid="difficulty-select"
            class="w-full px-4 py-2.5 rounded-xl border-2 border-warm-200 focus:border-primary-400 outline-none transition-all bg-white"
          >
            <option v-for="n in 10" :key="n" :value="n">{{ n }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-warm-700 mb-1">
            {{ t('expert.misconception') }}
          </label>
          <input
            v-model="form.target_misconception_id"
            type="text"
            data-testid="misconception-input"
            class="w-full px-4 py-2.5 rounded-xl border-2 border-warm-200 focus:border-primary-400 outline-none transition-all font-mono text-sm"
            placeholder="MATH-FRAC-ADD-01"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-warm-700 mb-1">
            {{ t('expert.timeEstimate') }}
          </label>
          <input
            v-model.number="form.estimated_time_sec"
            type="number"
            data-testid="time-input"
            min="5"
            step="5"
            class="w-full px-4 py-2.5 rounded-xl border-2 border-warm-200 focus:border-primary-400 outline-none transition-all"
          />
        </div>
      </div>

      <!-- Preview Toggle -->
      <div class="flex items-center gap-2">
        <button
          type="button"
          data-testid="preview-toggle"
          @click="togglePreview"
          class="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center gap-1"
        >
          <span>{{ showPreview ? t('expert.hidePreview') : t('expert.showPreview') }}</span>
        </button>
      </div>

      <!-- Preview Section -->
      <div
        v-if="showPreview"
        data-testid="question-preview"
        class="student-preview bg-white rounded-xl p-6 border-2 border-primary-100"
      >
        <h3 class="text-lg font-semibold text-warm-800 mb-4">
          {{ t('expert.studentPreview') }}
        </h3>
        <p class="text-warm-700 mb-4">{{ form.content.text }}</p>

        <div v-if="form.content.type === 'multiple_choice'" class="space-y-2">
          <div
            v-for="(option, index) in form.content.options"
            :key="index"
            class="p-3 rounded-lg border-2 border-warm-200 hover:border-primary-300 cursor-pointer transition-colors"
          >
            {{ option || t('expert.emptyOption') }}
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex gap-3 pt-4">
        <button
          type="submit"
          data-testid="save-button"
          :disabled="isSaving"
          class="flex-1 px-6 py-3 bg-primary-500 hover:bg-primary-600 disabled:bg-warm-300 text-white font-semibold rounded-xl transition-colors shadow-soft flex justify-center items-center gap-2"
        >
          <span v-if="isSaving" class="animate-spin">⟳</span>
          {{ isSaving ? t('expert.saving') : t('expert.save') }}
        </button>
        <button
          type="button"
          @click="handleCancel"
          class="px-6 py-3 bg-warm-200 hover:bg-warm-300 text-warm-700 font-semibold rounded-xl transition-colors"
        >
          {{ t('expert.cancel') }}
        </button>
      </div>
    </form>
  </div>
</template>
