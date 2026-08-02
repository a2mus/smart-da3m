<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useContentStore } from '@/stores/contentStore'
import { type Module } from '@/services/contentService'
import ModuleEditor from '@/components/expert/ModuleEditor.vue'

const { t } = useI18n()
const router = useRouter()
const contentStore = useContentStore()

const showCreateModal = ref(false)
const showEditModal = ref(false)
const selectedModule = ref<Module | null>(null)

const modules = computed(() => contentStore.modules)

const handleCreateModule = async (moduleData: any) => {
  try {
    await contentStore.createModule(moduleData)
    showCreateModal.value = false
  } catch (err) {
    console.error('Failed to create module:', err)
  }
}

const handleUpdateModule = async (moduleData: any) => {
  try {
    await contentStore.updateModule(moduleData.id, moduleData)
    showEditModal.value = false
    selectedModule.value = null
  } catch (err) {
    console.error('Failed to update module:', err)
  }
}

const handleEditModule = (module: Module) => {
  selectedModule.value = module
  showEditModal.value = true
}

const handleDeleteModule = async (moduleId: string) => {
  if (!confirm(t('expert.confirmDelete', 'Are you sure you want to delete this module?'))) return
  try {
    await contentStore.deleteModule(moduleId)
  } catch (err) {
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

onMounted(() => {
  contentStore.fetchModules()
})
</script>

<template>
  <div class="min-h-screen p-6 bg-surface">
    <div class="bg-surface-bright rounded-2xl p-6 shadow-soft border border-outline-variant">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-primary">
          {{ t('expert.modules', 'Curriculum Modules') }}
        </h1>
        <button
          class="bg-primary text-on-primary px-4 py-2 rounded-xl flex items-center gap-2 hover:bg-primary/90 transition-colors font-medium shadow-sm"
          @click="showCreateModal = true"
        >
          <span>+</span>
          {{ t('expert.createModule', 'Create Module') }}
        </button>
      </div>

      <!-- Error Message -->
      <div
        v-if="contentStore.error"
        class="bg-error-container text-error px-4 py-3 rounded-xl mb-4"
      >
        {{ contentStore.error }}
      </div>

      <!-- Loading State -->
      <div
        v-if="contentStore.loading"
        class="text-center py-12"
      >
        <div class="animate-spin inline-block w-8 h-8 border-4 border-primary border-t-transparent rounded-full" />
        <p class="mt-2 text-on-surface-variant">
          {{ t('common.loading') }}
        </p>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="modules.length === 0"
        class="text-center py-12 text-on-surface-variant"
      >
        <p class="text-lg">
          {{ t('expert.noModules', 'No modules found.') }}
        </p>
        <p class="text-sm mt-1">
          {{ t('expert.createFirstModule', 'Click "Create Module" to add your first curriculum module.') }}
        </p>
      </div>

      <!-- Modules Grid -->
      <div
        v-else
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        <div
          v-for="mod in modules"
          :key="mod.id"
          class="bg-surface-container-low rounded-xl p-5 hover:shadow-md transition-shadow border border-outline-variant"
        >
          <div class="flex justify-between items-start mb-3">
            <span
              :class="[
                'px-2.5 py-1 text-xs font-medium rounded-full',
                mod.status === 'PUBLISHED' ? 'bg-tertiary-container text-tertiary' : 'bg-secondary-container text-secondary'
              ]"
            >
              {{ mod.status === 'PUBLISHED' ? t('expert.published', 'Published') : t('expert.draft', 'Draft') }}
            </span>
            <div class="flex gap-1">
              <button
                class="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary-container/20 rounded-lg transition-colors"
                :title="t('expert.edit', 'Edit')"
                @click="handleEditModule(mod)"
              >
                ✎
              </button>
              <button
                class="p-1.5 text-on-surface-variant hover:text-error hover:bg-error-container/20 rounded-lg transition-colors"
                :title="t('expert.delete', 'Delete')"
                @click="handleDeleteModule(mod.id)"
              >
                🗑
              </button>
            </div>
          </div>
          <h3 class="font-semibold text-on-surface mb-1 text-start">
            {{ mod.title || mod.subject }}
          </h3>
          <p
            v-if="mod.description"
            class="text-xs text-on-surface-variant mb-2 text-start line-clamp-2"
          >
            {{ mod.description }}
          </p>
          <p class="text-sm text-on-surface-variant mb-1 text-start">
            {{ mod.grade_level }} • {{ mod.subject }}
          </p>
          <p class="text-sm text-on-surface-variant mb-3 text-start">
            {{ mod.domain }}
          </p>
          <div class="flex items-center justify-between">
            <code class="text-xs bg-surface-container-high px-2 py-1 rounded text-on-surface-variant">{{ mod.competency_id }}</code>
            <button
              class="text-sm text-primary hover:underline font-medium"
              @click="handleManageQuestions(mod.id)"
            >
              {{ t('expert.manageQuestions', 'Manage Questions') }} →
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Module Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
      @click.self="closeModals"
    >
      <div class="w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <ModuleEditor
          mode="create"
          @save="handleCreateModule"
          @cancel="closeModals"
        />
      </div>
    </div>

    <!-- Edit Module Modal -->
    <div
      v-if="showEditModal && selectedModule"
      class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
      @click.self="closeModals"
    >
      <div class="w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <ModuleEditor
          mode="edit"
          :module="selectedModule"
          @update="handleUpdateModule"
          @cancel="closeModals"
        />
      </div>
    </div>
  </div>
</template>
