import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  contentService,
  type KnowledgeAtom,
  type Module,
  type ModuleCreate,
  type Question,
  type QuestionCreate,
} from '@/services/contentService'

export const useContentStore = defineStore('content', () => {
  const modules = ref<Module[]>([])
  const currentModule = ref<Module | null>(null)
  const questions = ref<Question[]>([])
  const knowledgeAtoms = ref<KnowledgeAtom[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchModules() {
    loading.value = true
    error.value = null
    try {
      const response = await contentService.getModules()
      modules.value = response.items || []
    } catch (err: any) {
      error.value = err?.message || 'Failed to fetch modules'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchModule(id: string) {
    loading.value = true
    error.value = null
    try {
      const data = await contentService.getModule(id)
      currentModule.value = data
      return data
    } catch (err: any) {
      error.value = err?.message || 'Failed to fetch module'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createModule(payload: ModuleCreate) {
    loading.value = true
    error.value = null
    try {
      const newMod = await contentService.createModule(payload)
      modules.value.unshift(newMod)
      return newMod
    } catch (err: any) {
      error.value = err?.message || 'Failed to create module'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateModule(id: string, payload: Partial<ModuleCreate>) {
    loading.value = true
    error.value = null
    try {
      const updated = await contentService.updateModule(id, payload)
      const index = modules.value.findIndex((m) => m.id === id)
      if (index !== -1) {
        modules.value[index] = updated
      }
      if (currentModule.value?.id === id) {
        currentModule.value = updated
      }
      return updated
    } catch (err: any) {
      error.value = err?.message || 'Failed to update module'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteModule(id: string) {
    loading.value = true
    error.value = null
    try {
      await contentService.deleteModule(id)
      modules.value = modules.value.filter((m) => m.id !== id)
      if (currentModule.value?.id === id) {
        currentModule.value = null
      }
    } catch (err: any) {
      error.value = err?.message || 'Failed to delete module'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchQuestions(moduleId?: string) {
    loading.value = true
    error.value = null
    try {
      const response = await contentService.getQuestions(moduleId)
      questions.value = response.items || []
      return questions.value
    } catch (err: any) {
      error.value = err?.message || 'Failed to fetch questions'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createQuestion(payload: QuestionCreate) {
    loading.value = true
    error.value = null
    try {
      const newQ = await contentService.createQuestion(payload)
      questions.value.unshift(newQ)
      return newQ
    } catch (err: any) {
      error.value = err?.message || 'Failed to create question'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateQuestion(id: string, payload: Partial<QuestionCreate>) {
    loading.value = true
    error.value = null
    try {
      const updated = await contentService.updateQuestion(id, payload)
      const index = questions.value.findIndex((q) => q.id === id)
      if (index !== -1) {
        questions.value[index] = updated
      }
      return updated
    } catch (err: any) {
      error.value = err?.message || 'Failed to update question'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteQuestion(id: string) {
    loading.value = true
    error.value = null
    try {
      await contentService.deleteQuestion(id)
      questions.value = questions.value.filter((q) => q.id !== id)
    } catch (err: any) {
      error.value = err?.message || 'Failed to delete question'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchKnowledgeAtoms(competencyId?: string) {
    loading.value = true
    error.value = null
    try {
      const response = await contentService.getKnowledgeAtoms(competencyId)
      knowledgeAtoms.value = response.items || []
      return knowledgeAtoms.value
    } catch (err: any) {
      error.value = err?.message || 'Failed to fetch knowledge atoms'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createKnowledgeAtom(payload: Omit<KnowledgeAtom, 'id' | 'created_at' | 'updated_at'>) {
    loading.value = true
    error.value = null
    try {
      const newAtom = await contentService.createKnowledgeAtom(payload)
      knowledgeAtoms.value.unshift(newAtom)
      return newAtom
    } catch (err: any) {
      error.value = err?.message || 'Failed to create knowledge atom'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateKnowledgeAtom(
    id: string,
    payload: Partial<Omit<KnowledgeAtom, 'id' | 'created_at' | 'updated_at'>>,
  ) {
    loading.value = true
    error.value = null
    try {
      const updated = await contentService.updateKnowledgeAtom(id, payload)
      const index = knowledgeAtoms.value.findIndex((a) => a.id === id)
      if (index !== -1) {
        knowledgeAtoms.value[index] = updated
      }
      return updated
    } catch (err: any) {
      error.value = err?.message || 'Failed to update knowledge atom'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteKnowledgeAtom(id: string) {
    loading.value = true
    error.value = null
    try {
      await contentService.deleteKnowledgeAtom(id)
      knowledgeAtoms.value = knowledgeAtoms.value.filter((a) => a.id !== id)
    } catch (err: any) {
      error.value = err?.message || 'Failed to delete knowledge atom'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    modules,
    currentModule,
    questions,
    knowledgeAtoms,
    loading,
    error,
    fetchModules,
    fetchModule,
    createModule,
    updateModule,
    deleteModule,
    fetchQuestions,
    createQuestion,
    updateQuestion,
    deleteQuestion,
    fetchKnowledgeAtoms,
    createKnowledgeAtom,
    updateKnowledgeAtom,
    deleteKnowledgeAtom,
  }
})
