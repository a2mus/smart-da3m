import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useOfflineSync } from '@/composables/useOfflineSync'
import { offlineStore } from '@/stores/offlineModule'
import { diagnosticService } from '@/services/diagnosticService'

describe('useOfflineSync composable', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('initializes isOnline from navigator.onLine and tracks network status', () => {
    const { isOnline } = useOfflineSync()
    expect(typeof isOnline.value).toBe('boolean')
  })

  it('queues an answer and updates pendingCount', async () => {
    vi.spyOn(offlineStore, 'queueAnswer').mockResolvedValue(42)
    vi.spyOn(offlineStore, 'getPendingAnswers').mockResolvedValue([
      {
        id: 42,
        session_id: 'sess-1',
        question_id: 'q-1',
        answer: 'opt-a',
        sync_status: 'PENDING',
        created_at: new Date(),
      },
    ])
    vi.spyOn(offlineStore, 'getPendingSyncSessions').mockResolvedValue([])

    const { queueAnswer, pendingCount } = useOfflineSync()

    const id = await queueAnswer({
      session_id: 'sess-1',
      question_id: 'q-1',
      answer: 'opt-a',
      sync_status: 'PENDING',
    })

    expect(id).toBe(42)
    expect(pendingCount.value).toBe(1)
  })

  it('queues completion for an offline session and updates pendingCount', async () => {
    vi.spyOn(offlineStore, 'completeOfflineSession').mockResolvedValue(undefined)
    vi.spyOn(offlineStore, 'getPendingAnswers').mockResolvedValue([])
    vi.spyOn(offlineStore, 'getPendingSyncSessions').mockResolvedValue([
      {
        id: 'sess-1',
        student_id: 'stud-1',
        module_id: 'mod-1',
        status: 'SYNC_PENDING',
        started_at: new Date(),
        answers: [],
      },
    ])

    const { queueCompletion, pendingCount } = useOfflineSync()

    await queueCompletion('sess-1')

    expect(offlineStore.completeOfflineSession).toHaveBeenCalledWith('sess-1')
    expect(pendingCount.value).toBe(1)
  })

  it('flushes pending answers when syncNow is called online', async () => {
    const pendingItem = {
      id: 10,
      session_id: 'sess-10',
      question_id: 'q-10',
      answer: 'ans-10',
      time_ms: 1200,
      sync_status: 'PENDING' as const,
      created_at: new Date(),
    }

    vi.spyOn(offlineStore, 'getPendingAnswers')
      .mockResolvedValueOnce([pendingItem])
      .mockResolvedValueOnce([])

    vi.spyOn(offlineStore, 'getPendingSyncSessions').mockResolvedValue([])
    vi.spyOn(diagnosticService, 'submitAnswer').mockResolvedValue({
      session_id: 'sess-10',
      question_number: 1,
      is_complete: false,
      accuracy: 1.0,
      current_mastery: 1.0,
      mastery_level: 'MASTERED',
      is_correct: true,
    })
    vi.spyOn(offlineStore, 'markAnswerSynced').mockResolvedValue(undefined)

    const { syncNow, pendingCount } = useOfflineSync()

    await syncNow()

    expect(diagnosticService.submitAnswer).toHaveBeenCalledWith({
      session_id: 'sess-10',
      question_id: 'q-10',
      answer: 'ans-10',
      time_ms: 1200,
    })
    expect(offlineStore.markAnswerSynced).toHaveBeenCalledWith(10)
    expect(pendingCount.value).toBe(0)
  })
})
