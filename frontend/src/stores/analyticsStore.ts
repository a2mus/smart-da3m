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

  async function fetchStudentGroups() {
    try {
      const groups = await analyticsService.getStudentGroups()
      studentGroups.value = groups
    } catch (err: unknown) {
      console.error('analyticsStore fetchStudentGroups error:', err)
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
    fetchHeatmap,
    fetchStudentGroups,
    fetchMetrics,
  }
})
