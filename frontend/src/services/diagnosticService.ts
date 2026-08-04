import { api } from './api'
import { offlineStore, type OfflineQuestion } from '@/stores/offlineModule'

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

export interface ActiveDiagnosticSession {
  session_id: string
  module_id: string
  question_number: number
  total_questions: number
  started_at: string
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
  async preFetchModuleQuestions(moduleId: string): Promise<Question[]> {
    if (typeof navigator !== 'undefined' && !navigator.onLine) {
      const cached = await offlineStore.getCachedQuestions(moduleId)
      return cached.map((q) => ({
        id: q.id,
        content: q.content,
        difficulty_level: q.difficulty_level,
        estimated_time_sec: q.estimated_time_sec,
      }))
    }

    try {
      let rawQuestions: any = []
      try {
        const response = await api.get('/diagnostic/questions', { params: { module_id: moduleId } })
        rawQuestions = response.data
      } catch {
        const response = await api.get(`/diagnostic/module/${moduleId}/questions`)
        rawQuestions = response.data
      }

      const questionList: Question[] = Array.isArray(rawQuestions)
        ? rawQuestions
        : (rawQuestions?.questions || rawQuestions?.items || [])

      const offlineQuestions: OfflineQuestion[] = questionList.map((q) => ({
        id: q.id,
        module_id: moduleId,
        content: q.content,
        difficulty_level: q.difficulty_level,
        estimated_time_sec: q.estimated_time_sec,
      }))

      await offlineStore.cacheQuestions(moduleId, offlineQuestions)
      return questionList
    } catch (err) {
      console.warn('Failed to pre-fetch questions online, falling back to cache:', err)
      const cached = await offlineStore.getCachedQuestions(moduleId)
      return cached.map((q) => ({
        id: q.id,
        content: q.content,
        difficulty_level: q.difficulty_level,
        estimated_time_sec: q.estimated_time_sec,
      }))
    }
  }

  async getNextQuestionOffline(moduleId: string, currentIndex: number): Promise<Question | null> {
    const cached = await offlineStore.getCachedQuestions(moduleId)
    if (!cached || cached.length === 0 || currentIndex < 0 || currentIndex >= cached.length) {
      return null
    }
    const q = cached[currentIndex]
    return {
      id: q.id,
      content: q.content,
      difficulty_level: q.difficulty_level,
      estimated_time_sec: q.estimated_time_sec,
    }
  }

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

  async getActiveSession(): Promise<ActiveDiagnosticSession | null> {
    try {
      const response = await api.get('/diagnostic/active-session')
      return response.data
    } catch {
      return null
    }
  }

  async abandonSession(sessionId: string): Promise<void> {
    await api.post(`/diagnostic/session/${sessionId}/abandon`)
  }
}

export const diagnosticService = new DiagnosticService()
