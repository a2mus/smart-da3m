<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAnalyticsStore } from '@/stores/analyticsStore'
import type { HeatmapResponse, HeatmapCell } from '@/services/analyticsService'

const { t } = useI18n()
const analyticsStore = useAnalyticsStore()

const props = defineProps<{
  data?: HeatmapResponse | null
  loading?: boolean
  moduleId?: string
}>()

const emit = defineEmits<{
  (e: 'cell-click', cell: HeatmapCell): void
  (e: 'student-click', studentId: string): void
}>()

onMounted(() => {
  if (!props.data && !analyticsStore.heatmapData) {
    analyticsStore.fetchHeatmap(props.moduleId)
  }
})

watch(
  () => props.moduleId,
  (newModuleId) => {
    if (!props.data) {
      analyticsStore.fetchHeatmap(newModuleId)
    }
  }
)

const currentData = computed(() => props.data ?? analyticsStore.heatmapData)
const isLoading = computed(() => props.loading ?? analyticsStore.loading)

// Build a matrix of cells for the heatmap
const heatmapMatrix = computed(() => {
  if (!currentData.value) return []

  const { students, competencies, cells } = currentData.value
  const matrix: Array<{
    student: { id: string; name: string; grade_level: string }
    cells: Array<HeatmapCell | null>
  }> = []

  for (const student of students) {
    const rowCells: Array<HeatmapCell | null> = []
    for (const competencyId of competencies) {
      const cell = cells.find(
        (c) => c.student_id === student.id && c.competency_id === competencyId
      )
      rowCells.push(cell || null)
    }
    matrix.push({ student, cells: rowCells })
  }

  return matrix
})

const getMasteryLabel = (masteryLevel?: string) => {
  if (!masteryLevel) return t('analytics.noData', 'لا توجد بيانات')
  return t(`mastery.${masteryLevel.toLowerCase()}`, masteryLevel)
}

const getCellBgColor = (masteryLevel: string) => {
  switch (masteryLevel.toUpperCase()) {
    case 'MASTERED':
    case 'PROFICIENT':
      return '#86efac' // Green
    case 'FAMILIAR':
      return '#fef9c3' // Yellow
    case 'ATTEMPTED':
    case 'NOT_STARTED':
    default:
      return '#fee2e2' // Red
  }
}

const getCellTooltip = (cell: HeatmapCell | null) => {
  if (!cell) return t('analytics.noData', 'لا توجد بيانات')
  return `${getMasteryLabel(cell.mastery_level)} (${Math.round(cell.score)}%)`
}

const toggleAutoGroups = () => {
  analyticsStore.toggleAutoGroupsOverlay()
}

const changeGroupBy = (groupBy: string) => {
  analyticsStore.fetchStudentGroups(groupBy)
}

const handleExportPdf = () => {
  analyticsStore.exportReport('pdf', 'heatmap')
}

const handleExportCsv = () => {
  analyticsStore.exportReport('csv', 'heatmap')
}

const handlePrintCards = () => {
  analyticsStore.triggerPrintCards()
}
</script>

<template>
  <div class="competency-heatmap">
    <!-- Auto-Grouping & Export Control Toolbar -->
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3 bg-surface-container-low p-3 rounded-lg border border-outline-variant">
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="px-3 py-1.5 text-xs font-semibold rounded-md transition-colors border"
          :class="analyticsStore.showAutoGroupsOverlay ? 'bg-primary text-on-primary border-primary' : 'bg-surface-bright text-on-surface border-outline-variant hover:bg-surface-container'"
          @click="toggleAutoGroups"
        >
          {{ analyticsStore.showAutoGroupsOverlay ? t('analytics.hideAutoGroups', 'إخفاء مجموعات المعالجة') : t('analytics.showAutoGroups', 'عرض مجموعات المعالجة المقترحة') }}
        </button>

        <div class="h-4 w-px bg-outline-variant mx-1" />

        <button
          type="button"
          class="px-3 py-1.5 text-xs font-semibold rounded-md transition-colors bg-surface-bright text-on-surface border border-outline-variant hover:bg-surface-container flex items-center gap-1.5"
          @click="handleExportPdf"
        >
          <span class="i-lucide-file-text w-3.5 h-3.5 text-secondary" />
          {{ t('analytics.exportPdf', 'تصدير PDF') }}
        </button>

        <button
          type="button"
          class="px-3 py-1.5 text-xs font-semibold rounded-md transition-colors bg-surface-bright text-on-surface border border-outline-variant hover:bg-surface-container flex items-center gap-1.5"
          @click="handleExportCsv"
        >
          <span class="i-lucide-file-spread-sheet w-3.5 h-3.5 text-tertiary" />
          {{ t('analytics.exportCsv', 'تصدير CSV') }}
        </button>

        <button
          type="button"
          class="px-3 py-1.5 text-xs font-semibold rounded-md transition-colors bg-primary-container text-on-primary-container border border-primary-container hover:bg-primary-fixed flex items-center gap-1.5"
          @click="handlePrintCards"
        >
          <span class="material-symbols-outlined text-sm text-primary">print</span>
          {{ t('analytics.printRemediationCards', 'طباعة بطاقات المعالجة') }}
        </button>
      </div>

      <div
        v-if="analyticsStore.showAutoGroupsOverlay"
        class="flex items-center gap-2 text-xs"
      >
        <span class="text-on-surface-variant font-medium">{{ t('analytics.groupBy', 'تجميع حسب') }}:</span>
        <button
          type="button"
          class="px-2.5 py-1 rounded transition-colors"
          :class="analyticsStore.autoGroupBy === 'competency' ? 'bg-primary-container text-on-primary-container font-bold' : 'bg-surface-bright text-on-surface hover:bg-surface-container-high'"
          @click="changeGroupBy('competency')"
        >
          {{ t('analytics.groupByCompetency', 'الكفاءة') }}
        </button>
        <button
          type="button"
          class="px-2.5 py-1 rounded transition-colors"
          :class="analyticsStore.autoGroupBy === 'error_type' ? 'bg-primary-container text-on-primary-container font-bold' : 'bg-surface-bright text-on-surface hover:bg-surface-container-high'"
          @click="changeGroupBy('error_type')"
        >
          {{ t('analytics.groupByErrorType', 'نوع الخطأ') }}
        </button>
      </div>
    </div>

    <!-- Suggested Remediation Groups Overlay / Banner -->
    <div
      v-if="analyticsStore.showAutoGroupsOverlay && analyticsStore.studentGroups.length > 0"
      class="mb-6 bg-secondary-container/20 p-4 rounded-xl border border-secondary-container"
    >
      <h4 class="text-sm font-bold text-secondary mb-2">
        {{ t('analytics.suggestedRemediationGroups', 'مجموعات المعالجة المقترحة (آلياً)') }}
      </h4>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        <div
          v-for="group in analyticsStore.studentGroups"
          :key="group.group_id || group.name || group.group_name"
          class="bg-surface-bright p-3 rounded-lg border border-outline-variant shadow-sm"
        >
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-on-surface">{{ group.name || group.group_name }}</span>
            <span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-primary-fixed text-on-primary-fixed">
              {{ group.student_count }} {{ t('analytics.studentsCount', 'تلاميذ') }}
            </span>
          </div>
          <p class="text-xs text-on-surface-variant mt-1.5">
            {{ group.recommended_action }}
          </p>
        </div>
      </div>
    </div>
    <!-- Loading State -->
    <div
      v-if="isLoading"
      class="flex items-center justify-center py-12"
    >
      <div class="animate-spin w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full" />
    </div>

    <!-- Empty State -->
    <div
      v-else-if="!currentData || currentData.students.length === 0"
      class="text-center py-12 text-ink-600"
    >
      <p class="text-lg">
        {{ t('analytics.noDataAvailable', 'لا توجد بيانات متاحة حالياً') }}
      </p>
      <p class="text-sm mt-1">
        {{ t('analytics.selectFilters', 'اختر وحدة دراسية لعرض الخريطة الحرارية') }}
      </p>
    </div>

    <!-- Heatmap Grid -->
    <div
      v-else
      class="heatmap-container overflow-x-auto"
    >
      <div class="min-w-max">
        <!-- Header Row -->
        <div class="flex border-b-2 border-ink-200">
          <!-- Student Name Header -->
          <div class="w-40 flex-shrink-0 p-3 font-semibold text-ink-700 bg-ink-50 sticky start-0 z-10">
            {{ t('analytics.student', 'التلميذ') }}
          </div>
          <!-- Competency Headers -->
          <div
            v-for="competency in currentData.competencies"
            :key="competency"
            class="w-24 flex-shrink-0 p-3 text-center text-xs font-medium text-ink-700 bg-ink-50 border-s border-ink-200"
            :title="competency"
          >
            <span class="truncate block">{{ competency }}</span>
          </div>
        </div>

        <!-- Data Rows -->
        <div
          v-for="row in heatmapMatrix"
          :key="row.student.id"
          class="flex border-b border-ink-100 hover:bg-ink-50/50"
        >
          <!-- Student Name -->
          <div
            class="w-40 flex-shrink-0 p-3 font-medium text-ink-800 sticky start-0 z-10 bg-surface-bright cursor-pointer hover:text-teal-600"
            @click="emit('student-click', row.student.id)"
          >
            <div class="text-sm">
              {{ row.student.name }}
            </div>
            <div class="text-xs text-ink-500">
              {{ row.student.grade_level }}
            </div>
          </div>

          <!-- Competency Cells -->
          <div
            v-for="(cell, index) in row.cells"
            :key="`${row.student.id}-${currentData.competencies[index]}`"
            class="w-24 flex-shrink-0 p-2 border-s border-ink-100"
          >
            <div
              v-if="cell"
              class="h-12 rounded-lg flex items-center justify-center cursor-pointer transition-all hover:scale-105 hover:shadow-md"
              :style="{ backgroundColor: getCellBgColor(cell.mastery_level) }"
              :title="getCellTooltip(cell)"
              @click="emit('cell-click', cell)"
            >
              <span class="text-xs font-semibold text-ink-800">
                {{ Math.round(cell.score) }}%
              </span>
            </div>
            <div
              v-else
              class="h-12 rounded-lg bg-ink-100 flex items-center justify-center"
              :title="getCellTooltip(null)"
            >
              <span class="text-ink-400">-</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Legend -->
    <div
      v-if="currentData && currentData.students.length > 0"
      class="mt-6 flex flex-wrap items-center gap-4 text-sm"
    >
      <span class="font-medium text-ink-700">{{ t('analytics.legend', 'مفتاح الخريطة') }}:</span>
      <div class="flex items-center gap-2">
        <div
          class="w-4 h-4 rounded"
          style="background-color: #86efac;"
        />
        <span class="text-ink-600">{{ t('mastery.mastered', 'متقن') }} / {{ t('mastery.proficient', 'متمكن') }}</span>
      </div>
      <div class="flex items-center gap-2">
        <div
          class="w-4 h-4 rounded"
          style="background-color: #fef9c3;"
        />
        <span class="text-ink-600">{{ t('mastery.familiar', 'مكتسب جزئياً') }}</span>
      </div>
      <div class="flex items-center gap-2">
        <div
          class="w-4 h-4 rounded"
          style="background-color: #fee2e2;"
        />
        <span class="text-ink-600">{{ t('mastery.not_started', 'غير مكتسب') }} / {{ t('mastery.attempted', 'في طور الإكتساب') }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.competency-heatmap {
  @apply w-full;
}

.heatmap-container {
  @apply rounded-xl border border-ink-200 bg-surface-bright;
}
</style>
