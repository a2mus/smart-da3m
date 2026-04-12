import { api } from './api'

export interface KnowledgeAtom {
  id: string
  competency_id: string
  remediation_type: 'AUDIO_VISUAL' | 'SIMULATION' | 'MIND_MAP'
  content: {
    title: string
    description: string
    media_url?: string
    interactive_data?: any
  }
}

export interface RemediationPath {
  id: string
  student_id: string
  competency_id: string
  status: 'IN_PROGRESS' | 'COMPLETED' | 'FAILED' | 'ABANDONED'
  atoms: KnowledgeAtom[]
  atoms_completed: string[]
  progress_percent: number
  current_difficulty: number
  started_at: string
  completed_at: string | null
}

export interface AtomCompletion {
  atom_id: string
  atoms_completed: number
  total_atoms: number
  progress_percent: number
  new_difficulty: number
  next_atom: KnowledgeAtom | null
  recommendation: string | null
}

export interface PassportQuestion {
  id: string
  content: {
    text: string
    type: 'multiple_choice' | 'text' | 'interactive'
    options?: string[]
    correct_answer?: string
  }
  difficulty_level: number
}

export interface PassportEvaluation {
  passed: boolean
  accuracy: number
  correct_count: number
  total_questions: number
  previous_mastery_level: string
  new_mastery_level: string
  badge_earned: string | null
  alert_triggered: boolean
  message: string
}

class RemediationService {
  async getPathway(competencyId: string, studentGroup = 'B'): Promise<RemediationPath> {
    const response = await api.get(`/remediation/pathway/${competencyId}`, {
      params: { student_group: studentGroup },
    })
    return response.data
  }

  async completeAtom(atomId: string, data: {
    time_spent_ms: number
    interactions_count: number
    is_correct: boolean
  }): Promise<AtomCompletion> {
    const response = await api.post(`/remediation/atoms/${atomId}/complete`, data)
    return response.data
  }

  async getStatus(competencyId: string): Promise<{
    competency_id: string
    status: string
    atoms_completed: string[]
    progress_percent: number
    can_take_passport: boolean
  }> {
    const response = await api.get(`/remediation/status/${competencyId}`)
    return response.data
  }

  async getPassportQuestions(competencyId: string): Promise<{
    competency_id: string
    questions: PassportQuestion[]
    assessment_id: string
  }> {
    const response = await api.get(`/remediation/passport/questions/${competencyId}`)
    return response.data
  }

  async evaluatePassport(competencyId: string, answers: {
    question_id: string
    answer: string
    time_ms: number
  }[]): Promise<PassportEvaluation> {
    const response = await api.post('/remediation/passport/evaluate', {
      competency_id: competencyId,
      answers,
    })
    return response.data
  }
}

export const remediationService = new RemediationService()
