import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  dashboardService,
  type ChildSummary,
  type ChildDashboardData,
  type ParentDashboardResponse,
} from '@/services/dashboardService'

export const useDashboardStore = defineStore('dashboard', () => {
  const children = ref<ChildSummary[]>([])
  const selectedChildId = ref<string>('')
  const currentChildData = ref<ChildDashboardData | null>(null)
  const overviewData = ref<ParentDashboardResponse | null>(null)
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)

  const selectedChildSummary = computed(() =>
    children.value.find(
      (c) => (c.childId || c.child_id) === selectedChildId.value
    ) || null
  )

  /**
   * Fetch all children and overview data for the current parent.
   */
  async function fetchChildren() {
    loading.value = true
    error.value = null
    try {
      const list = await dashboardService.getChildrenList()
      children.value = list
      if (list.length > 0 && !selectedChildId.value) {
        selectedChildId.value = list[0].childId || list[0].child_id || ''
        await fetchChildData(selectedChildId.value)
      }
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch children'
      console.error('dashboardStore fetchChildren error:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch detailed dashboard metrics for a specific child.
   */
  async function fetchChildData(childId: string) {
    if (!childId) return
    loading.value = true
    error.value = null
    try {
      selectedChildId.value = childId
      const data = await dashboardService.getChildDetails(childId)
      currentChildData.value = data
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch child data'
      console.error('dashboardStore fetchChildData error:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch full dashboard overview response.
   */
  async function fetchOverview(childId?: string) {
    loading.value = true
    error.value = null
    try {
      const data = await dashboardService.getOverview(childId)
      overviewData.value = data
      if (data.children && data.children.length > 0) {
        currentChildData.value = data.children[0]
      }
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch overview'
      console.error('dashboardStore fetchOverview error:', err)
    } finally {
      loading.value = false
    }
  }

  function selectChild(childId: string) {
    selectedChildId.value = childId
    return fetchChildData(childId)
  }

  return {
    children,
    selectedChildId,
    currentChildData,
    overviewData,
    loading,
    error,
    selectedChildSummary,
    fetchChildren,
    fetchChildData,
    fetchOverview,
    selectChild,
  }
})
