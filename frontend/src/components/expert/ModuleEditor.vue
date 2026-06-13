<script setup lang="ts">
import { reactive, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface ModuleForm {
  subject: string
  grade_level: string
  domain: string
  competency_id: string
  status: 'DRAFT' | 'PUBLISHED'
}

interface Props {
  mode: 'create' | 'edit'
  module?: {
    id: string
    subject: string
    grade_level: string
    domain: string
    competency_id: string
    status: 'DRAFT' | 'PUBLISHED'
    created_at: string
  }
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'create',
})

const emit = defineEmits<{
  (e: 'save', data: ModuleForm): void
  (e: 'update', data: ModuleForm & { id: string }): void
  (e: 'cancel'): void
}>()

const form = reactive<ModuleForm>({
  subject: props.module?.subject ?? '',
  grade_level: props.module?.grade_level ?? '',
  domain: props.module?.domain ?? '',
  competency_id: props.module?.competency_id ?? '',
  status: props.module?.status ?? 'DRAFT',
})

const errors = reactive<Partial<Record<keyof ModuleForm, string>>>({})

const isEditMode = computed(() => props.mode === 'edit')
const title = computed(() =>
  isEditMode.value ? t('expert.editModule') : t('expert.createModule')
)

const validateForm = (): boolean => {
  let isValid = true
  Object.keys(errors).forEach((key) => delete errors[key as keyof ModuleForm])

  if (!form.subject.trim()) {
    errors.subject = t('validation.required')
    isValid = false
  }
  if (!form.grade_level.trim()) {
    errors.grade_level = t('validation.required')
    isValid = false
  }
  if (!form.domain.trim()) {
    errors.domain = t('validation.required')
    isValid = false
  }
  if (!form.competency_id.trim()) {
    errors.competency_id = t('validation.required')
    isValid = false
  }

  return isValid
}

const handleSubmit = () => {
  if (!validateForm()) return

  if (isEditMode.value && props.module) {
    emit('update', { ...form, id: props.module.id })
  } else {
    emit('save', { ...form })
  }
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<template>
  <div class="bg-warm-50 rounded-2xl p-6 shadow-soft">
    <h2 class="text-2xl font-bold text-primary-700 mb-6">
      {{ title }}
    </h2>

    <form
      class="space-y-5"
      @submit.prevent="handleSubmit"
    >
      <!-- Subject -->
      <div>
        <label
          for="subject"
          class="block text-sm font-medium text-warm-700 mb-1"
        >
          {{ t('expert.subject') }}
        </label>
        <input
          id="subject"
          v-model="form.subject"
          type="text"
          data-testid="subject-input"
          class="w-full px-4 py-2.5 rounded-xl border-2 border-warm-200 focus:border-primary-400 focus:ring-2 focus:ring-primary-100 outline-none transition-all bg-surface-bright"
          :class="{ 'border-red-400': errors.subject }"
          :placeholder="t('expert.subjectPlaceholder')"
        >
        <p
          v-if="errors.subject"
          class="error-message text-red-500 text-sm mt-1"
        >
          {{ errors.subject }}
        </p>
      </div>

      <!-- Grade Level -->
      <div>
        <label
          for="grade_level"
          class="block text-sm font-medium text-warm-700 mb-1"
        >
          {{ t('expert.gradeLevel') }}
        </label>
        <select
          id="grade_level"
          v-model="form.grade_level"
          data-testid="grade-level-input"
          class="w-full px-4 py-2.5 rounded-xl border-2 border-warm-200 focus:border-primary-400 focus:ring-2 focus:ring-primary-100 outline-none transition-all bg-surface-bright"
          :class="{ 'border-red-400': errors.grade_level }"
        >
          <option value="">
            {{ t('expert.selectGrade') }}
          </option>
          <option value="السنة 1">
            {{ t('grades.year1') }}
          </option>
          <option value="السنة 2">
            {{ t('grades.year2') }}
          </option>
          <option value="السنة 3">
            {{ t('grades.year3') }}
          </option>
          <option value="السنة 4">
            {{ t('grades.year4') }}
          </option>
          <option value="السنة 5">
            {{ t('grades.year5') }}
          </option>
        </select>
        <p
          v-if="errors.grade_level"
          class="error-message text-red-500 text-sm mt-1"
        >
          {{ errors.grade_level }}
        </p>
      </div>

      <!-- Domain -->
      <div>
        <label
          for="domain"
          class="block text-sm font-medium text-warm-700 mb-1"
        >
          {{ t('expert.domain') }}
        </label>
        <input
          id="domain"
          v-model="form.domain"
          type="text"
          data-testid="domain-input"
          class="w-full px-4 py-2.5 rounded-xl border-2 border-warm-200 focus:border-primary-400 focus:ring-2 focus:ring-primary-100 outline-none transition-all bg-surface-bright"
          :class="{ 'border-red-400': errors.domain }"
          :placeholder="t('expert.domainPlaceholder')"
        >
        <p
          v-if="errors.domain"
          class="error-message text-red-500 text-sm mt-1"
        >
          {{ errors.domain }}
        </p>
      </div>

      <!-- Competency ID -->
      <div>
        <label
          for="competency_id"
          class="block text-sm font-medium text-warm-700 mb-1"
        >
          {{ t('expert.competency') }}
        </label>
        <input
          id="competency_id"
          v-model="form.competency_id"
          type="text"
          data-testid="competency-input"
          class="w-full px-4 py-2.5 rounded-xl border-2 border-warm-200 focus:border-primary-400 focus:ring-2 focus:ring-primary-100 outline-none transition-all bg-surface-bright font-mono text-sm"
          :class="{ 'border-red-400': errors.competency_id }"
          placeholder="MATH-4-NUM-01"
        >
        <p
          v-if="errors.competency_id"
          class="error-message text-red-500 text-sm mt-1"
        >
          {{ errors.competency_id }}
        </p>
      </div>

      <!-- Status -->
      <div v-if="isEditMode">
        <label
          for="status"
          class="block text-sm font-medium text-warm-700 mb-1"
        >
          {{ t('expert.status') }}
        </label>
        <select
          id="status"
          v-model="form.status"
          data-testid="status-input"
          class="w-full px-4 py-2.5 rounded-xl border-2 border-warm-200 focus:border-primary-400 focus:ring-2 focus:ring-primary-100 outline-none transition-all bg-surface-bright"
        >
          <option value="DRAFT">
            {{ t('expert.draft') }}
          </option>
          <option value="PUBLISHED">
            {{ t('expert.published') }}
          </option>
        </select>
      </div>

      <!-- Actions -->
      <div class="flex gap-3 pt-4">
        <button
          type="submit"
          data-testid="submit-button"
          class="flex-1 px-6 py-3 bg-primary-500 hover:bg-primary-600 text-on-primary font-semibold rounded-xl transition-colors shadow-soft"
        >
          {{ t('expert.save') }}
        </button>
        <button
          type="button"
          data-testid="cancel-button"
          class="px-6 py-3 bg-warm-200 hover:bg-warm-300 text-warm-700 font-semibold rounded-xl transition-colors"
          @click="handleCancel"
        >
          {{ t('expert.cancel') }}
        </button>
      </div>
    </form>
  </div>
</template>
