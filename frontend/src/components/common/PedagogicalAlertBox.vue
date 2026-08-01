<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAlertStore } from '@/stores/alertStore'
import { useSSE } from '@/composables/useSSE'
import { alertService } from '@/services/alertService'

const { t } = useI18n()

interface Props {
  childId?: string
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  compact: false,
})

const alertStore = useAlertStore()
const expanded = ref(false)

// Connect to real-time SSE stream and feed alerts directly into alertStore
useSSE({
  autoConnect: true,
  onAlert: (alert) => {
    alertStore.addAlertFromSSE(alert)
  },
})

const unreadCount = computed(() => alertStore.unreadCount)
const hasCritical = computed(() => alertStore.hasCritical)
const alerts = computed(() => alertStore.sortedAlerts)
const loading = computed(() => alertStore.isLoading)

const fetchAlerts = async () => {
  await alertStore.fetchAlerts(false, props.childId)
}

const markAsRead = async (alertId: string) => {
  await alertStore.markAlertsRead([alertId])
}

const dismissAlert = (alertId: string) => {
  alertStore.dismissAlert(alertId)
}

const formatTimeAgo = (timestamp?: string) => {
  if (!timestamp) return t('time.justNow')
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(hours / 24)

  if (hours < 1) return t('time.justNow')
  if (hours < 24) return t('time.hoursAgo', { hours })
  return t('time.daysAgo', { days })
}

onMounted(fetchAlerts)
</script>

<template>
  <div
    data-testid="pedagogical-alert-box"
    class="relative"
  >
    <!-- Compact View (Badge) -->
    <button
      v-if="compact"
      class="relative p-2 rounded-full hover:bg-surface-container-low transition-colors"
      @click="expanded = !expanded"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        class="w-6 h-6 text-on-surface-variant"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0"
        />
      </svg>
      <span
        v-if="unreadCount > 0"
        :class="[
          'absolute top-0 end-0 w-5 h-5 rounded-full text-xs flex items-center justify-center text-on-primary font-bold',
          hasCritical ? 'bg-error' : 'bg-primary'
        ]"
      >
        {{ unreadCount }}
      </span>
    </button>

    <!-- Expanded View -->
    <div
      v-else
      class="bg-surface-bright rounded-2xl shadow-md overflow-hidden border border-outline-variant"
      :class="{ 'border-2 border-error': hasCritical }"
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-outline-variant">
        <div class="flex items-center gap-2">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="w-6 h-6 text-primary"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0"
            />
          </svg>
          <h3 class="font-bold text-on-surface">
            {{ t('alerts.title') }}
          </h3>
          <span
            v-if="unreadCount > 0"
            class="bg-primary text-on-primary text-xs px-2 py-0.5 rounded-full font-semibold"
          >
            {{ unreadCount }}
          </span>
        </div>
        <button
          v-if="alerts.length > 0"
          class="text-sm text-primary hover:underline font-medium"
          @click="fetchAlerts"
        >
          {{ t('common.refresh') }}
        </button>
      </div>

      <!-- Loading -->
      <div
        v-if="loading"
        class="text-center py-8"
      >
        <div class="animate-spin inline-block w-6 h-6 border-2 border-primary border-t-transparent rounded-full" />
      </div>

      <!-- Empty State -->
      <div
        v-else-if="alerts.length === 0"
        class="text-center py-8 text-on-surface-variant"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="w-12 h-12 text-tertiary mx-auto mb-2"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
          />
        </svg>
        <p class="text-sm">
          {{ t('alerts.noAlerts') }}
        </p>
      </div>

      <!-- Alerts List -->
      <div
        v-else
        class="max-h-80 overflow-y-auto"
      >
        <div
          v-for="alert in alerts"
          :key="alert.id"
          :class="[
            'p-4 border-b border-outline-variant last:border-b-0 transition-colors',
            alert.severity === 'CRITICAL' ? 'bg-error-container text-on-surface' :
            alert.severity === 'WARNING' ? 'bg-secondary-container text-on-surface' :
            'bg-tertiary-container text-on-surface',
            !(alert.isRead || alert.is_read) ? 'border-s-4 border-s-primary' : 'opacity-75'
          ]"
        >
          <div class="flex items-start gap-3">
            <span class="text-xl">
              {{ alertService.getSeverityIcon(alert.severity) }}
            </span>
            <div class="flex-1 min-w-0">
              <p class="text-sm text-on-surface leading-relaxed font-medium">
                {{ alert.simplifiedMessage || alert.simplified_message || alert.message }}
              </p>
              <div class="flex items-center justify-between mt-2">
                <span class="text-xs text-on-surface-variant">
                  {{ formatTimeAgo(alert.createdAt || alert.created_at) }}
                </span>
                <div class="flex gap-2">
                  <button
                    v-if="!(alert.isRead || alert.is_read)"
                    class="text-xs text-primary font-bold hover:underline"
                    @click="markAsRead(alert.id)"
                  >
                    {{ t('alerts.markRead') }}
                  </button>
                  <button
                    class="text-xs text-on-surface-variant hover:text-on-surface"
                    @click="dismissAlert(alert.id)"
                  >
                    {{ t('common.dismiss') }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- View All Link -->
      <div
        v-if="alerts.length > 0"
        class="p-3 border-t border-outline-variant text-center"
      >
        <router-link
          to="/parent/alerts"
          class="text-sm text-primary hover:underline font-semibold"
        >
          {{ t('alerts.viewAll') }} →
        </router-link>
      </div>
    </div>

    <!-- Dropdown for Compact Mode -->
    <div
      v-if="compact && expanded"
      class="absolute end-0 top-full mt-2 w-80 bg-surface-bright rounded-xl shadow-lg border border-outline-variant z-50"
    >
      <div class="p-3 border-b border-outline-variant flex justify-between items-center">
        <span class="font-semibold text-on-surface">{{ t('alerts.title') }}</span>
        <button
          class="text-on-surface-variant hover:text-on-surface"
          @click="expanded = false"
        >
          ×
        </button>
      </div>
      <div class="max-h-64 overflow-y-auto">
        <div
          v-if="alerts.length === 0"
          class="p-4 text-center text-on-surface-variant text-sm"
        >
          {{ t('alerts.noAlerts') }}
        </div>
        <div
          v-for="alert in alerts.slice(0, 5)"
          :key="alert.id"
          class="p-3 border-b border-outline-variant last:border-b-0 hover:bg-surface-container-low"
        >
          <div class="flex items-start gap-2">
            <span>{{ alertService.getSeverityIcon(alert.severity) }}</span>
            <p class="text-sm text-on-surface line-clamp-2">
              {{ alert.simplifiedMessage || alert.simplified_message || alert.message }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
