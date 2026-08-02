<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useContentStore } from '@/stores/contentStore'
import ModuleEditorComponent, { type ModuleForm } from '@/components/expert/ModuleEditor.vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const contentStore = useContentStore()

const moduleId = computed(() => route.params.id as string | undefined)
const isEditMode = computed(() => !!moduleId.value && moduleId.value !== 'new')

onMounted(async () => {
  if (isEditMode.value && moduleId.value) {
    await contentStore.fetchModule(moduleId.value)
  }
})

const handleSave = async (formData: ModuleForm) => {
  try {
    await contentStore.createModule(formData)
    router.push('/expert/modules')
  } catch (err) {
    console.error('Failed to create module:', err)
  }
}

const handleUpdate = async (formData: ModuleForm & { id: string }) => {
  try {
    await contentStore.updateModule(formData.id, formData)
    router.push('/expert/modules')
  } catch (err) {
    console.error('Failed to update module:', err)
  }
}

const handleCancel = () => {
  router.push('/expert/modules')
}
</script>

<template>
  <div class="min-h-screen p-6 bg-surface">
    <div class="max-w-4xl mx-auto">
      <div
        v-if="contentStore.loading"
        class="text-center py-12"
      >
        <div class="animate-spin inline-block w-8 h-8 border-4 border-primary border-t-transparent rounded-full" />
        <p class="mt-2 text-on-surface-variant">
          {{ t('common.loading') }}
        </p>
      </div>

      <div
        v-else-if="contentStore.error"
        class="bg-error-container text-error p-4 rounded-xl mb-4"
      >
        {{ contentStore.error }}
      </div>

      <ModuleEditorComponent
        v-else
        :mode="isEditMode ? 'edit' : 'create'"
        :module="isEditMode && contentStore.currentModule ? contentStore.currentModule : undefined"
        @save="handleSave"
        @update="handleUpdate"
        @cancel="handleCancel"
      />
    </div>
  </div>
</template>
