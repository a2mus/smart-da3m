<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const stats = ref({
  totalModules: 12,
  totalStudents: 48,
  pendingAlerts: 7,
})
</script>

<template>
  <div
    dir="rtl"
    class="min-h-screen bg-surface px-4 py-8"
  >
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-black text-teal-700 mb-2">
        {{ t('expert.dashboardTitle') }}
      </h1>
      <p class="text-ink-500 mb-8">
        {{ t('expert.welcomeSubtitle') }}
      </p>

      <!-- Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div class="bg-surface-container rounded-2xl p-6 text-center border border-ink-100">
          <span class="material-symbols-outlined text-4xl text-teal-600 mb-2">menu_book</span>
          <p class="text-3xl font-black text-teal-700">
            {{ stats.totalModules }}
          </p>
          <p class="text-sm text-ink-500 mt-1">
            {{ t('expert.learningUnit') }}
          </p>
        </div>
        <div class="bg-surface-container rounded-2xl p-6 text-center border border-ink-100">
          <span class="material-symbols-outlined text-4xl text-ochre-600 mb-2">group</span>
          <p class="text-3xl font-black text-ochre-700">
            {{ stats.totalStudents }}
          </p>
          <p class="text-sm text-ink-500 mt-1">
            {{ t('expert.studentUnit') }}
          </p>
        </div>
        <div class="bg-surface-container rounded-2xl p-6 text-center border border-ink-100">
          <span class="material-symbols-outlined text-4xl text-rose-500 mb-2">notifications_active</span>
          <p class="text-3xl font-black text-rose-600">
            {{ stats.pendingAlerts }}
          </p>
          <p class="text-sm text-ink-500 mt-1">
            {{ t('expert.pendingAlert') }}
          </p>
        </div>
      </div>

      <!-- Navigation Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <router-link
          to="/expert/modules"
          class="bg-surface-container rounded-2xl p-6 border border-ink-100 hover:border-teal-300
                 hover:shadow-lg transition-all group flex items-center gap-4"
        >
          <span class="material-symbols-outlined text-4xl text-teal-600 group-hover:scale-110 transition-transform">library_books</span>
          <div>
            <p class="font-bold text-ink-800 text-lg">
              {{ t('expert.contentManagement') }}
            </p>
            <p class="text-sm text-ink-500">
              {{ t('expert.contentManagementDesc') }}
            </p>
          </div>
        </router-link>
        <router-link
          to="/expert/analytics"
          class="bg-surface-container rounded-2xl p-6 border border-ink-100 hover:border-teal-300
                 hover:shadow-lg transition-all group flex items-center gap-4"
        >
          <span class="material-symbols-outlined text-4xl text-teal-600 group-hover:scale-110 transition-transform">insights</span>
          <div>
            <p class="font-bold text-ink-800 text-lg">
              {{ t('expert.analyticsTitle') }}
            </p>
            <p class="text-sm text-ink-500">
              {{ t('expert.analyticsDesc') }}
            </p>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>