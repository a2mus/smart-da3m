<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { diagnosticService, type ActiveDiagnosticSession } from '@/services/diagnosticService'
import { offlineStore } from '@/stores/offlineModule'

const { t } = useI18n()
const router = useRouter()

const activeSession = ref<ActiveDiagnosticSession | null>(null)
const isLoading = ref(true)
const isAbandoning = ref(false)

const checkActiveSession = async () => {
  isLoading.value = true
  try {
    const session = await diagnosticService.getActiveSession()
    if (session) {
      activeSession.value = session
      return
    }
  } catch (err) {
    console.warn('Failed to fetch active session from API, falling back to offline store:', err)
  }

  try {
    const offlineSessions = await offlineStore.getPendingSyncSessions()
    const inProgressOffline = offlineSessions.find((s) => s.status === 'IN_PROGRESS')
    if (inProgressOffline) {
      const parsedDate = inProgressOffline.started_at ? new Date(inProgressOffline.started_at) : new Date()
      const validDateStr = !isNaN(parsedDate.getTime()) ? parsedDate.toISOString() : new Date().toISOString()

      activeSession.value = {
        session_id: inProgressOffline.id,
        module_id: inProgressOffline.module_id,
        question_number: Math.min(inProgressOffline.answers ? inProgressOffline.answers.length + 1 : 1, 10),
        total_questions: 10,
        started_at: validDateStr,
      }
    }
  } catch (err) {
    console.warn('Failed to check offline diagnostic session:', err)
  } finally {
    isLoading.value = false
  }
}

const resumeDiagnostic = () => {
  if (!activeSession.value) return
  router.push(`/student/diagnostic/${activeSession.value.module_id}`)
}

const abandonDiagnostic = async () => {
  if (!activeSession.value) return
  if (!confirm(t('diagnostic.resumeBanner.abandonConfirm'))) return

  const sessionIdToAbandon = activeSession.value.session_id
  isAbandoning.value = true
  try {
    await diagnosticService.abandonSession(sessionIdToAbandon)
  } catch (err) {
    console.warn('Failed to abandon session via API, clearing locally:', err)
  } finally {
    try {
      await offlineStore.completeOfflineSession(sessionIdToAbandon)
    } catch (localErr) {
      console.warn('Failed to clear local offline session:', localErr)
    }
    activeSession.value = null
    isAbandoning.value = false
  }
}

onMounted(() => {
  checkActiveSession()
})
</script>

<template>
  <div
    v-if="!isLoading && activeSession"
    data-testid="diagnostic-resume-banner"
    class="w-full bg-primary-container text-on-primary-container rounded-[2rem] p-6 md:p-8 flex flex-col md:flex-row items-center justify-between shadow-lg gap-6 mb-8 border border-primary/20"
  >
    <div class="flex items-center gap-5 text-start w-full md:w-auto">
      <div class="w-14 h-14 bg-primary text-on-primary rounded-2xl flex items-center justify-center shrink-0 shadow-md">
        <span
          class="material-symbols-outlined text-3xl"
          data-icon="play_circle"
          style="font-variation-settings: 'FILL' 1;"
        >play_circle</span>
      </div>
      <div>
        <h3 class="text-xl md:text-2xl font-black">
          {{ t('diagnostic.resumeBanner.title') }}
        </h3>
        <p class="text-on-primary-container/80 text-sm md:text-base font-bold">
          {{ t('diagnostic.resumeBanner.progress', { current: activeSession.question_number, total: activeSession.total_questions }) }}
        </p>
      </div>
    </div>

    <div class="flex items-center gap-3 w-full md:w-auto justify-end">
      <button
        data-testid="abandon-diagnostic-btn"
        :disabled="isAbandoning"
        class="px-5 py-3 rounded-xl bg-surface-bright/80 text-on-surface-variant hover:bg-error-container hover:text-error transition-all text-sm font-bold disabled:opacity-50"
        @click="abandonDiagnostic"
      >
        {{ t('diagnostic.resumeBanner.abandon') }}
      </button>

      <button
        data-testid="resume-diagnostic-btn"
        class="px-6 py-3 rounded-xl bg-primary text-on-primary hover:bg-primary/90 transition-all font-bold text-sm md:text-base shadow-md flex items-center gap-2 active:scale-95"
        @click="resumeDiagnostic"
      >
        <span>{{ t('diagnostic.resumeBanner.resume') }}</span>
        <span class="material-symbols-outlined text-xl">arrow_back</span>
      </button>
    </div>
  </div>
</template>
