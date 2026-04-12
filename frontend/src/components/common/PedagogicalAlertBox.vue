<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { alertService, type Alert } from '@/services/alertService'

const { t } = useI18n()

interface Props {
  childId?: string
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  compact: false,
})

const alerts = ref<Alert[]>([])
const loading = ref(true)
const expanded = ref(false)
const error = ref<string | null>(null)

const unreadCount = computed(() => {
  return alerts.value.filter(a => !a.is_read).length
})

const hasCritical = computed(() => {
  return alerts.value.some(a => a.severity === 'CRITICAL')
})

const fetchAlerts = async () => {
  loading.value = true
  error.value = null
  try {
    if (props.childId) {
      const parentAlerts = await alertService.getChildAlerts(props.childId)
      alerts.value = parentAlerts.map(a => ({
        id: a.id,
        student_id: '',
        trigger_type: 'INACTIVITY' as const,
        severity: a.severity,
        status: a.is_read ? 'READ' as const : 'UNREAD' as const,
        simplified_message: a.message,
        expert_message: a.message,
        context_data: {},
        created_at: a.created_at,
        is_read: a.is_read,
        message: a.message,
      }))
    } else {
      const response = await alertService.getAlerts(true)
      alerts.value = response.items.map(a => ({
        ...a,
        is_read: a.is_read ?? (a.status === 'READ'),
      }))
    }
  } catch (err) {
    error.value = t('errors.fetchFailed')
    console.error('Failed to fetch alerts:', err)
  } finally {
    loading.value = false
  }
}

const markAsRead = async (alertId: string) => {
  try {
    await alertService.markAlertsRead([alertId])
    const alert = alerts.value.find(a => a.id === alertId)
    if (alert) {
      alert.is_read = true
    }
  } catch (err) {
    console.error('Failed to mark alert as read:', err)
  }
}

const dismissAlert = (alertId: string) => {
  alerts.value = alerts.value.filter(a => a.id !== alertId)
}

const formatTimeAgo = (timestamp: string) => {
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
  <div data-testid="pedagogical-alert-box" class="relative">
    <!-- Compact View (Badge) -->
    <button
      v-if="compact"
      @click="expanded = !expanded"
      class="relative p-2 rounded-full hover:bg-warm-100 transition-colors"
    >
      <span class="text-2xl">🔔</span>
      <span
        v-if="unreadCount > 0"
        :class="[
          'absolute top-0 right-0 w-5 h-5 rounded-full text-xs flex items-center justify-center text-white font-bold',
          hasCritical ? 'bg-red-500' : 'bg-primary-500'
        ]"
      >
        {{ unreadCount }}
      </span>
    </button>

    <!-- Expanded View -->
    <div
      v-else
      class="bg-white rounded-2xl shadow-soft overflow-hidden"
      :class="{ 'border-2 border-red-200': hasCritical }"
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-warm-100">
        <div class="flex items-center gap-2">
          <span class="text-xl">🔔</span>
          <h3 class="font-bold text-warm-800">{{ t('alerts.title') }}</h3>
          <span
            v-if="unreadCount > 0"
            class="bg-primary-500 text-white text-xs px-2 py-0.5 rounded-full"
          >
            {{ unreadCount }}
          </span>
        </div>
        <button
          v-if="alerts.length > 0"
          @click="fetchAlerts"
          class="text-sm text-primary-600 hover:text-primary-700"
        >
          {{ t('common.refresh') }}
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-8">
        <div class="animate-spin inline-block w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full"></div>
      </div>

      <!-- Empty State -->
      <div v-else-if="alerts.length === 0" class="text-center py-8 text-warm-500">
        <div class="text-4xl mb-2">✅</div>
        <p class="text-sm">{{ t('alerts.noAlerts') }}</p>
      </div>

      <!-- Alerts List -->
      <div v-else class="max-h-80 overflow-y-auto">
        <div
          v-for="alert in alerts"
          :key="alert.id"
          :class="[
            'p-4 border-b border-warm-100 last:border-b-0 transition-colors',
            alert.severity === 'CRITICAL' ? 'bg-red-50' :
            alert.severity === 'WARNING' ? 'bg-yellow-50' :
            'bg-blue-50',
            !alert.is_read ? 'border-l-4' : 'opacity-75'
          ]"
          :style="{
            borderLeftColor: alert.severity === 'CRITICAL' ? '#ef4444' :
                            alert.severity === 'WARNING' ? '#eab308' : '#3b82f6'
          }"
        >
          <div class="flex items-start gap-3">
            <span class="text-xl">
              {{ alertService.getSeverityIcon(alert.severity) }}
            </span>
            <div class="flex-1 min-w-0">
              <p class="text-sm text-warm-800 leading-relaxed">
{{ alert.simplified_message || alert.message }}
              </p>
              <div class="flex items-center justify-between mt-2">
                <span class="text-xs text-warm-500">
                  {{ formatTimeAgo(alert.created_at) }}
                </span>
                <div class="flex gap-2">
                  <button
                    v-if="!alert.is_read"
                    @click="markAsRead(alert.id)"
                    class="text-xs text-primary-600 hover:text-primary-700 font-medium"
                  >
                    {{ t('alerts.markRead') }}
                  </button>
                  <button
                    @click="dismissAlert(alert.id)"
                    class="text-xs text-warm-400 hover:text-warm-600"
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
      <div v-if="alerts.length > 0" class="p-3 border-t border-warm-100 text-center">
        <router-link
          to="/parent/alerts"
          class="text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          {{ t('alerts.viewAll') }} →
        </router-link>
      </div>
    </div>

    <!-- Dropdown for Compact Mode -->
    <div
      v-if="compact && expanded"
      class="absolute right-0 top-full mt-2 w-80 bg-white rounded-xl shadow-lg z-50"
    >
      <div class="p-3 border-b border-warm-100 flex justify-between items-center">
        <span class="font-semibold text-warm-800">{{ t('alerts.title') }}</span>
        <button @click="expanded = false" class="text-warm-400 hover:text-warm-600">×</button>
      </div>
      <div class="max-h-64 overflow-y-auto">
        <div v-if="alerts.length === 0" class="p-4 text-center text-warm-500 text-sm">
          {{ t('alerts.noAlerts') }}
        </div>
        <div
          v-for="alert in alerts.slice(0, 5)"
          :key="alert.id"
          class="p-3 border-b border-warm-100 last:border-b-0 hover:bg-warm-50"
        >
          <div class="flex items-start gap-2">
            <span>{{ alertService.getSeverityIcon(alert.severity) }}</span>
            <p class="text-sm text-warm-700 line-clamp-2">
              {{ alert.simplified_message || alert.message }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
