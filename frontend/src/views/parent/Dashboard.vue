<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import AppHeader from '@/components/common/AppHeader.vue'
import SubjectRadarChart from '@/components/parent/SubjectRadarChart.vue'
import InsightCard from '@/components/parent/InsightCard.vue'
import { useDashboardStore } from '@/stores/dashboardStore'

const { t } = useI18n()
const dashboardStore = useDashboardStore()

const children = computed(() => dashboardStore.children)
const selectedChildId = computed(() => dashboardStore.selectedChildId)
const childData = computed(() => dashboardStore.currentChildData)
const loading = computed(() => dashboardStore.loading)
const error = computed(() => dashboardStore.error)

const selectChild = (childId: string) => {
  dashboardStore.selectChild(childId)
}

const getMasteryColor = (level?: string) => {
  switch (level) {
    case 'MASTERED': return 'bg-mint-500'
    case 'PROFICIENT': return 'bg-teal-500'
    case 'FAMILIAR': return 'bg-amber-500'
    case 'ATTEMPTED': return 'bg-ochre-500'
    default: return 'bg-ink-300'
  }
}

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'DIAGNOSTIC': return '📝'
    case 'REMEDIATION': return '📚'
    case 'PASSPORT': return '🛂'
    case 'ACHIEVEMENT': return '🏆'
    default: return '📌'
  }
}

const formatRelativeTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return t('time.today')
  if (days === 1) return t('time.yesterday')
  if (days < 7) return t('time.daysAgo', { days })
  return date.toLocaleDateString()
}

onMounted(() => {
  dashboardStore.fetchChildren()
})
</script>

<template>
  <div class="min-h-screen bg-ink-50">
    <AppHeader />
    <!-- Mobile-First Header -->
    <div class="bg-surface shadow-sm sticky top-0 z-10">
      <div class="max-w-lg mx-auto px-4 py-4">
        <h1 class="text-xl font-bold text-teal-700">
          {{ t('parent.dashboard') }}
        </h1>

        <!-- Child Selector -->
        <div
          v-if="children.length > 1"
          class="mt-3 flex gap-2 overflow-x-auto pb-2"
        >
          <button
            v-for="child in children"
            :key="child.childId || child.child_id"
            :class="[
              'flex items-center gap-2 px-4 py-2 rounded-full whitespace-nowrap transition-colors',
              selectedChildId === (child.childId || child.child_id)
                ? 'bg-teal-500 text-on-primary'
                : 'bg-ink-100 text-ink-700 hover:bg-ink-200'
            ]"
            @click="selectChild(child.childId || child.child_id || '')"
          >
            <span class="w-8 h-8 bg-surface/20 rounded-full flex items-center justify-center text-sm">
              {{ child.name.charAt(0) }}
            </span>
            <span class="text-sm font-medium">{{ child.name }}</span>
            <span
              v-if="child.needsAttention || child.needs_attention"
              class="w-2 h-2 bg-rose-500 rounded-full"
            />
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-lg mx-auto px-4 py-6">
      <!-- Loading -->
      <div
        v-if="loading"
        class="text-center py-12"
      >
        <div class="animate-spin inline-block w-10 h-10 border-4 border-teal-500 border-t-transparent rounded-full" />
        <p class="mt-3 text-ink-600">
          {{ t('common.loading') }}
        </p>
      </div>

      <!-- Error -->
      <div
        v-else-if="error"
        class="bg-rose-50 border border-rose-200 text-rose-600 px-4 py-3 rounded-xl mb-4"
      >
        {{ error }}
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!childData"
        class="text-center py-12 text-ink-600"
      >
        <div class="text-6xl mb-4">
          👨‍gsub👨‍👧
        </div>
        <p class="text-lg">
          {{ t('parent.noChildren') }}
        </p>
      </div>

      <!-- Dashboard Content -->
      <div
        v-else
        class="space-y-6"
      >
        <!-- Welcome & Summary -->
        <div class="bg-surface rounded-2xl p-5 shadow-soft">
          <h2 class="text-lg font-bold text-ink-800 mb-2">
            {{ t('parent.hello', { name: childData.name }) }}
          </h2>
          <p class="text-ink-600 text-sm leading-relaxed">
            {{ childData.summary }}
          </p>

          <!-- Overall Progress -->
          <div class="mt-4 flex items-center gap-3">
            <div class="flex-1">
              <div class="flex justify-between text-sm mb-1">
                <span class="text-ink-600">{{ t('parent.overallProgress') }}</span>
                <span class="font-semibold text-teal-600">
                  {{ Math.round(childData.overallProgress ?? childData.overall_progress ?? 0) }}%
                </span>
              </div>
              <div class="h-2 bg-ink-200 rounded-full overflow-hidden">
                <div
                  class="h-full bg-teal-500 rounded-full transition-all duration-500"
                  :style="{ width: `${childData.overallProgress ?? childData.overall_progress ?? 0}%` }"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Radar Chart -->
        <div class="bg-surface rounded-2xl p-5 shadow-soft">
          <h3 class="text-lg font-bold text-ink-800 mb-4">
            {{ t('parent.subjectBalance') }}
          </h3>
          <SubjectRadarChart
            :subjects="childData.subjects"
            class="w-full"
          />
        </div>

        <!-- Subject Breakdown -->
        <div class="bg-surface rounded-2xl p-5 shadow-soft">
          <h3 class="text-lg font-bold text-ink-800 mb-4">
            {{ t('parent.subjects') }}
          </h3>
          <div class="space-y-3">
            <div
              v-for="subject in childData.subjects"
              :key="subject.competencyId || subject.competency_id"
              class="flex items-center gap-3 p-3 bg-ink-50 rounded-xl"
            >
              <div
                :class="['w-3 h-3 rounded-full', getMasteryColor(subject.masteryLevel || subject.mastery_level)]"
              />
              <div class="flex-1">
                <div class="flex justify-between items-center">
                  <span class="font-medium text-ink-800">{{ subject.name }}</span>
                  <span class="text-sm text-ink-600">{{ subject.score }}%</span>
                </div>
                <div class="text-xs text-ink-500 capitalize">
                  {{ t(`mastery.${(subject.masteryLevel || subject.mastery_level || '').toLowerCase()}`) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recommendations -->
        <div
          v-if="childData.recommendations && childData.recommendations.length > 0"
          class="bg-surface rounded-2xl p-5 shadow-soft"
        >
          <h3 class="text-lg font-bold text-ink-800 mb-4">
            {{ t('parent.recommendations') }}
          </h3>
          <div class="space-y-3">
            <InsightCard
              v-for="(rec, index) in childData.recommendations"
              :key="index"
              :title="rec.title"
              :description="rec.description"
              :duration="rec.duration"
              :priority="rec.priority"
            />
          </div>
        </div>

        <!-- Recent Activities -->
        <div
          v-if="(childData.recentActivities || childData.recent_activities || []).length > 0"
          class="bg-surface rounded-2xl p-5 shadow-soft"
        >
          <h3 class="text-lg font-bold text-ink-800 mb-4">
            {{ t('parent.recentActivities') }}
          </h3>
          <div class="grid grid-cols-2 gap-3">
            <div
              v-for="activity in (childData.recentActivities || childData.recent_activities || []).slice(0, 4)"
              :key="activity.timestamp"
              class="p-3 bg-ink-50 rounded-xl"
            >
              <div class="text-2xl mb-1">
                {{ getActivityIcon(activity.type) }}
              </div>
              <div class="text-sm font-medium text-ink-800 line-clamp-2">
                {{ activity.title }}
              </div>
              <div class="text-xs text-ink-500 mt-1">
                {{ formatRelativeTime(activity.timestamp) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
