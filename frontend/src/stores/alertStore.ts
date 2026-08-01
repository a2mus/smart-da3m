import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { alertService, type Alert, type ParentAlertSummary } from '@/services/alertService'

export const useAlertStore = defineStore('alert', () => {
  // State
  const alerts = ref<Alert[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const activeChildId = ref<string | null>(null)

  // Getters
  const unreadCount = computed(() => {
    return alerts.value.filter(a => !a.isRead && !a.is_read).length
  })

  const hasCritical = computed(() => {
    return alerts.value.some(a => a.severity === 'CRITICAL')
  })

  const sortedAlerts = computed(() => {
    return [...alerts.value].sort((a, b) => {
      const timeA = new Date(a.createdAt || a.created_at || 0).getTime()
      const timeB = new Date(b.createdAt || b.created_at || 0).getTime()
      return timeB - timeA
    })
  })

  const parentAlerts = computed<ParentAlertSummary[]>(() => {
    return sortedAlerts.value.map(a => ({
      id: a.id,
      severity: a.severity,
      message: a.simplifiedMessage || a.simplified_message || a.message || '',
      createdAt: a.createdAt || a.created_at || new Date().toISOString(),
      created_at: a.createdAt || a.created_at || new Date().toISOString(),
      isRead: a.isRead ?? a.is_read ?? false,
      is_read: a.isRead ?? a.is_read ?? false,
    }))
  })

  const expertAlerts = computed(() => {
    return sortedAlerts.value.map(a => ({
      ...a,
      displayMessage: a.expertMessage || a.expert_message || a.simplifiedMessage || a.simplified_message || a.message || '',
    }))
  })

  // Actions
  async function fetchAlerts(unreadOnly = false, childId?: string) {
    isLoading.value = true
    error.value = null
    try {
      if (childId) {
        activeChildId.value = childId
        const childSummaries = await alertService.getChildAlerts(childId)
        alerts.value = childSummaries.map(s => ({
          id: s.id,
          studentId: childId,
          student_id: childId,
          severity: s.severity,
          status: s.isRead || s.is_read ? 'READ' : 'UNREAD',
          simplifiedMessage: s.message,
          simplified_message: s.message,
          expertMessage: s.message,
          expert_message: s.message,
          createdAt: s.createdAt || s.created_at || new Date().toISOString(),
          created_at: s.createdAt || s.created_at || new Date().toISOString(),
          isRead: s.isRead ?? s.is_read ?? false,
          is_read: s.isRead ?? s.is_read ?? false,
          message: s.message,
        }))
      } else {
        const result = await alertService.getAlerts(unreadOnly)
        alerts.value = result.items
      }
    } catch (err: any) {
      error.value = err?.response?.data?.detail || err?.message || 'Failed to fetch alerts'
      console.error('Failed to fetch alerts:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function markAlertsRead(alertIds: string[]) {
    if (!alertIds.length) return
    try {
      await alertService.markAlertsRead(alertIds)
      alerts.value = alerts.value.map(a => {
        if (alertIds.includes(a.id)) {
          return {
            ...a,
            isRead: true,
            is_read: true,
            status: 'READ',
          }
        }
        return a
      })
    } catch (err) {
      console.error('Failed to mark alerts as read:', err)
    }
  }

  function dismissAlert(alertId: string) {
    alerts.value = alerts.value.filter(a => a.id !== alertId)
  }

  function addAlertFromSSE(rawAlert: any) {
    const normalized = alertService.normalizeAlert(rawAlert)
    
    // Deduplicate by ID
    const existingIndex = alerts.value.findIndex(a => a.id === normalized.id)
    if (existingIndex >= 0) {
      alerts.value[existingIndex] = normalized
    } else {
      alerts.value.unshift(normalized)
    }
  }

  function clearAlerts() {
    alerts.value = []
    activeChildId.value = null
    error.value = null
  }

  return {
    alerts,
    isLoading,
    error,
    activeChildId,
    unreadCount,
    hasCritical,
    sortedAlerts,
    parentAlerts,
    expertAlerts,
    fetchAlerts,
    markAlertsRead,
    dismissAlert,
    addAlertFromSSE,
    clearAlerts,
  }
})
