import Dexie, { type Table } from 'dexie'

export interface OfflineQuestion {
  id: string
  module_id: string
  content: {
    text: string
    type: 'multiple_choice' | 'text' | 'interactive'
    options?: string[]
    correct_answer?: string
    media_urls?: string[]
  }
  difficulty_level: number
  estimated_time_sec: number
  target_misconception_id?: string
}

export interface OfflineSession {
  id: string
  student_id: string
  module_id: string
  status: 'IN_PROGRESS' | 'COMPLETED' | 'SYNC_PENDING'
  started_at: Date
  completed_at?: Date
  answers: OfflineAnswer[]
}

export interface OfflineAnswer {
  question_id: string
  answer: string
  is_correct?: boolean
  time_ms: number
  answered_at: Date
}

export class OfflineDatabase extends Dexie {
  questions!: Table<OfflineQuestion>
  sessions!: Table<OfflineSession>

  constructor() {
    super('IhsaneOfflineDB')
    this.version(1).stores({
      questions: 'id, module_id, difficulty_level',
      sessions: 'id, student_id, module_id, status',
    })
  }
}

export const offlineDB = new OfflineDatabase()

class OfflineModuleStore {
  async cacheQuestions(moduleId: string, questions: OfflineQuestion[]): Promise<void> {
    await offlineDB.questions.bulkPut(questions)
  }

  async getCachedQuestions(moduleId: string): Promise<OfflineQuestion[]> {
    return await offlineDB.questions.where('module_id').equals(moduleId).toArray()
  }

  async getCachedQuestion(questionId: string): Promise<OfflineQuestion | undefined> {
    return await offlineDB.questions.get(questionId)
  }

  async createOfflineSession(session: OfflineSession): Promise<void> {
    await offlineDB.sessions.put(session)
  }

  async getOfflineSession(sessionId: string): Promise<OfflineSession | undefined> {
    return await offlineDB.sessions.get(sessionId)
  }

  async updateSessionAnswers(sessionId: string, answers: OfflineAnswer[]): Promise<void> {
    await offlineDB.sessions.update(sessionId, { answers })
  }

  async completeOfflineSession(sessionId: string): Promise<void> {
    await offlineDB.sessions.update(sessionId, {
      status: 'SYNC_PENDING',
      completed_at: new Date(),
    })
  }

  async getPendingSyncSessions(): Promise<OfflineSession[]> {
    return await offlineDB.sessions.where('status').equals('SYNC_PENDING').toArray()
  }

  async markSessionSynced(sessionId: string): Promise<void> {
    await offlineDB.sessions.update(sessionId, { status: 'COMPLETED' })
  }

  async clearCachedModule(moduleId: string): Promise<void> {
    await offlineDB.questions.where('module_id').equals(moduleId).delete()
  }

  async isModuleCached(moduleId: string): Promise<boolean> {
    const count = await offlineDB.questions.where('module_id').equals(moduleId).count()
    return count > 0
  }
}

export const offlineStore = new OfflineModuleStore()
