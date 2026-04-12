<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { contentService, type Module } from '@/services/contentService'
import ModuleEditor from '@/components/expert/ModuleEditor.vue'

const { t } = useI18n()
const router = useRouter()

const modules = ref<Module[]>([])
const loading = ref(false)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const selectedModule = ref<Module | null>(null)
const error = ref<string | null>(null)

const filteredModules = computed(() => modules.value)

const fetchModules = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await contentService.getModules()
    modules.value = response.items || []
  } catch (err) {
    error.value = t('errors.fetchFailed')
    console.error('Failed to fetch modules:', err)
  } finally {
    loading.value = false
  }
}

const handleCreateModule = async (moduleData: Omit<Module, 'id' | 'created_at' | 'updated_at'>) => {
  try {
    await contentService.createModule(moduleData)
    showCreateModal.value = false
    await fetchModules()
  } catch (err) {
    error.value = t('errors.createFailed')
    console.error('Failed to create module:', err)
  }
}

const handleUpdateModule = async (moduleData: Module) => {
  try {
    await contentService.updateModule(moduleData.id, moduleData)
    showEditModal.value = false
    selectedModule.value = null
    await fetchModules()
  } catch (err) {
    error.value = t('errors.updateFailed')
    console.error('Failed to update module:', err)
  }
}

const handleEditModule = (module: Module) => {
  selectedModule.value = module
  showEditModal.value = true
}

const handleDeleteModule = async (moduleId: string) => {
  if (!confirm(t('expert.confirmDelete'))) return
  try {
    await contentService.deleteModule(moduleId)
    await fetchModules()
  } catch (err) {
    error.value = t('errors.deleteFailed')
    console.error('Failed to delete module:', err)
  }
}

const handleManageQuestions = (moduleId: string) => {
  router.push(`/expert/modules/${moduleId}/questions`)
}

const closeModals = () => {
  showCreateModal.value = false
  showEditModal.value = false
  selectedModule.value = null
}

onMounted(() => fetchModules())
</script>

<template>
  <div class="min-h-screen p-6">
    <div class="nurturing-card p-6">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-primary-700">
          {{ t('expert.modules') }}
        </h1>
        <button @click="showCreateModal = true" class="btn-primary flex items-center gap-2">
          <span>+</span>
          {{ t('expert.createModule') }}
        </button>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-4">
        {{ error }}
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin inline-block w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full"></div>
        <p class="mt-2 text-warm-600">{{ t('common.loading') }}</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredModules.length === 0" class="text-center py-12 text-warm-600">
        <p class="text-lg">{{ t('expert.noModules') }}</p>
        <p class="text-sm mt-1">{{ t('expert.createFirstModule') }}</p>
      </div>

      <!-- Modules Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="module in filteredModules" :key="module.id"
          class="bg-warm-50 rounded-xl p-5 hover:shadow-md transition-shadow border-2 border-transparent hover:border-primary-200">
          <div class="flex justify-between items-start mb-3">
            <span :class="[
              'px-2 py-1 text-xs font-medium rounded-full',
              module.status === 'PUBLISHED' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
            ]">
              {{ module.status === 'PUBLISHED' ? t('expert.published') : t('expert.draft') }}
            </span>
            <div class="flex gap-1">
              <button @click="handleEditModule(module)"
                class="p-1.5 text-warm-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                :title="t('expert.edit')">✎</button>
              <button @click="handleDeleteModule(module.id)"
                class="p-1.5 text-warm-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                :title="t('expert.delete')">🗑</button>
            </div>
          </div>
          <h3 class="font-semibold text-warm-800 mb-1">{{ module.subject }}</h3>
          <p class="text-sm text-warm-600 mb-2">{{ module.grade_level }}</p>
          <p class="text-sm text-warm-500 mb-3">{{ module.domain }}</p>
          <div class="flex items-center justify-between">
            <code class="text-xs bg-warm-100 px-2 py-1 rounded text-warm-600">{{ module.competency_id }}</code>
            <button @click="handleManageQuestions(module.id)"
              class="text-sm text-primary-600 hover:text-primary-700 font-medium">
              {{ t('expert.manageQuestions') }} →
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Module Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
      @click.self="closeModals">
      <div class="w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <ModuleEditor mode="create" @save="handleCreateModule" @cancel="closeModals" />
      </div>
    </div>

    <!-- Edit Module Modal -->
    <div v-if="showEditModal && selectedModule" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
      @click.self="closeModals">
      <div class="w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <ModuleEditor mode="edit" :module="selectedModule" @update="handleUpdateModule" @cancel="closeModals" />
      </div>
    </div>
  </div>
</template>
