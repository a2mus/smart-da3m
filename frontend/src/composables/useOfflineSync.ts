import { ref, onMounted, onUnmounted } from 'vue'
import { offlineStore, type PendingAnswer } from '@/stores/offlineModule'
import { diagnosticService } from '@/services/diagnosticService'

interface SyncManager {
  register(tag: string): Promise<void>
}

interface ServiceWorkerRegistrationWithSync extends ServiceWorkerRegistration {
  sync: SyncManager
}

export function useOfflineSync() {
  const isOnline = ref(typeof navigator !== 'undefined' ? navigator.onLine : true)
  const pendingCount = ref(0)
  const isSyncing = ref(false)

  const refreshPendingCount = async () => {
    try {
      const answers = await offlineStore.getPendingAnswers()
      const sessions = await offlineStore.getPendingSyncSessions()
      pendingCount.value = answers.length + sessions.length
    } catch (err) {
      console.warn('Failed to refresh pending count:', err)
    }
  }

  const registerBackgroundSync = async () => {
    if (
      typeof window !== 'undefined' &&
      'serviceWorker' in navigator &&
      'SyncManager' in window
    ) {
      try {
        const registration = await navigator.serviceWorker.ready
        if ('sync' in registration) {
          const syncReg = registration as unknown as ServiceWorkerRegistrationWithSync
          await syncReg.sync.register('offline-sync')
        }
      } catch (err) {
        console.debug('Background sync registration not supported or failed:', err)
      }
    }
  }

  const syncNow = async (): Promise<void> => {
    if (typeof navigator !== 'undefined' && !navigator.onLine) {
      isOnline.value = false
      return
    }

    isSyncing.value = true
    try {
      // 1. Flush pending write-behind answers
      const pendingAnswers = await offlineStore.getPendingAnswers()
      for (const item of pendingAnswers) {
        try {
          await diagnosticService.submitAnswer({
            session_id: item.session_id,
            question_id: item.question_id,
            answer: item.answer,
            time_ms: item.time_ms || 0,
          })
          if (item.id) {
            await offlineStore.markAnswerSynced(item.id)
          }
        } catch (e) {
          console.warn('Failed to sync pending answer during flush:', e)
          break
        }
      }

      // 2. Flush pending completed offline sessions
      const pendingSessions = await offlineStore.getPendingSyncSessions()
      for (const session of pendingSessions) {
        try {
          await offlineStore.markSessionSynced(session.id)
        } catch (e) {
          console.warn('Failed to mark session synced during flush:', e)
        }
      }

      // 3. Register background sync tag with SW if available
      await registerBackgroundSync()
    } catch (err) {
      console.error('Error executing syncNow:', err)
    } finally {
      await refreshPendingCount()
      isSyncing.value = false
    }
  }

  const queueAnswer = async (
    answerData: Omit<PendingAnswer, 'id' | 'created_at'> & { created_at?: Date }
  ): Promise<number> => {
    const id = await offlineStore.queueAnswer(answerData)
    await refreshPendingCount()

    if (isOnline.value) {
      syncNow()
    }
    return id
  }

  const queueCompletion = async (sessionId: string): Promise<void> => {
    await offlineStore.completeOfflineSession(sessionId)
    await refreshPendingCount()

    if (isOnline.value) {
      syncNow()
    }
  }

  const handleOnline = () => {
    isOnline.value = true
    syncNow()
  }

  const handleOffline = () => {
    isOnline.value = false
  }

  onMounted(() => {
    refreshPendingCount()
    if (typeof window !== 'undefined') {
      window.addEventListener('online', handleOnline)
      window.addEventListener('offline', handleOffline)
    }
  })

  onUnmounted(() => {
    if (typeof window !== 'undefined') {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  })

  return {
    isOnline,
    pendingCount,
    isSyncing,
    syncNow,
    queueAnswer,
    queueCompletion,
    refreshPendingCount,
  }
}
