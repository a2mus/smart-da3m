<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import CompetencyHeatmap from '@/components/expert/CompetencyHeatmap.vue'
import { analyticsService, type HeatmapResponse, type StudentGroup, type MetricsResponse } from '@/services/analyticsService'

const { t } = useI18n()
const router = useRouter()

// Data refs
const heatmapData = ref<HeatmapResponse | null>(null)
const studentGroups = ref<StudentGroup[]>([])
const metrics = ref<MetricsResponse | null>(null)

// UI state
const loading = ref({
  heatmap: false,
  groups: false,
  metrics: false,
  export: false,
})

const error = ref<string | null>(null)

// Filters
const selectedCompetencies = ref<string[]>([])
const groupBy = ref<'competency' | 'error_type'>('competency')
const activeTab = ref<'heatmap' | 'groups' | 'metrics'>('heatmap')

// Fetch heatmap data
const fetchHeatmap = async () => {
  loading.value.heatmap = true
  error.value = null
  try {
    const filters = {
      competency_ids: selectedCompetencies.value.length > 0 ? selectedCompetencies.value : undefined,
    }
    heatmapData.value = await analyticsService.getHeatmap(filters)
  } catch (err) {
    error.value = t('errors.fetchHeatmapFailed')
    console.error('Failed to fetch heatmap:', err)
  } finally {
    loading.value.heatmap = false
  }
}

// Fetch auto-grouped students
const fetchGroups = async () => {
  loading.value.groups = true
  error.value = null
  try {
    const filters = {}
    const response = await analyticsService.autoGroup(filters, groupBy.value)
    studentGroups.value = response.groups
  } catch (err) {
    error.value = t('errors.fetchGroupsFailed')
    console.error('Failed to fetch groups:', err)
  } finally {
    loading.value.groups = false
  }
}

// Fetch platform metrics
const fetchMetrics = async () => {
  loading.value.metrics = true
  error.value = null
  try {
    metrics.value = await analyticsService.getMetrics()
  } catch (err) {
    error.value = t('errors.fetchMetricsFailed')
    console.error('Failed to fetch metrics:', err)
  } finally {
    loading.value.metrics = false
  }
}

// Export report
const exportReport = async (format: 'csv' | 'pdf') => {
  loading.value.export = true
  error.value = null
  try {
    const studentIds = heatmapData.value?.students.map(s => s.id)
    const response = await analyticsService.exportReport({
      format,
      report_type: 'heatmap',
      filters: {
        competency_ids: selectedCompetencies.value.length > 0 ? selectedCompetencies.value : undefined,
      },
      student_ids: studentIds,
    })

    // Show success message
    alert(t('analytics.exportSuccess', { file: response.file_path }))
  } catch (err) {
    error.value = t('errors.exportFailed')
    console.error('Failed to export report:', err)
  } finally {
    loading.value.export = false
  }
}

// Handle heatmap cell click
const handleCellClick = (cell: any) => {
  console.log('Cell clicked:', cell)
  // Could navigate to student detail view
}

// Handle student click
const handleStudentClick = (studentId: string) => {
  router.push(`/expert/students/${studentId}`)
}

// Refresh all data
const refreshData = async () => {
  await Promise.all([
    fetchHeatmap(),
    fetchGroups(),
    fetchMetrics(),
  ])
}

onMounted(() => {
  refreshData()
})

// Computed available competencies from heatmap data
const availableCompetencies = computed(() => {
  return heatmapData.value?.competencies || []
})
</script>

<template>
  <div class="min-h-screen p-6">
    <div class="nurturing-card p-6">
      <!-- Header -->
      <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-6">
        <div>
          <h1 class="text-2xl font-bold text-primary-700">
            {{ t('expert.analytics') }}
          </h1>
          <p class="text-warm-600 mt-1">
            {{ t('expert.analyticsDescription') }}
          </p>
        </div>
        <div class="flex gap-2">
          <button
            @click="exportReport('csv')"
            :disabled="loading.export"
            class="btn-secondary flex items-center gap-2"
          >
            <span v-if="loading.export" class="animate-spin">⟳</span>
            <span v-else>📊</span>
            {{ t('analytics.exportCSV') }}
          </button>
          <button
            @click="exportReport('pdf')"
            :disabled="loading.export"
            class="btn-secondary flex items-center gap-2"
          >
            <span v-if="loading.export" class="animate-spin">⟳</span>
            <span v-else>📄</span>
            {{ t('analytics.exportPDF') }}
          </button>
          <button @click="refreshData" class="btn-primary">
            🔄 {{ t('common.refresh') }}
          </button>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-4">
        {{ error }}
      </div>

      <!-- Metrics Overview -->
      <div v-if="metrics" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
        <div class="bg-warm-50 rounded-xl p-4 text-center">
          <div class="text-2xl font-bold text-primary-600">{{ metrics.total_students }}</div>
          <div class="text-sm text-warm-600">{{ t('analytics.totalStudents') }}</div>
        </div>
        <div class="bg-warm-50 rounded-xl p-4 text-center">
          <div class="text-2xl font-bold text-green-600">{{ Math.round(metrics.gap_reduction_rate) }}%</div>
          <div class="text-sm text-warm-600">{{ t('analytics.gapReduction') }}</div>
        </div>
        <div class="bg-warm-50 rounded-xl p-4 text-center">
          <div class="text-2xl font-bold text-blue-600">{{ metrics.mastery_speed.toFixed(1) }}</div>
          <div class="text-sm text-warm-600">{{ t('analytics.masterySpeed') }}</div>
        </div>
        <div class="bg-warm-50 rounded-xl p-4 text-center">
          <div class="text-2xl font-bold text-purple-600">{{ Math.round(metrics.retention_rate) }}%</div>
          <div class="text-sm text-warm-600">{{ t('analytics.retentionRate') }}</div>
        </div>
        <div class="bg-warm-50 rounded-xl p-4 text-center">
          <div class="text-2xl font-bold text-orange-600">{{ Math.round(metrics.resilience_score) }}%</div>
          <div class="text-sm text-warm-600">{{ t('analytics.resilienceScore') }}</div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="border-b border-warm-200 mb-6">
        <nav class="flex gap-1">
          <button
            @click="activeTab = 'heatmap'"
            :class="[
              'px-4 py-2 font-medium text-sm rounded-t-lg transition-colors',
              activeTab === 'heatmap'
                ? 'bg-primary-100 text-primary-700 border-b-2 border-primary-500'
                : 'text-warm-600 hover:text-warm-800 hover:bg-warm-50'
            ]"
          >
            {{ t('analytics.heatmap') }}
          </button>
          <button
            @click="activeTab = 'groups'"
            :class="[
              'px-4 py-2 font-medium text-sm rounded-t-lg transition-colors',
              activeTab === 'groups'
                ? 'bg-primary-100 text-primary-700 border-b-2 border-primary-500'
                : 'text-warm-600 hover:text-warm-800 hover:bg-warm-50'
            ]"
          >
            {{ t('analytics.studentGroups') }}
          </button>
          <button
            @click="activeTab = 'metrics'"
            :class="[
              'px-4 py-2 font-medium text-sm rounded-t-lg transition-colors',
              activeTab === 'metrics'
                ? 'bg-primary-100 text-primary-700 border-b-2 border-primary-500'
                : 'text-warm-600 hover:text-warm-800 hover:bg-warm-50'
            ]"
          >
            {{ t('analytics.detailedMetrics') }}
          </button>
        </nav>
      </div>

      <!-- Filters -->
      <div class="bg-warm-50 rounded-xl p-4 mb-6">
        <div class="flex flex-wrap items-center gap-4">
          <div class="flex items-center gap-2">
            <span class="text-sm font-medium text-warm-700">{{ t('analytics.filterBy') }}:</span>
            <select
              v-model="selectedCompetencies"
              multiple
              class="form-select min-w-[200px]"
            >
              <option v-for="comp in availableCompetencies" :key="comp" :value="comp">
                {{ comp }}
              </option>
            </select>
          </div>
          <button @click="fetchHeatmap" class="btn-primary text-sm">
            {{ t('analytics.applyFilters') }}
          </button>
        </div>
      </div>

      <!-- Heatmap Tab -->
      <div v-if="activeTab === 'heatmap'">
        <CompetencyHeatmap
          :data="heatmapData"
          :loading="loading.heatmap"
          @cell-click="handleCellClick"
          @student-click="handleStudentClick"
        />
      </div>

      <!-- Student Groups Tab -->
      <div v-if="activeTab === 'groups'">
        <div v-if="loading.groups" class="flex items-center justify-center py-12">
          <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full"></div>
        </div>
        <div v-else-if="studentGroups.length === 0" class="text-center py-12 text-warm-600">
          <p class="text-lg">{{ t('analytics.noGroupsFound') }}</p>
          <p class="text-sm mt-1">{{ t('analytics.groupsDescription') }}</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="group in studentGroups"
            :key="group.group_id"
            class="bg-white rounded-xl p-5 border-2 border-warm-100 hover:border-primary-200 transition-colors"
          >
            <div class="flex justify-between items-start mb-3">
              <h3 class="font-semibold text-warm-800">{{ group.name }}</h3>
              <span class="px-2 py-1 bg-primary-100 text-primary-700 text-xs font-medium rounded-full">
                {{ group.student_count }} {{ t('analytics.students') }}
              </span>
            </div>
            <p class="text-sm text-warm-600 mb-4">{{ group.recommended_action }}</p>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="studentId in group.student_ids.slice(0, 5)"
                :key="studentId"
                class="px-2 py-1 bg-warm-100 text-warm-600 text-xs rounded"
              >
                {{ studentId.slice(0, 8) }}...
              </span>
              <span v-if="group.student_ids.length > 5" class="text-xs text-warm-500">
                +{{ group.student_ids.length - 5 }} more
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Detailed Metrics Tab -->
      <div v-if="activeTab === 'metrics'">
        <div v-if="loading.metrics" class="flex items-center justify-center py-12">
          <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full"></div>
        </div>
        <div v-else-if="!metrics" class="text-center py-12 text-warm-600">
          <p class="text-lg">{{ t('analytics.noMetricsAvailable') }}</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="bg-warm-50 rounded-xl p-6">
            <h3 class="font-semibold text-warm-800 mb-4">{{ t('analytics.effortVsResults') }}</h3>
            <div class="flex items-center justify-center h-32">
              <div class="text-4xl font-bold text-primary-600">
                {{ Math.round(metrics.effort_vs_results * 100) }}%
              </div>
            </div>
            <p class="text-sm text-warm-600 text-center">
              {{ t('analytics.effortResultsDescription') }}
            </p>
          </div>
          <div class="bg-warm-50 rounded-xl p-6">
            <h3 class="font-semibold text-warm-800 mb-4">{{ t('analytics.totalAssessments') }}</h3>
            <div class="flex items-center justify-center h-32">
              <div class="text-4xl font-bold text-primary-600">
                {{ metrics.total_assessments }}
              </div>
            </div>
            <p class="text-sm text-warm-600 text-center">
              {{ t('analytics.assessmentsDescription') }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>