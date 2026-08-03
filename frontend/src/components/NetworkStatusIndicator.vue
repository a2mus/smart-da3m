<template>
  <div
    v-if="!isOnline || isSyncing || pendingCount > 0"
    class="w-full transition-all duration-300 ease-in-out"
    role="status"
    aria-live="polite"
  >
    <!-- Offline status banner -->
    <div
      v-if="!isOnline"
      class="flex items-center justify-between px-4 py-2 bg-secondary-container text-on-surface-variant border-b border-outline-variant text-sm"
    >
      <div class="flex items-center gap-2">
        <svg
          class="w-4 h-4 text-secondary shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M18.364 5.636a9 9 0 010 12.728m-2.828-2.829a5 5 0 010-7.07 1 1 0 011.414-1.414 7 7 0 010 9.9 1 1 0 01-1.414-1.414zM5.636 5.636a9 9 0 000 12.728m2.828-2.829a5 5 0 000-7.07 1 1 0 00-1.414-1.414 7 7 0 000 9.9 1 1 0 001.414-1.414zM12 12a1 1 0 100-2 1 1 0 000 2z"
          />
        </svg>
        <span class="font-medium">
          {{ t('network.offlineMessage', 'أنت تعمل حالياً بدون اتصال بالإنترنت. سيتم حفظ إجاباتك ومزامنتها لاحقاً.') }}
        </span>
      </div>
      <span
        v-if="pendingCount > 0"
        class="text-xs px-2 py-0.5 rounded bg-surface-container text-on-surface-variant font-semibold ms-2"
      >
        {{ pendingCount }} {{ t('network.pendingItems', 'إجابات معلقة') }}
      </span>
    </div>

    <!-- Syncing status banner -->
    <div
      v-else-if="isSyncing"
      class="flex items-center justify-between px-4 py-2 bg-primary-container text-on-surface-variant border-b border-outline-variant text-sm"
    >
      <div class="flex items-center gap-2">
        <svg
          class="w-4 h-4 text-primary animate-spin shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
        <span class="font-medium">
          {{ t('network.syncingMessage', 'جاري مزامنة الإجابات المحفوظة...') }}
        </span>
      </div>
    </div>

    <!-- Pending items indicator when online -->
    <div
      v-else-if="pendingCount > 0"
      class="flex items-center justify-between px-4 py-2 bg-surface-container-high text-on-surface-variant border-b border-outline-variant text-sm"
    >
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-secondary" />
        <span class="text-xs">
          {{ pendingCount }} {{ t('network.pendingSyncNotice', 'إجابات بانتظار المزامنة') }}
        </span>
      </div>
      <button
        class="text-xs font-semibold text-primary hover:underline ms-2"
        @click="syncNow"
      >
        {{ t('network.syncNow', 'مزامنة الآن') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useOfflineSync } from '@/composables/useOfflineSync'
import { useI18n } from 'vue-i18n'

const { isOnline, isSyncing, pendingCount, syncNow } = useOfflineSync()
const { t } = useI18n()
</script>
