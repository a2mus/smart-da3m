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

export interface PendingAnswer {
  id?: number
  session_id: string
  question_id: string
  answer: string
  time_ms?: number
  sync_status: 'PENDING' | 'SYNCED'
  created_at: Date
}

export class OfflineDatabase extends Dexie {
  questions!: Table<OfflineQuestion>
  sessions!: Table<OfflineSession>
  pending_answers!: Table<PendingAnswer>

  constructor() {
    super('IhsaneOfflineDB')
    this.version(1).stores({
      questions: 'id, module_id, difficulty_level',
      sessions: 'id, student_id, module_id, status',
      pending_answers: '++id, session_id, question_id, sync_status, created_at',
    })
  }
}

export const offlineDB = new OfflineDatabase()

class OfflineModuleStore {
  async cacheQuestions(_moduleId: string, questions: OfflineQuestion[]): Promise<void> {
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

  async queueAnswer(answer: Omit<PendingAnswer, 'id' | 'created_at'> & { created_at?: Date }): Promise<number> {
    const id = await offlineDB.pending_answers.add({
      ...answer,
      created_at: answer.created_at || new Date(),
    })
    return id as number
  }

  async getPendingAnswers(): Promise<PendingAnswer[]> {
    const pending = await offlineDB.pending_answers.where('sync_status').equals('PENDING').toArray()
    return pending.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
  }

  async markAnswerSynced(id: number): Promise<void> {
    await offlineDB.pending_answers.update(id, { sync_status: 'SYNCED' })
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
