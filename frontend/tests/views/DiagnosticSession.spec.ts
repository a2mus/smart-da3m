import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import DiagnosticRunner from '@/components/student/DiagnosticRunner.vue'

const i18n = createI18n({
  legacy: false,
  locale: 'ar',
  messages: {
    ar: {
      'diagnostic.title': 'اختبار تشخيصي',
      'diagnostic.progress': 'التقدم',
      'diagnostic.question': 'سؤال',
      'diagnostic.of': 'من',
      'diagnostic.submit': 'تأكيد الإجابة',
      'diagnostic.next': 'التالي',
      'diagnostic.previous': 'السابق',
      'diagnostic.finish': 'إنهاء',
      'diagnostic.loading': 'جاري التحميل...',
      'diagnostic.error': 'حدث خطأ',
      'diagnostic.results': 'النتائج',
      'diagnostic.congratulations': 'تهانينا!',
    },
    fr: {
      'diagnostic.title': 'Test Diagnostique',
      'diagnostic.progress': 'Progression',
      'diagnostic.question': 'Question',
      'diagnostic.of': 'sur',
      'diagnostic.submit': 'Confirmer',
      'diagnostic.next': 'Suivant',
      'diagnostic.previous': 'Précédent',
      'diagnostic.finish': 'Terminer',
      'diagnostic.loading': 'Chargement...',
      'diagnostic.error': 'Une erreur est survenue',
      'diagnostic.results': 'Résultats',
      'diagnostic.congratulations': 'Félicitations!',
    },
  },
})

vi.mock('@/services/diagnosticService', () => ({
  diagnosticService: {
    startSession: vi.fn(),
    submitAnswer: vi.fn(),
    getResults: vi.fn(),
    startDiagnostic: vi.fn(),
  },
}))

vi.mock('@/stores/offlineModule', () => ({
  offlineStore: {
    createOfflineSession: vi.fn().mockResolvedValue(true),
    updateSessionAnswers: vi.fn().mockResolvedValue(true),
    completeOfflineSession: vi.fn().mockResolvedValue(true),
  }
}))

vi.mock('vue-router', () => ({
  useRoute: vi.fn(() => ({ params: { moduleId: 'test-module-id' } })),
  useRouter: vi.fn(() => ({ push: vi.fn() })),
}))

describe('DiagnosticRunner', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('Component Rendering', () => {
    it('renders the diagnostic runner interface', () => {
      const wrapper = mount(DiagnosticRunner, {
        props: { moduleId: 'test-module-id' },
        global: { plugins: [i18n] },
      })
      expect(wrapper.find('[data-testid="diagnostic-runner"]').exists()).toBe(true)
    })

    it('displays loading state initially', () => {
      const wrapper = mount(DiagnosticRunner, {
        props: { moduleId: 'test-module-id' },
        global: { plugins: [i18n] },
      })
      expect(wrapper.find('[data-testid="loading-state"]').exists()).toBe(true)
    })
  })

  describe('Question Display', () => {
    it('renders question text when loaded', async () => {
      const { diagnosticService } = await import('@/services/diagnosticService')
      diagnosticService.startDiagnostic.mockResolvedValue({
        session_id: 'session-123',
        question: {
          id: 'q1',
          content: { text: 'What is 2 + 2?', type: 'multiple_choice', options: ['3', '4', '5'] },
        },
      })

      const wrapper = mount(DiagnosticRunner, {
        props: { moduleId: 'test-module-id' },
        global: { plugins: [i18n] },
      })

      await flushPromises()
      expect(wrapper.text()).toContain('What is 2 + 2?')
    })

    it('renders multiple choice options', async () => {
      const { diagnosticService } = await import('@/services/diagnosticService')
      diagnosticService.startDiagnostic.mockResolvedValue({
        session_id: 'session-123',
        question: {
          id: 'q1',
          content: { text: 'Test?', type: 'multiple_choice', options: ['A', 'B', 'C'] },
        },
      })

      const wrapper = mount(DiagnosticRunner, {
        props: { moduleId: 'test-module-id' },
        global: { plugins: [i18n] },
      })

      await flushPromises()
      const options = wrapper.findAll('[data-testid="answer-option"]')
      expect(options.length).toBe(3)
    })
  })

  describe('Answer Submission', () => {
    it('submits answer and loads next question', async () => {
      const { diagnosticService } = await import('@/services/diagnosticService')
      diagnosticService.startDiagnostic.mockResolvedValue({
        session_id: 'session-123',
        question: { id: 'q1', content: { text: 'Q1?', type: 'multiple_choice', options: ['A', 'B'] } },
      })
      diagnosticService.submitAnswer.mockResolvedValue({
        next_question: { id: 'q2', content: { text: 'Q2?', type: 'multiple_choice', options: ['C', 'D'] } },
        is_complete: false,
      })

      const wrapper = mount(DiagnosticRunner, {
        props: { moduleId: 'test-module-id' },
        global: { plugins: [i18n] },
      })

      await flushPromises()
      const answerOptions = wrapper.findAll('[data-testid="answer-option"]')
      if (answerOptions.length > 0) {
        await answerOptions[0].trigger('click')
      }
      await wrapper.find('[data-testid="submit-button"]').trigger('click')
      await flushPromises()

      expect(diagnosticService.submitAnswer).toHaveBeenCalled()
      expect(wrapper.text()).toContain('Q2?')
    })

    it('shows completion screen when session ends', async () => {
      const { diagnosticService } = await import('@/services/diagnosticService')
      diagnosticService.startDiagnostic.mockResolvedValue({
        session_id: 'session-123',
        question: { id: 'q1', content: { text: 'Last?', type: 'multiple_choice', options: ['A'] } },
      })
      diagnosticService.submitAnswer.mockResolvedValue({
        next_question: null,
        is_complete: true,
        results: { mastery_level: 'PROFICIENT', recommended_group: 'B' },
      })

      const wrapper = mount(DiagnosticRunner, {
        props: { moduleId: 'test-module-id' },
        global: { plugins: [i18n] },
      })

      await flushPromises()
      const answerOptions = wrapper.findAll('[data-testid="answer-option"]')
      if (answerOptions.length > 0) {
        await answerOptions[0].trigger('click')
      }
      await wrapper.find('[data-testid="submit-button"]').trigger('click')
      await flushPromises()

      expect(wrapper.find('[data-testid="results-screen"]').exists()).toBe(true)
    })
  })
})
