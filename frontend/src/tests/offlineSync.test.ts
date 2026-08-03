import { describe, it, expect, beforeEach, vi } from 'vitest'
import { offlineStore, offlineDB, type OfflineQuestion, type OfflineSession } from '@/stores/offlineModule'
import { diagnosticService } from '@/services/diagnosticService'
import { mount } from '@vue/test-utils'
import NetworkStatusIndicator from '@/components/NetworkStatusIndicator.vue'
import { api } from '@/services/api'

vi.mock('@/composables/useOfflineSync', () => ({
  useOfflineSync: () => ({
    isOnline: false,
    isSyncing: false,
    pendingCount: 2,
    syncNow: vi.fn(),
  }),
}))

vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string, defaultVal: string) => defaultVal || key,
  }),
}))

describe('Story 5.3 Offline & Question Pre-Fetch Unit Tests', () => {
  let mockQuestions: OfflineQuestion[] = []
  let mockSessions: OfflineSession[] = []

  beforeEach(() => {
    mockQuestions = []
    mockSessions = []

    vi.spyOn(offlineDB.questions, 'bulkPut').mockImplementation(async (items: any) => {
      mockQuestions.push(...items)
      return items.map((_: any, i: number) => `id-${i}`) as any
    })

    vi.spyOn(offlineDB.questions, 'where').mockImplementation((field: string) => {
      return {
        equals: (val: any) => ({
          toArray: async () => mockQuestions.filter((q: any) => q[field] === val),
        }),
      } as any
    })

    vi.spyOn(offlineDB.sessions, 'where').mockImplementation((field: string) => {
      return {
        equals: (val: any) => ({
          toArray: async () => mockSessions.filter((s: any) => s[field] === val),
        }),
      } as any
    })

    vi.spyOn(offlineDB.sessions, 'update').mockImplementation(async (id: any, changes: any) => {
      const session = mockSessions.find((s) => s.id === id)
      if (session) {
        Object.assign(session, changes)
      }
      return 1
    })
  })

  it('cacheQuestions stores questions with default module_id if missing', async () => {
    const questionsInput: OfflineQuestion[] = [
      {
        id: 'q-1',
        module_id: '',
        content: { text: 'Question 1', type: 'multiple_choice', options: ['A', 'B'] },
        difficulty_level: 1,
        estimated_time_sec: 30,
      },
    ]

    await offlineStore.cacheQuestions('mod-100', questionsInput)
    expect(mockQuestions.length).toBe(1)
    expect(mockQuestions[0].module_id).toBe('mod-100')
  })

  it('getCachedQuestions retrieves questions filtered by module_id', async () => {
    mockQuestions = [
      {
        id: 'q-1',
        module_id: 'mod-1',
        content: { text: 'Q1', type: 'multiple_choice' },
        difficulty_level: 1,
        estimated_time_sec: 20,
      },
      {
        id: 'q-2',
        module_id: 'mod-2',
        content: { text: 'Q2', type: 'multiple_choice' },
        difficulty_level: 2,
        estimated_time_sec: 20,
      },
    ]

    const result = await offlineStore.getCachedQuestions('mod-1')
    expect(result.length).toBe(1)
    expect(result[0].id).toBe('q-1')
  })

  it('getPendingSyncSessions and markSessionSynced update offline session state', async () => {
    mockSessions = [
      {
        id: 'session-1',
        student_id: 'std-1',
        module_id: 'mod-1',
        status: 'SYNC_PENDING',
        started_at: new Date(),
        answers: [],
      },
    ]

    const pending = await offlineStore.getPendingSyncSessions()
    expect(pending.length).toBe(1)
    expect(pending[0].id).toBe('session-1')

    await offlineStore.markSessionSynced('session-1')
    expect(mockSessions[0].status).toBe('COMPLETED')
  })

  it('preFetchModuleQuestions fetches from API and caches questions when online', async () => {
    const apiQuestions = [
      {
        id: 'q-api-1',
        content: { text: 'API Question', type: 'text' },
        difficulty_level: 1,
        estimated_time_sec: 45,
      },
    ]
    vi.spyOn(api, 'get').mockResolvedValueOnce({ data: apiQuestions } as any)

    const questions = await diagnosticService.preFetchModuleQuestions('mod-api')
    expect(questions.length).toBe(1)
    expect(questions[0].id).toBe('q-api-1')
    expect(mockQuestions.length).toBe(1)
    expect(mockQuestions[0].module_id).toBe('mod-api')
  })

  it('preFetchModuleQuestions falls back to Dexie cache when API fails or offline', async () => {
    mockQuestions = [
      {
        id: 'q-cached-1',
        module_id: 'mod-fail',
        content: { text: 'Cached Question', type: 'text' },
        difficulty_level: 1,
        estimated_time_sec: 30,
      },
    ]
    vi.spyOn(api, 'get').mockRejectedValueOnce(new Error('Network error'))

    const questions = await diagnosticService.preFetchModuleQuestions('mod-fail')
    expect(questions.length).toBe(1)
    expect(questions[0].id).toBe('q-cached-1')
  })

  it('getNextQuestionOffline returns question at specific index', async () => {
    mockQuestions = [
      {
        id: 'q-0',
        module_id: 'mod-next',
        content: { text: 'First Question', type: 'multiple_choice' },
        difficulty_level: 1,
        estimated_time_sec: 30,
      },
      {
        id: 'q-1',
        module_id: 'mod-next',
        content: { text: 'Second Question', type: 'multiple_choice' },
        difficulty_level: 2,
        estimated_time_sec: 30,
      },
    ]

    const first = await diagnosticService.getNextQuestionOffline('mod-next', 0)
    expect(first?.id).toBe('q-0')

    const second = await diagnosticService.getNextQuestionOffline('mod-next', 1)
    expect(second?.id).toBe('q-1')

    const outOfBounds = await diagnosticService.getNextQuestionOffline('mod-next', 5)
    expect(outOfBounds).toBeNull()
  })

  it('renders NetworkStatusIndicator banner when offline', () => {
    const wrapper = mount(NetworkStatusIndicator)
    expect(wrapper.text()).toContain('أنت تعمل حالياً بدون اتصال بالإنترنت')
    expect(wrapper.text()).toContain('2')
  })
})
