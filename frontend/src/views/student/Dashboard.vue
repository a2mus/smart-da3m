<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { contentService, type Module } from '@/services/contentService'
import { diagnosticService, type CompetencyProfile } from '@/services/diagnosticService'

const { t } = useI18n()
const router = useRouter()

const modules = ref<Module[]>([])
const profiles = ref<CompetencyProfile[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const availableModules = computed(() => modules.value.filter(m => m.status === 'PUBLISHED'))
const masteredCount = computed(() => profiles.value.filter(p => p.mastery_level === 'MASTERED').length)
const inProgressCount = computed(() => profiles.value.filter(p => p.mastery_level === 'ATTEMPTED' || p.mastery_level === 'FAMILIAR').length)

const fetchData = async () => {
  loading.value = true
  error.value = null
  try {
    const [modulesRes, profilesRes] = await Promise.all([
      contentService.getModules(),
      diagnosticService.getCompetencyProfiles(),
    ])
    modules.value = modulesRes.items || []
    profiles.value = profilesRes || []
  } catch (err) {
    error.value = t('errors.fetchFailed')
    console.error('Failed to fetch dashboard data:', err)
  } finally {
    loading.value = false
  }
}

const startDiagnostic = (moduleId: string) => {
  router.push(`/student/diagnostic/${moduleId}`)
}

const getMasteryColor = (level: string) => {
  switch (level) {
    case 'MASTERED': return 'bg-green-500'
    case 'PROFICIENT': return 'bg-blue-500'
    case 'FAMILIAR': return 'bg-yellow-500'
    case 'ATTEMPTED': return 'bg-orange-500'
    default: return 'bg-gray-300'
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="min-h-screen p-6">
    <div class="max-w-5xl mx-auto">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-primary-700 mb-2">{{ t('student.welcome') }}</h1>
        <p class="text-warm-600">{{ t('student.readyToLearn') }}</p>
      </div>

      <div class="grid grid-cols-3 gap-4 mb-8">
        <div class="bg-white rounded-2xl p-5 shadow-soft text-center">
          <div class="text-3xl font-bold text-primary-600">{{ masteredCount }}</div>
          <div class="text-sm text-warm-600">{{ t('student.mastered') }}</div>
        </div>
        <div class="bg-white rounded-2xl p-5 shadow-soft text-center">
          <div class="text-3xl font-bold text-yellow-600">{{ inProgressCount }}</div>
          <div class="text-sm text-warm-600">{{ t('student.inProgress') }}</div>
        </div>
        <div class="bg-white rounded-2xl p-5 shadow-soft text-center">
          <div class="text-3xl font-bold text-blue-600">{{ availableModules.length }}</div>
          <div class="text-sm text-warm-600">{{ t('student.available') }}</div>
        </div>
      </div>

      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-4">
        {{ error }}
      </div>

      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin inline-block w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full"></div>
        <p class="mt-2 text-warm-600">{{ t('common.loading') }}</p>
      </div>

      <div v-else>
        <h2 class="text-xl font-bold text-warm-800 mb-4">{{ t('student.availableModules') }}</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="module in availableModules" :key="module.id"
            class="bg-white rounded-xl p-5 shadow-soft hover:shadow-md transition-shadow">
            <div class="flex justify-between items-start mb-3">
              <span class="px-2 py-1 text-xs font-medium rounded-full bg-primary-100 text-primary-700">
                {{ module.subject }}
              </span>
            </div>
            <h3 class="font-semibold text-warm-800 mb-1">{{ module.grade_level }}</h3>
            <p class="text-sm text-warm-500 mb-4">{{ module.domain }}</p>
            <button @click="startDiagnostic(module.id)"
              class="w-full py-2.5 bg-primary-500 hover:bg-primary-600 text-white font-semibold rounded-lg transition-colors">
              {{ t('student.startDiagnostic') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
