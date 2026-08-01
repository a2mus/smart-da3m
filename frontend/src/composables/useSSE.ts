import { ref, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { alertService, type Alert } from '@/services/alertService'

export interface UseSSEOptions {
  autoConnect?: boolean
  onAlert?: (alert: Alert) => void
  onMessage?: (event: MessageEvent) => void
  onError?: (error: Event | Error) => void
  onConnect?: () => void
  onDisconnect?: () => void
}

export function useSSE(options: UseSSEOptions = {}) {
  const {
    autoConnect = true,
    onAlert,
    onMessage,
    onError,
    onConnect,
    onDisconnect,
  } = options

  const isConnected = ref(false)
  const isPolling = ref(false)
  const error = ref<string | null>(null)
  const lastTimestamp = ref<string>(new Date().toISOString())

  let eventSource: EventSource | null = null
  let pollIntervalTimer: ReturnType<typeof setInterval> | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let reconnectAttempts = 0
  const maxReconnectInterval = 30000 // 30 seconds
  const initialReconnectInterval = 2000 // 2 seconds
  const pollingInterval = 15000 // 15 seconds

  const authStore = useAuthStore()

  function getStreamUrl(): string {
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
    const token = authStore.token || ''
    const orgId = authStore.activeOrganizationId || ''
    
    const params = new URLSearchParams()
    if (token) params.append('token', token)
    if (orgId) params.append('organization_id', orgId)

    const queryString = params.toString()
    return `${baseUrl}/events/stream${queryString ? `?${queryString}` : ''}`
  }

  function connect() {
    disconnect()

    const url = getStreamUrl()
    try {
      eventSource = new EventSource(url)

      eventSource.onopen = () => {
        isConnected.value = true
        isPolling.value = false
        error.value = null
        reconnectAttempts = 0
        stopPolling()

        // Fetch any missed alerts since last disconnect
        recoverMissedAlerts()

        if (onConnect) onConnect()
      }

      eventSource.onmessage = (event) => {
        handleRawEvent(event)
      }

      eventSource.addEventListener('alert', (event: MessageEvent) => {
        handleAlertEvent(event)
      })

      eventSource.onerror = (err) => {
        isConnected.value = false
        if (onError) onError(err)
        
        // Clean up current EventSource
        if (eventSource) {
          eventSource.close()
          eventSource = null
        }

        if (onDisconnect) onDisconnect()

        // Start fallback polling immediately while reconnecting
        startPolling()
        scheduleReconnect()
      }
    } catch (e: any) {
      error.value = e?.message || 'Failed to establish SSE connection'
      startPolling()
      scheduleReconnect()
    }
  }

  function scheduleReconnect() {
    if (reconnectTimer) clearTimeout(reconnectTimer)

    reconnectAttempts++
    const delay = Math.min(
      initialReconnectInterval * Math.pow(1.5, reconnectAttempts - 1),
      maxReconnectInterval
    )

    reconnectTimer = setTimeout(() => {
      if (!isConnected.value) {
        connect()
      }
    }, delay)
  }

  function handleRawEvent(event: MessageEvent) {
    if (onMessage) onMessage(event)
    try {
      const parsed = JSON.parse(event.data)
      if (parsed.type === 'alert' && parsed.data) {
        processAlertData(parsed.data)
      }
    } catch {
      // Non-JSON message
    }
  }

  function handleAlertEvent(event: MessageEvent) {
    try {
      const parsed = JSON.parse(event.data)
      processAlertData(parsed)
    } catch {
      console.error('Failed to parse SSE alert event data')
    }
  }

  function processAlertData(data: any) {
    const alert = alertService.normalizeAlert(data)
    if (alert.createdAt) {
      lastTimestamp.value = alert.createdAt
    }
    if (onAlert) {
      onAlert(alert)
    }
  }

  async function recoverMissedAlerts() {
    try {
      const missed = await alertService.getAlertsSince(lastTimestamp.value)
      if (missed.length > 0) {
        for (const alert of missed) {
          if (onAlert) onAlert(alert)
        }
        const newest = missed[0]
        if (newest.createdAt) {
          lastTimestamp.value = newest.createdAt
        }
      }
    } catch (err) {
      console.error('Failed to recover missed alerts:', err)
    }
  }

  function startPolling() {
    if (pollIntervalTimer) return
    isPolling.value = true

    // Initial poll check
    recoverMissedAlerts()

    pollIntervalTimer = setInterval(() => {
      recoverMissedAlerts()
    }, pollingInterval)
  }

  function stopPolling() {
    if (pollIntervalTimer) {
      clearInterval(pollIntervalTimer)
      pollIntervalTimer = null
    }
    isPolling.value = false
  }

  function disconnect() {
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    stopPolling()
    isConnected.value = false
    isPolling.value = false
  }

  if (autoConnect) {
    connect()
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    isPolling,
    error,
    lastTimestamp,
    connect,
    disconnect,
    recoverMissedAlerts,
  }
}
