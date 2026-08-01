import { describe, it, expect, beforeEach, vi } from 'vitest'
import { offlineStore, offlineDB } from '@/stores/offlineModule'

describe('offlineModule store', () => {
  let mockPending: any[] = []

  beforeEach(() => {
    mockPending = []
    vi.spyOn(offlineDB.pending_answers, 'add').mockImplementation(async (item: any) => {
      const id = mockPending.length + 1
      const record = { ...item, id }
      mockPending.push(record)
      return id
    })
    vi.spyOn(offlineDB.pending_answers, 'where').mockImplementation((field: string) => {
      return {
        equals: (val: any) => ({
          toArray: async () => mockPending.filter((x) => x[field] === val),
        }),
      } as any
    })
    vi.spyOn(offlineDB.pending_answers, 'update').mockImplementation(async (id: any, changes: any) => {
      const item = mockPending.find((x) => x.id === id)
      if (item) Object.assign(item, changes)
      return 1
    })
    vi.spyOn(offlineDB.pending_answers, 'get').mockImplementation(async (id: any) => {
      return mockPending.find((x) => x.id === id)
    })
  })

  it('queues pending answers to Dexie write-behind buffer', async () => {
    const id = await offlineStore.queueAnswer({
      session_id: 'session-123',
      question_id: 'q-456',
      answer: '4',
      time_ms: 5000,
      sync_status: 'PENDING',
    })

    expect(id).toBeDefined()

    const pending = await offlineStore.getPendingAnswers()
    expect(pending.length).toBe(1)
    expect(pending[0].session_id).toBe('session-123')
    expect(pending[0].question_id).toBe('q-456')
    expect(pending[0].answer).toBe('4')
    expect(pending[0].sync_status).toBe('PENDING')
  })

  it('marks pending answer as SYNCED upon successful server sync', async () => {
    const id = await offlineStore.queueAnswer({
      session_id: 'session-123',
      question_id: 'q-789',
      answer: 'Option A',
      sync_status: 'PENDING',
    })

    await offlineStore.markAnswerSynced(id)

    const pending = await offlineStore.getPendingAnswers()
    expect(pending.length).toBe(0)

    const record = await offlineDB.pending_answers.get(id)
    expect(record?.sync_status).toBe('SYNCED')
  })

  it('retrieves pending answers in chronological order', async () => {
    const t1 = new Date('2026-08-01T10:00:00Z')
    const t2 = new Date('2026-08-01T10:05:00Z')

    await offlineStore.queueAnswer({
      session_id: 'session-1',
      question_id: 'q-2',
      answer: 'Second',
      sync_status: 'PENDING',
      created_at: t2,
    })

    await offlineStore.queueAnswer({
      session_id: 'session-1',
      question_id: 'q-1',
      answer: 'First',
      sync_status: 'PENDING',
      created_at: t1,
    })

    const pending = await offlineStore.getPendingAnswers()
    expect(pending.length).toBe(2)
    expect(pending[0].answer).toBe('First')
    expect(pending[1].answer).toBe('Second')
  })
})
