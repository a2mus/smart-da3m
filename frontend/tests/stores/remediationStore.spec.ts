import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useRemediationStore } from '@/stores/remediationStore'
import { remediationService } from '@/services/remediationService'

vi.mock('@/services/remediationService', () => ({
  remediationService: {
    getPathway: vi.fn(),
    startPathway: vi.fn(),
    completeAtom: vi.fn(),
    getPassportQuestions: vi.fn(),
    evaluatePassport: vi.fn(),
  },
}))

describe('remediationStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initializes with default empty state', () => {
    const store = useRemediationStore()
    expect(store.pathway).toBeNull()
    expect(store.currentAtomIndex).toBe(0)
    expect(store.loading).toBe(false)
    expect(store.actionLoading).toBe(false)
    expect(store.error).toBeNull()
    expect(store.passportQuestions).toEqual([])
    expect(store.passportEvaluation).toBeNull()
    expect(store.currentAtom).toBeNull()
    expect(store.atomsCompleted).toEqual([])
    expect(store.progressPercent).toBe(0)
    expect(store.canTakePassport).toBe(false)
  })

  it('fetches remediation pathway and sets currentAtomIndex to first uncompleted atom', async () => {
    const mockPathway = {
      id: 'path-123',
      student_id: 'student-1',
      competency_id: 'comp-456',
      status: 'VALIDATED' as const,
      atoms: [
        { id: 'atom-1', competency_id: 'comp-456', remediation_type: 'AUDIO_VISUAL' as const, content: { title: 'Atom 1', description: 'Desc 1' } },
        { id: 'atom-2', competency_id: 'comp-456', remediation_type: 'SIMULATION' as const, content: { title: 'Atom 2', description: 'Desc 2' } },
      ],
      atoms_completed: ['atom-1'],
      progress_percent: 50,
      current_difficulty: 5,
      started_at: '2026-08-01T00:00:00Z',
      completed_at: null,
    }

    vi.mocked(remediationService.getPathway).mockResolvedValue(mockPathway)

    const store = useRemediationStore()
    await store.fetchPathway('comp-456')

    expect(remediationService.getPathway).toHaveBeenCalledWith('comp-456', 'B')
    expect(store.pathway).toEqual(mockPathway)
    expect(store.currentAtomIndex).toBe(1) // atom-1 completed, so atom-2 index 1 is first uncompleted
    expect(store.currentAtom?.id).toBe('atom-2')
    expect(store.atomsCompleted).toEqual(['atom-1'])
  })

  it('starts pathway and updates path status to IN_PROGRESS', async () => {
    const store = useRemediationStore()
    store.pathway = {
      id: 'path-123',
      student_id: 'student-1',
      competency_id: 'comp-456',
      status: 'VALIDATED',
      atoms: [],
      atoms_completed: [],
      progress_percent: 0,
      current_difficulty: 5,
      started_at: '2026-08-01T00:00:00Z',
      completed_at: null,
    }

    vi.mocked(remediationService.startPathway).mockResolvedValue({
      id: 'path-123',
      competency_id: 'comp-456',
      status: 'IN_PROGRESS',
      started_at: '2026-08-01T00:00:00Z',
      message: 'Pathway started',
    })

    await store.startPathway('path-123')

    expect(remediationService.startPathway).toHaveBeenCalledWith('path-123')
    expect(store.pathway?.status).toBe('IN_PROGRESS')
  })

  it('completes atom and updates progress and completed atoms', async () => {
    const store = useRemediationStore()
    store.pathway = {
      id: 'path-123',
      student_id: 'student-1',
      competency_id: 'comp-456',
      status: 'IN_PROGRESS',
      atoms: [
        { id: 'atom-1', competency_id: 'comp-456', remediation_type: 'AUDIO_VISUAL', content: { title: 'A1', description: 'D1' } },
        { id: 'atom-2', competency_id: 'comp-456', remediation_type: 'SIMULATION', content: { title: 'A2', description: 'D2' } },
      ],
      atoms_completed: [],
      progress_percent: 0,
      current_difficulty: 5,
      started_at: '2026-08-01T00:00:00Z',
      completed_at: null,
    }

    vi.mocked(remediationService.completeAtom).mockResolvedValue({
      atom_id: 'atom-1',
      atoms_completed: 1,
      total_atoms: 2,
      progress_percent: 50,
      new_difficulty: 6,
      next_atom: null,
      recommendation: null,
    })

    await store.completeAtom('atom-1')

    expect(remediationService.completeAtom).toHaveBeenCalledWith('atom-1', {
      time_spent_ms: 15000,
      interactions_count: 1,
      is_correct: true,
    })
    expect(store.atomsCompleted).toContain('atom-1')
    expect(store.progressPercent).toBe(50)
    expect(store.currentAtomIndex).toBe(1)
  })

  it('fetches passport questions and populates state', async () => {
    const mockQuestions = [
      { id: 'q1', content: { text: 'Question 1', type: 'multiple_choice' as const, options: ['A', 'B'] }, difficulty_level: 5 },
    ]

    vi.mocked(remediationService.getPassportQuestions).mockResolvedValue({
      competency_id: 'comp-456',
      questions: mockQuestions,
      assessment_id: 'assess-789',
    })

    const store = useRemediationStore()
    await store.fetchPassportQuestions('comp-456')

    expect(remediationService.getPassportQuestions).toHaveBeenCalledWith('comp-456')
    expect(store.passportQuestions).toEqual(mockQuestions)
  })

  it('evaluates passport assessment and updates state', async () => {
    const mockEval = {
      passed: true,
      accuracy: 1.0,
      correct_count: 1,
      total_questions: 1,
      previous_mastery_level: 'FAMILIAR',
      new_mastery_level: 'MASTERED',
      badge_earned: 'badge-123',
      alert_triggered: false,
      message: 'Passport passed!',
    }

    vi.mocked(remediationService.evaluatePassport).mockResolvedValue(mockEval)

    const store = useRemediationStore()
    store.pathway = {
      id: 'path-123',
      student_id: 'student-1',
      competency_id: 'comp-456',
      status: 'IN_PROGRESS',
      atoms: [],
      atoms_completed: [],
      progress_percent: 100,
      current_difficulty: 5,
      started_at: '2026-08-01T00:00:00Z',
      completed_at: null,
    }

    const answers = [{ question_id: 'q1', answer: 'A', time_ms: 5000 }]
    const result = await store.evaluatePassport('comp-456', answers)

    expect(remediationService.evaluatePassport).toHaveBeenCalledWith('comp-456', answers)
    expect(result).toEqual(mockEval)
    expect(store.passportEvaluation).toEqual(mockEval)
    expect(store.pathway.status).toBe('COMPLETED')
  })

  it('resets store state when reset is called', () => {
    const store = useRemediationStore()
    store.currentAtomIndex = 2
    store.error = 'Some error'

    store.reset()

    expect(store.pathway).toBeNull()
    expect(store.currentAtomIndex).toBe(0)
    expect(store.error).toBeNull()
  })
})
