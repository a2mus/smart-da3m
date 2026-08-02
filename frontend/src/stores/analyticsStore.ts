import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  analyticsService,
  type HeatmapResponse,
  type StudentGroup,
  type MetricsResponse,
} from '@/services/analyticsService'

export const useAnalyticsStore = defineStore('analytics', () => {
  const heatmapData = ref<HeatmapResponse | null>(null)
  const studentGroups = ref<StudentGroup[]>([])
  const metrics = ref<MetricsResponse | null>(null)
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const showAutoGroupsOverlay = ref<boolean>(false)
  const autoGroupBy = ref<string>('competency')

  async function fetchHeatmap(moduleId?: string) {
    loading.value = true
    error.value = null
    try {
      const data = await analyticsService.getHeatmap(moduleId)
      heatmapData.value = data
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch heatmap data'
      console.error('analyticsStore fetchHeatmap error:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchStudentGroups(groupBy: string = 'competency') {
    autoGroupBy.value = groupBy
    try {
      const groups = await analyticsService.getStudentGroups(groupBy)
      studentGroups.value = groups
    } catch (err: unknown) {
      console.error('analyticsStore fetchStudentGroups error:', err)
    }
  }

  function toggleAutoGroupsOverlay() {
    showAutoGroupsOverlay.value = !showAutoGroupsOverlay.value
    if (showAutoGroupsOverlay.value && studentGroups.value.length === 0) {
      fetchStudentGroups(autoGroupBy.value)
    }
  }

  async function fetchMetrics() {
    try {
      const data = await analyticsService.getMetrics()
      metrics.value = data
    } catch (err: unknown) {
      console.error('analyticsStore fetchMetrics error:', err)
    }
  }

  return {
    heatmapData,
    studentGroups,
    metrics,
    loading,
    error,
    showAutoGroupsOverlay,
    autoGroupBy,
    fetchHeatmap,
    fetchStudentGroups,
    toggleAutoGroupsOverlay,
    fetchMetrics,
  }
})
