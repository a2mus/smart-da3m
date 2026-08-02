import { defineStore } from 'pinia'
import { ref } from 'vue'
import { contentService, type Module, type ModuleCreate } from '@/services/contentService'

export const useContentStore = defineStore('content', () => {
  const modules = ref<Module[]>([])
  const currentModule = ref<Module | null>(null)
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

  return {
    modules,
    currentModule,
    loading,
    error,
    fetchModules,
    fetchModule,
    createModule,
    updateModule,
    deleteModule,
  }
})
