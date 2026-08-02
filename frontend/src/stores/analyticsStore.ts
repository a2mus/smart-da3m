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
  const exporting = ref<boolean>(false)
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

  async function exportReport(format: 'pdf' | 'csv' = 'csv', reportType: string = 'heatmap') {
    exporting.value = true
    loading.value = true
    try {
      const res = await analyticsService.exportReport(format, reportType)
      if ('file_path' in res && res.file_path) {
        const a = document.createElement('a')
        a.href = `/api/v1/analytics/export?format=${format}&report_type=${reportType}`
        a.download = `${reportType}.${format}`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
      }
      return res
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to export report'
      console.error('analyticsStore exportReport error:', err)
      throw err
    } finally {
      exporting.value = false
      loading.value = false
    }
  }

  return {
    heatmapData,
    studentGroups,
    metrics,
    loading,
    exporting,
    error,
    showAutoGroupsOverlay,
    autoGroupBy,
    fetchHeatmap,
    fetchStudentGroups,
    toggleAutoGroupsOverlay,
    fetchMetrics,
    exportReport,
  }
})
