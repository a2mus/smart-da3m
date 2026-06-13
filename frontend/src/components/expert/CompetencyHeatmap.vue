<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { HeatmapResponse, HeatmapCell } from '@/services/analyticsService'

const { t } = useI18n()

const props = defineProps<{
  data: HeatmapResponse | null
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'cell-click', cell: HeatmapCell): void
  (e: 'student-click', studentId: string): void
}>()

// Build a matrix of cells for the heatmap
const heatmapMatrix = computed(() => {
  if (!props.data) return []

  const { students, competencies, cells } = props.data
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
  if (!masteryLevel) return t('analytics.noData')
  return t(`mastery.${masteryLevel.toLowerCase()}`)
}

const getCellTooltip = (cell: HeatmapCell | null) => {
  if (!cell) return t('analytics.noData')
  return `${getMasteryLabel(cell.mastery_level)} (${Math.round(cell.p_learned * 100)}%)`
}
</script>

<template>
  <div class="competency-heatmap">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!data || data.students.length === 0" class="text-center py-12 text-ink-600">
      <p class="text-lg">{{ t('analytics.noDataAvailable') }}</p>
      <p class="text-sm mt-1">{{ t('analytics.selectFilters') }}</p>
    </div>

    <!-- Heatmap Grid -->
    <div v-else class="heatmap-container overflow-x-auto">
      <div class="min-w-max">
        <!-- Header Row -->
        <div class="flex border-b-2 border-ink-200">
          <!-- Student Name Header -->
          <div class="w-40 flex-shrink-0 p-3 font-semibold text-ink-700 bg-ink-50 sticky left-0 z-10">
            {{ t('analytics.student') }}
          </div>
          <!-- Competency Headers -->
          <div
            v-for="competency in data.competencies"
            :key="competency"
            class="w-24 flex-shrink-0 p-3 text-center text-xs font-medium text-ink-700 bg-ink-50 border-l border-ink-200"
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
            class="w-40 flex-shrink-0 p-3 font-medium text-ink-800 sticky left-0 z-10 bg-surface cursor-pointer hover:text-teal-600"
            @click="emit('student-click', row.student.id)"
          >
            <div class="text-sm">{{ row.student.name }}</div>
            <div class="text-xs text-ink-500">{{ row.student.grade_level }}</div>
          </div>

          <!-- Competency Cells -->
          <div
            v-for="(cell, index) in row.cells"
            :key="`${row.student.id}-${data.competencies[index]}`"
            class="w-24 flex-shrink-0 p-2 border-l border-ink-100"
          >
            <div
              v-if="cell"
              class="h-12 rounded-lg flex items-center justify-center cursor-pointer transition-all hover:scale-105 hover:shadow-md"
              :style="{ backgroundColor: cell.color }"
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
    <div v-if="data && data.students.length > 0" class="mt-6 flex flex-wrap items-center gap-4 text-sm">
      <span class="font-medium text-ink-700">{{ t('analytics.legend') }}:</span>
      <div class="flex items-center gap-2">
        <div class="w-4 h-4 rounded" style="background-color: #86efac;"></div>
        <span class="text-ink-600">{{ t('mastery.mastered') }}</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-4 h-4 rounded" style="background-color: #d1fae5;"></div>
        <span class="text-ink-600">{{ t('mastery.proficient') }}</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-4 h-4 rounded" style="background-color: #fef9c3;"></div>
        <span class="text-ink-600">{{ t('mastery.familiar') }}</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-4 h-4 rounded" style="background-color: #fef3c7;"></div>
        <span class="text-ink-600">{{ t('mastery.attempted') }}</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-4 h-4 rounded" style="background-color: #fee2e2;"></div>
        <span class="text-ink-600">{{ t('mastery.not_started') }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.competency-heatmap {
  @apply w-full;
}

.heatmap-container {
  @apply rounded-xl border border-ink-200 bg-surface;
}
</style>