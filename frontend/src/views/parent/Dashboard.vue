<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { dashboardService, type ChildDashboardData, type ChildSummary } from '@/services/dashboardService'
import SubjectRadarChart from '@/components/parent/SubjectRadarChart.vue'
import InsightCard from '@/components/parent/InsightCard.vue'

const { t } = useI18n()

const children = ref<ChildSummary[]>([])
const selectedChildId = ref<string>('')
const childData = ref<ChildDashboardData | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

const fetchChildren = async () => {
  try {
    children.value = await dashboardService.getChildrenList()
    if (children.value.length > 0 && !selectedChildId.value) {
      selectedChildId.value = children.value[0].child_id
      await fetchChildData()
    }
  } catch (err) {
    error.value = t('errors.fetchFailed')
    console.error('Failed to fetch children:', err)
  }
}

const fetchChildData = async () => {
  if (!selectedChildId.value) return
  loading.value = true
  error.value = null
  try {
    childData.value = await dashboardService.getChildDetails(selectedChildId.value)
  } catch (err) {
    error.value = t('errors.fetchFailed')
    console.error('Failed to fetch child data:', err)
  } finally {
    loading.value = false
  }
}

const selectChild = async (childId: string) => {
  selectedChildId.value = childId
  await fetchChildData()
}

const getMasteryColor = (level: string) => {
  switch (level) {
    case 'MASTERED': return 'bg-green-500'
    case 'PROFICIENT': return 'bg-blue-500'
    case 'FAMILIAR': return 'bg-yellow-500'
    case 'ATTEMPTED': return 'bg-orange-500'
    default: return 'bg-gray-300'
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

onMounted(fetchChildren)
</script>

<template>
  <div class="min-h-screen bg-warm-50">
    <!-- Mobile-First Header -->
    <div class="bg-white shadow-sm sticky top-0 z-10">
      <div class="max-w-lg mx-auto px-4 py-4">
        <h1 class="text-xl font-bold text-primary-700">{{ t('parent.dashboard') }}</h1>
        
        <!-- Child Selector -->
        <div v-if="children.length > 1" class="mt-3 flex gap-2 overflow-x-auto pb-2">
          <button
            v-for="child in children"
            :key="child.child_id"
            @click="selectChild(child.child_id)"
            :class="[
              'flex items-center gap-2 px-4 py-2 rounded-full whitespace-nowrap transition-colors',
              selectedChildId === child.child_id
                ? 'bg-primary-500 text-white'
                : 'bg-warm-100 text-warm-700 hover:bg-warm-200'
            ]"
          >
            <span class="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center text-sm">
              {{ child.name.charAt(0) }}
            </span>
            <span class="text-sm font-medium">{{ child.name }}</span>
            <span
              v-if="child.needs_attention"
              class="w-2 h-2 bg-red-500 rounded-full"
            ></span>
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-lg mx-auto px-4 py-6">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin inline-block w-10 h-10 border-4 border-primary-500 border-t-transparent rounded-full"></div>
        <p class="mt-3 text-warm-600">{{ t('common.loading') }}</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-4">
        {{ error }}
      </div>

      <!-- Empty State -->
      <div v-else-if="!childData" class="text-center py-12 text-warm-600">
        <div class="text-6xl mb-4">👨‍👩‍👧</div>
        <p class="text-lg">{{ t('parent.noChildren') }}</p>
      </div>

      <!-- Dashboard Content -->
      <div v-else class="space-y-6">
        <!-- Welcome & Summary -->
        <div class="bg-white rounded-2xl p-5 shadow-soft">
          <h2 class="text-lg font-bold text-warm-800 mb-2">
            {{ t('parent.hello', { name: childData.name }) }}
          </h2>
          <p class="text-warm-600 text-sm leading-relaxed">
            {{ childData.summary }}
          </p>
          
          <!-- Overall Progress -->
          <div class="mt-4 flex items-center gap-3">
            <div class="flex-1">
              <div class="flex justify-between text-sm mb-1">
                <span class="text-warm-600">{{ t('parent.overallProgress') }}</span>
                <span class="font-semibold text-primary-600">{{ Math.round(childData.overall_progress) }}%</span>
              </div>
              <div class="h-2 bg-warm-200 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-primary-500 rounded-full transition-all duration-500"
                  :style="{ width: `${childData.overall_progress}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Radar Chart -->
        <div class="bg-white rounded-2xl p-5 shadow-soft">
          <h3 class="text-lg font-bold text-warm-800 mb-4">{{ t('parent.subjectBalance') }}</h3>
          <SubjectRadarChart 
            :subjects="childData.subjects"
            class="w-full"
          />
        </div>

        <!-- Subject Breakdown -->
        <div class="bg-white rounded-2xl p-5 shadow-soft">
          <h3 class="text-lg font-bold text-warm-800 mb-4">{{ t('parent.subjects') }}</h3>
          <div class="space-y-3">
            <div
              v-for="subject in childData.subjects"
              :key="subject.competency_id"
              class="flex items-center gap-3 p-3 bg-warm-50 rounded-xl"
            >
              <div 
                :class="['w-3 h-3 rounded-full', getMasteryColor(subject.mastery_level)]"
              ></div>
              <div class="flex-1">
                <div class="flex justify-between items-center">
                  <span class="font-medium text-warm-800">{{ subject.name }}</span>
                  <span class="text-sm text-warm-600">{{ subject.score }}%</span>
                </div>
                <div class="text-xs text-warm-500 capitalize">
                  {{ t(`mastery.${subject.mastery_level.toLowerCase()}`) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recommendations -->
        <div v-if="childData.recommendations.length > 0" class="bg-white rounded-2xl p-5 shadow-soft">
          <h3 class="text-lg font-bold text-warm-800 mb-4">{{ t('parent.recommendations') }}</h3>
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
        <div v-if="childData.recent_activities.length > 0" class="bg-white rounded-2xl p-5 shadow-soft">
          <h3 class="text-lg font-bold text-warm-800 mb-4">{{ t('parent.recentActivities') }}</h3>
          <div class="grid grid-cols-2 gap-3">
            <div
              v-for="activity in childData.recent_activities.slice(0, 4)"
              :key="activity.timestamp"
              class="p-3 bg-warm-50 rounded-xl"
            >
              <div class="text-2xl mb-1">{{ getActivityIcon(activity.type) }}</div>
              <div class="text-sm font-medium text-warm-800 line-clamp-2">{{ activity.title }}</div>
              <div class="text-xs text-warm-500 mt-1">{{ formatRelativeTime(activity.timestamp) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
