<script setup lang="ts">
import { ref } from 'vue'

interface Alert {
  id: string
  severity: 'INFO' | 'WARNING' | 'CRITICAL'
  messageAr: string
  timestamp: string
  read: boolean
}

const alerts = ref<Alert[]>([
  { id: 'a1', severity: 'WARNING', messageAr: 'أحمد فشل في نفس نوع التمرين ٣ مرات في الكسور', timestamp: new Date().toISOString(), read: false },
  { id: 'a2', severity: 'INFO', messageAr: 'فاطمة أتمت وحدة الضرب بنجاح', timestamp: new Date(Date.now() - 86400000).toISOString(), read: true },
  { id: 'a3', severity: 'CRITICAL', messageAr: 'أحمد يحتاج دعماً فردياً في التعبير الكتابي', timestamp: new Date(Date.now() - 2 * 86400000).toISOString(), read: false },
  { id: 'a4', severity: 'INFO', messageAr: 'لم يسجل أحمد دخوله منذ ٥ أيام', timestamp: new Date(Date.now() - 5 * 86400000).toISOString(), read: false },
])

const severityColors: Record<string, string> = {
  INFO: 'bg-teal-100 text-teal-700 border-teal-300',
  WARNING: 'bg-amber-100 text-amber-700 border-amber-300',
  CRITICAL: 'bg-rose-100 text-rose-700 border-rose-300',
}
</script>

<template>
  <div
    dir="rtl"
    class="min-h-screen bg-surface px-4 py-8"
  >
    <div class="max-w-lg mx-auto">
      <h1 class="text-2xl font-black text-teal-700 mb-6">
        التنبيهات البيداغوجية
      </h1>
      <div class="space-y-3">
        <div
          v-for="a in alerts"
          :key="a.id"
          class="rounded-2xl border p-4 flex items-start gap-3"
          :class="[severityColors[a.severity], a.read ? 'opacity-60' : '']"
        >
          <span class="material-symbols-outlined text-2xl mt-0.5">
            {{ a.severity === 'CRITICAL' ? 'warning' : a.severity === 'WARNING' ? 'error' : 'info' }}
          </span>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-sm">
              {{ a.messageAr }}
            </p>
            <p class="text-xs opacity-60 mt-1">
              {{ new Date(a.timestamp).toLocaleDateString('ar') }}
            </p>
          </div>
          <span
            v-if="!a.read"
            class="w-2 h-2 rounded-full bg-current shrink-0 mt-1.5"
          />
        </div>
      </div>
    </div>
  </div>
</template>
