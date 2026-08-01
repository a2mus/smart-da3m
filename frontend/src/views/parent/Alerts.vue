<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAlertStore } from '@/stores/alertStore'
import { useSSE } from '@/composables/useSSE'
import { alertService } from '@/services/alertService'

const { t } = useI18n()
const alertStore = useAlertStore()

// Initialize real-time SSE event listener
useSSE({
  autoConnect: true,
  onAlert: (alert) => {
    alertStore.addAlertFromSSE(alert)
  },
})

const parentAlerts = computed(() => alertStore.parentAlerts)
const isLoading = computed(() => alertStore.isLoading)
const error = computed(() => alertStore.error)

const markAsRead = async (id: string) => {
  await alertStore.markAlertsRead([id])
}

const dismissAlert = (id: string) => {
  alertStore.dismissAlert(id)
}

const severityClasses: Record<string, string> = {
  CRITICAL: 'bg-error-container text-on-surface border-error',
  WARNING: 'bg-secondary-container text-on-surface border-secondary',
  INFO: 'bg-primary-container text-on-surface border-primary',
}

onMounted(() => {
  alertStore.fetchAlerts()
})
</script>

<template>
  <div
    class="min-h-screen bg-surface px-4 py-8"
  >
    <div class="max-w-xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-black text-primary">
          {{ t('alerts.title') }}
        </h1>
        <button
          v-if="parentAlerts.length > 0"
          class="text-xs text-primary font-bold hover:underline"
          @click="alertStore.fetchAlerts()"
        >
          {{ t('common.refresh') }}
        </button>
      </div>

      <!-- Loading state -->
      <div
        v-if="isLoading"
        class="text-center py-12"
      >
        <div class="animate-spin inline-block w-8 h-8 border-4 border-primary border-t-transparent rounded-full mb-3" />
        <p class="text-sm text-on-surface-variant">
          {{ t('common.loading') }}
        </p>
      </div>

      <!-- Error State -->
      <div
        v-else-if="error"
        class="p-4 bg-error-container text-on-surface rounded-2xl border border-error mb-4"
      >
        <p class="text-sm font-semibold">
          {{ error }}
        </p>
      </div>

      <!-- Empty state -->
      <div
        v-else-if="parentAlerts.length === 0"
        class="text-center py-12 bg-surface-bright rounded-2xl border border-outline-variant p-6"
      >
        <span class="text-4xl mb-3 block">🎉</span>
        <h2 class="text-lg font-bold text-on-surface mb-1">
          {{ t('alerts.noAlerts') }}
        </h2>
      </div>

      <!-- Alerts List -->
      <div
        v-else
        class="space-y-3"
      >
        <div
          v-for="a in parentAlerts"
          :key="a.id"
          class="rounded-2xl border p-4 flex items-start gap-3 transition-opacity"
          :class="[
            severityClasses[a.severity] || 'bg-surface-container text-on-surface border-outline',
            a.isRead || a.is_read ? 'opacity-60' : 'font-semibold'
          ]"
        >
          <span class="text-2xl shrink-0 mt-0.5">
            {{ alertService.getSeverityIcon(a.severity) }}
          </span>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-sm leading-relaxed">
              {{ a.message }}
            </p>
            <div class="flex items-center justify-between mt-2">
              <p class="text-xs opacity-70">
                {{ new Date(a.createdAt || a.created_at || '').toLocaleDateString() }}
              </p>
              <div class="flex gap-2">
                <button
                  v-if="!(a.isRead || a.is_read)"
                  class="text-xs text-primary font-bold hover:underline"
                  @click="markAsRead(a.id)"
                >
                  {{ t('alerts.markRead') }}
                </button>
                <button
                  class="text-xs text-on-surface-variant hover:text-on-surface"
                  @click="dismissAlert(a.id)"
                >
                  {{ t('common.dismiss') }}
                </button>
              </div>
            </div>
          </div>
          <span
            v-if="!(a.isRead || a.is_read)"
            class="w-2.5 h-2.5 rounded-full bg-primary shrink-0 mt-1.5"
          />
        </div>
      </div>
    </div>
  </div>
</template>
