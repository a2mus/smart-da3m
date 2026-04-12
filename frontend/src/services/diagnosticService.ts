import { api } from './api'

export interface DiagnosticSession {
  id: string
  student_id: string
  module_id: string
  status: 'IN_PROGRESS' | 'COMPLETED' | 'ABANDONED'
  recommended_group: 'A' | 'B' | 'C' | null
  started_at: string
  completed_at: string | null
}

export interface Question {
  id: string
  content: {
    text: string
    type: 'multiple_choice' | 'text' | 'interactive'
    options?: string[]
    correct_answer?: string
    media_urls?: string[]
  }
  difficulty_level: number
  estimated_time_sec: number
}

export interface StartDiagnosticResponse {
  session_id: string
  question: Question
  question_number: number
}

export interface AnswerSubmitRequest {
  session_id: string
  question_id: string
  answer: string
  time_ms: number
}

export interface AnswerSubmitResponse {
  is_correct: boolean
  error_classification: 'RESOURCE' | 'PROCESS' | 'INCIDENTAL' | 'NONE'
  current_mastery: number
  mastery_level: 'NOT_STARTED' | 'ATTEMPTED' | 'FAMILIAR' | 'PROFICIENT' | 'MASTERED'
  next_question: Question | null
  is_complete: boolean
  accuracy: number
}

export interface DiagnosticResults {
  session_id: string
  mastery_probability: number
  mastery_level: string
  recommended_group: 'A' | 'B' | 'C'
  total_questions: number
  correct_answers: number
  accuracy: number
  completed_at: string
}

export interface CompetencyProfile {
  id: string
  student_id: string
  competency_id: string
  mastery_level: string
  p_learned: number
  last_assessed: string
}

class DiagnosticService {
  async startDiagnostic(moduleId: string): Promise<StartDiagnosticResponse> {
    const response = await api.post('/diagnostic/start', { module_id: moduleId })
    return response.data
  }

  async submitAnswer(data: AnswerSubmitRequest): Promise<AnswerSubmitResponse> {
    const response = await api.post('/diagnostic/answer', data)
    return response.data
  }

  async getResults(sessionId: string): Promise<DiagnosticResults> {
    const response = await api.get(`/diagnostic/results/${sessionId}`)
    return response.data
  }

  async getCompetencyProfiles(): Promise<CompetencyProfile[]> {
    const response = await api.get('/diagnostic/competency-profile')
    return response.data
  }
}

export const diagnosticService = new DiagnosticService()
