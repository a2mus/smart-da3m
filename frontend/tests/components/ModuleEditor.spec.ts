import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import ModuleEditor from '@/components/expert/ModuleEditor.vue'

const i18n = createI18n({
  legacy: false,
  locale: 'ar',
  messages: {
    ar: {
      'expert.moduleName': 'اسم الوحدة',
      'expert.subject': 'المادة',
      'expert.gradeLevel': 'المستوى الدراسي',
      'expert.domain': 'المجال',
      'expert.competency': 'الكفاءة',
      'expert.save': 'حفظ',
      'expert.cancel': 'إلغاء',
      'expert.createModule': 'إنشاء وحدة',
      'expert.editModule': 'تعديل وحدة',
      'validation.required': 'هذا الحقل مطلوب',
    },
    fr: {
      'expert.moduleName': 'Nom du module',
      'expert.subject': 'Matière',
      'expert.gradeLevel': 'Niveau',
      'expert.domain': 'Domaine',
      'expert.competency': 'Compétence',
      'expert.save': 'Enregistrer',
      'expert.cancel': 'Annuler',
      'expert.createModule': 'Créer un module',
      'expert.editModule': 'Modifier le module',
      'validation.required': 'Ce champ est requis',
    },
  },
})

vi.mock('@/services/api', () => ({
  api: {
    post: vi.fn(),
    patch: vi.fn(),
    get: vi.fn(),
  },
}))

describe('ModuleEditor', () => {
  let wrapper: VueWrapper

  beforeEach(() => {
    setActivePinia(createPinia())
  })

  const mountComponent = (props = {}) => {
    return mount(ModuleEditor, {
      props: { ...props },
      global: {
        plugins: [createPinia(), i18n],
      },
    })
  }

  describe('Create Mode', () => {
    it('renders create mode correctly', () => {
      wrapper = mountComponent({ mode: 'create' })
      expect(wrapper.find('h2').text()).toContain('إنشاء وحدة')
      expect(wrapper.find('form').exists()).toBe(true)
    })

    it('displays all required form fields', () => {
      wrapper = mountComponent({ mode: 'create' })
      expect(wrapper.find('[data-testid="subject-input"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="grade-level-input"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="domain-input"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="competency-input"]').exists()).toBe(true)
    })

    it('validates required fields', async () => {
      wrapper = mountComponent({ mode: 'create' })
      const submitButton = wrapper.find('[data-testid="submit-button"]')
      await submitButton.trigger('click')
      await wrapper.vm.$nextTick()
      expect(wrapper.findAll('.error-message').length).toBeGreaterThan(0)
    })

    it('emits save event with form data when valid', async () => {
      wrapper = mountComponent({ mode: 'create' })
      await wrapper.find('[data-testid="subject-input"]').setValue('Mathematics')
      await wrapper.find('[data-testid="grade-level-input"]').setValue('السنة 4')
      await wrapper.find('[data-testid="domain-input"]').setValue('Numbers & Operations')
      await wrapper.find('[data-testid="competency-input"]').setValue('MATH-4-NUM-01')
      await wrapper.find('form').trigger('submit.prevent')
      expect(wrapper.emitted('save')).toBeTruthy()
      expect(wrapper.emitted('save')![0][0]).toMatchObject({
        subject: 'Mathematics',
        grade_level: 'السنة 4',
        domain: 'Numbers & Operations',
        competency_id: 'MATH-4-NUM-01',
      })
    })

    it('emits cancel event when cancel button clicked', async () => {
      wrapper = mountComponent({ mode: 'create' })
      await wrapper.find('[data-testid="cancel-button"]').trigger('click')
      expect(wrapper.emitted('cancel')).toBeTruthy()
    })
  })

  describe('Edit Mode', () => {
    const mockModule = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      subject: 'Mathematics',
      grade_level: 'السنة 4',
      domain: 'Numbers & Operations',
      competency_id: 'MATH-4-NUM-01',
      status: 'DRAFT',
      created_at: '2026-04-11T10:00:00Z',
    }

    it('renders edit mode with pre-filled data', () => {
      wrapper = mountComponent({ mode: 'edit', module: mockModule })
      expect(wrapper.find('h2').text()).toContain('تعديل وحدة')
      const subjectInput = wrapper.find('[data-testid="subject-input"]')
      expect((subjectInput.element as HTMLInputElement).value).toBe('Mathematics')
    })

    it('emits update event with modified data', async () => {
      wrapper = mountComponent({ mode: 'edit', module: mockModule })
      await wrapper.find('[data-testid="domain-input"]').setValue('Advanced Numbers')
      await wrapper.find('form').trigger('submit.prevent')
      expect(wrapper.emitted('update')).toBeTruthy()
      expect(wrapper.emitted('update')![0][0]).toMatchObject({
        id: mockModule.id,
        domain: 'Advanced Numbers',
      })
    })
  })

  describe('Accessibility', () => {
    it('has proper form labels', () => {
      wrapper = mountComponent({ mode: 'create' })
      const labels = wrapper.findAll('label')
      expect(labels.length).toBeGreaterThanOrEqual(4)
    })
  })
})
