import { api } from './api'

export interface Module {
  id: string
  subject: string
  grade_level: string
  domain: string
  competency_id: string
  status: 'DRAFT' | 'PUBLISHED'
  created_at: string
  updated_at: string
}

export interface ModuleCreate {
  subject: string
  grade_level: string
  domain: string
  competency_id: string
  status?: 'DRAFT' | 'PUBLISHED'
}

export interface QuestionContent {
  text: string
  type: 'multiple_choice' | 'text' | 'interactive'
  options?: string[]
  correct_answer?: string
}

export interface Question {
  id: string
  module_id: string
  content: QuestionContent
  difficulty_level: number
  target_misconception_id?: string
  estimated_time_sec: number
  created_at: string
  updated_at: string
}

export interface QuestionCreate {
  module_id: string
  content: QuestionContent
  difficulty_level: number
  target_misconception_id?: string
  estimated_time_sec: number
}

export interface KnowledgeAtom {
  id: string
  competency_id: string
  remediation_type: 'AUDIO_VISUAL' | 'SIMULATION' | 'MIND_MAP'
  content: {
    title: string
    description: string
    media_url?: string
  }
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

class ContentService {
  // Module CRUD
  async getModules(): Promise<PaginatedResponse<Module>> {
    const response = await api.get('/content/modules')
    return response.data
  }

  async getModule(id: string): Promise<Module> {
    const response = await api.get(`/content/modules/${id}`)
    return response.data
  }

  async createModule(data: ModuleCreate): Promise<Module> {
    const response = await api.post('/content/modules', data)
    return response.data
  }

  async updateModule(id: string, data: Partial<ModuleCreate>): Promise<Module> {
    const response = await api.patch(`/content/modules/${id}`, data)
    return response.data
  }

  async deleteModule(id: string): Promise<void> {
    await api.delete(`/content/modules/${id}`)
  }

  // Question CRUD
  async getQuestions(moduleId?: string): Promise<PaginatedResponse<Question>> {
    const params = moduleId ? { module_id: moduleId } : {}
    const response = await api.get('/content/questions', { params })
    return response.data
  }

  async getQuestion(id: string): Promise<Question> {
    const response = await api.get(`/content/questions/${id}`)
    return response.data
  }

  async createQuestion(data: QuestionCreate): Promise<Question> {
    const response = await api.post('/content/questions', data)
    return response.data
  }

  async updateQuestion(id: string, data: Partial<QuestionCreate>): Promise<Question> {
    const response = await api.patch(`/content/questions/${id}`, data)
    return response.data
  }

  async deleteQuestion(id: string): Promise<void> {
    await api.delete(`/content/questions/${id}`)
  }

  async bulkImportQuestions(moduleId: string, questions: QuestionCreate[]): Promise<{ imported_count: number; imported_ids: string[] }> {
    const response = await api.post('/content/questions/bulk', {
      module_id: moduleId,
      questions,
    })
    return response.data
  }

  // Knowledge Atom CRUD
  async getKnowledgeAtoms(competencyId?: string): Promise<PaginatedResponse<KnowledgeAtom>> {
    const params = competencyId ? { competency_id: competencyId } : {}
    const response = await api.get('/content/knowledge-atoms', { params })
    return response.data
  }

  async createKnowledgeAtom(data: Omit<KnowledgeAtom, 'id' | 'created_at' | 'updated_at'>): Promise<KnowledgeAtom> {
    const response = await api.post('/content/knowledge-atoms', data)
    return response.data
  }
}

export const contentService = new ContentService()
