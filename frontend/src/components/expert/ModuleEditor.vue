<script setup lang="ts">
import { reactive, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

export interface ModuleForm {
  title?: string
  description?: string
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
    title?: string
    description?: string
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
  title: props.module?.title ?? '',
  description: props.module?.description ?? '',
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
  <div class="bg-surface-bright rounded-2xl p-6 shadow-soft border border-outline-variant">
    <h2 class="text-2xl font-bold text-primary mb-6 text-start">
      {{ title }}
    </h2>

    <form
      class="space-y-5"
      @submit.prevent="handleSubmit"
    >
      <!-- Title -->
      <div>
        <label
          for="title"
          class="block text-sm font-medium text-on-surface mb-1 text-start"
        >
          {{ t('expert.moduleTitle', 'Module Title') }}
        </label>
        <input
          id="title"
          v-model="form.title"
          type="text"
          data-testid="title-input"
          class="w-full px-4 py-2.5 rounded-xl border border-outline-variant focus:border-primary focus:ring-2 focus:ring-primary-container outline-none transition-all bg-surface-container-low text-on-surface"
          :placeholder="t('expert.titlePlaceholder', 'Enter module title')"
        >
      </div>

      <!-- Description -->
      <div>
        <label
          for="description"
          class="block text-sm font-medium text-on-surface mb-1 text-start"
        >
          {{ t('expert.moduleDescription', 'Description') }}
        </label>
        <textarea
          id="description"
          v-model="form.description"
          rows="3"
          data-testid="description-input"
          class="w-full px-4 py-2.5 rounded-xl border border-outline-variant focus:border-primary focus:ring-2 focus:ring-primary-container outline-none transition-all bg-surface-container-low text-on-surface"
          :placeholder="t('expert.descriptionPlaceholder', 'Enter module description')"
        />
      </div>

      <!-- Subject -->
      <div>
        <label
          for="subject"
          class="block text-sm font-medium text-on-surface mb-1 text-start"
        >
          {{ t('expert.subject') }}
        </label>
        <input
          id="subject"
          v-model="form.subject"
          type="text"
          data-testid="subject-input"
          class="w-full px-4 py-2.5 rounded-xl border border-outline-variant focus:border-primary focus:ring-2 focus:ring-primary-container outline-none transition-all bg-surface-container-low text-on-surface"
          :class="{ 'border-error': errors.subject }"
          :placeholder="t('expert.subjectPlaceholder')"
        >
        <p
          v-if="errors.subject"
          class="error-message text-error text-sm mt-1 text-start"
        >
          {{ errors.subject }}
        </p>
      </div>

      <!-- Grade Level -->
      <div>
        <label
          for="grade_level"
          class="block text-sm font-medium text-on-surface mb-1 text-start"
        >
          {{ t('expert.gradeLevel') }}
        </label>
        <select
          id="grade_level"
          v-model="form.grade_level"
          data-testid="grade-level-input"
          class="w-full px-4 py-2.5 rounded-xl border border-outline-variant focus:border-primary focus:ring-2 focus:ring-primary-container outline-none transition-all bg-surface-container-low text-on-surface"
          :class="{ 'border-error': errors.grade_level }"
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
          class="error-message text-error text-sm mt-1 text-start"
        >
          {{ errors.grade_level }}
        </p>
      </div>

      <!-- Domain -->
      <div>
        <label
          for="domain"
          class="block text-sm font-medium text-on-surface mb-1 text-start"
        >
          {{ t('expert.domain') }}
        </label>
        <input
          id="domain"
          v-model="form.domain"
          type="text"
          data-testid="domain-input"
          class="w-full px-4 py-2.5 rounded-xl border border-outline-variant focus:border-primary focus:ring-2 focus:ring-primary-container outline-none transition-all bg-surface-container-low text-on-surface"
          :class="{ 'border-error': errors.domain }"
          :placeholder="t('expert.domainPlaceholder')"
        >
        <p
          v-if="errors.domain"
          class="error-message text-error text-sm mt-1 text-start"
        >
          {{ errors.domain }}
        </p>
      </div>

      <!-- Competency ID -->
      <div>
        <label
          for="competency_id"
          class="block text-sm font-medium text-on-surface mb-1 text-start"
        >
          {{ t('expert.competency') }}
        </label>
        <input
          id="competency_id"
          v-model="form.competency_id"
          type="text"
          data-testid="competency-input"
          class="w-full px-4 py-2.5 rounded-xl border border-outline-variant focus:border-primary focus:ring-2 focus:ring-primary-container outline-none transition-all bg-surface-container-low text-on-surface"
          :class="{ 'border-error': errors.competency_id }"
          :placeholder="t('expert.competencyPlaceholder')"
        >
        <p
          v-if="errors.competency_id"
          class="error-message text-error text-sm mt-1 text-start"
        >
          {{ errors.competency_id }}
        </p>
      </div>

      <!-- Status -->
      <div>
        <label
          for="status"
          class="block text-sm font-medium text-on-surface mb-1 text-start"
        >
          {{ t('expert.status', 'Status') }}
        </label>
        <select
          id="status"
          v-model="form.status"
          class="w-full px-4 py-2.5 rounded-xl border border-outline-variant focus:border-primary focus:ring-2 focus:ring-primary-container outline-none transition-all bg-surface-container-low text-on-surface"
        >
          <option value="DRAFT">
            {{ t('expert.draft', 'Draft') }}
          </option>
          <option value="PUBLISHED">
            {{ t('expert.published', 'Published') }}
          </option>
        </select>
      </div>

      <!-- Buttons -->
      <div class="flex justify-end gap-3 pt-4">
        <button
          type="button"
          data-testid="cancel-button"
          class="px-5 py-2.5 rounded-xl border border-outline-variant hover:bg-surface-container text-on-surface transition-colors font-medium"
          @click="handleCancel"
        >
          {{ t('common.cancel') }}
        </button>
        <button
          type="submit"
          data-testid="submit-button"
          class="px-5 py-2.5 rounded-xl bg-primary text-on-primary hover:bg-primary/90 transition-colors font-medium shadow-sm"
        >
          {{ isEditMode ? t('common.save') : t('common.create') }}
        </button>
      </div>
    </form>
  </div>
</template>
