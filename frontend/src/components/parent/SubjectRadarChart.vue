<script setup lang="ts">
import { computed } from 'vue'

interface Subject {
  name: string
  score: number
  mastery_level: string
}

interface Props {
  subjects: Subject[]
}

const props = defineProps<Props>()

const processedSubjects = computed(() => {
  // Limit to 6 subjects for readability
  const limited = props.subjects.slice(0, 6)
  
  return limited.map(subject => ({
    ...subject,
    normalizedScore: subject.score > 1 ? subject.score : Math.round(subject.score * 100)
  }))
})

const chartData = computed(() => {
  const subjects = processedSubjects.value
  if (subjects.length === 0) return null

  const centerX = 150
  const centerY = 150
  const radius = 100
  const angleStep = (2 * Math.PI) / subjects.length

  // Calculate polygon points
  const points = subjects.map((subject, index) => {
    const angle = index * angleStep - Math.PI / 2 // Start from top
    const r = (subject.normalizedScore / 100) * radius
    const x = centerX + r * Math.cos(angle)
    const y = centerY + r * Math.sin(angle)
    return `${x},${y}`
  }).join(' ')

  // Calculate axis end points
  const axes = subjects.map((_, index) => {
    const angle = index * angleStep - Math.PI / 2
    const x = centerX + radius * Math.cos(angle)
    const y = centerY + radius * Math.sin(angle)
    return { x, y, angle }
  })

  // Calculate label positions
  const labels = subjects.map((subject, index) => {
    const angle = index * angleStep - Math.PI / 2
    const labelRadius = radius + 25
    const x = centerX + labelRadius * Math.cos(angle)
    const y = centerY + labelRadius * Math.sin(angle)
    return { x, y, text: subject.name }
  })

  return { points, axes, labels, centerX, centerY, radius }
})

const getScoreColor = (score: number) => {
  if (score >= 80) return '#22c55e' // green-500
  if (score >= 60) return '#3b82f6' // blue-500
  if (score >= 40) return '#eab308' // yellow-500
  return '#ef4444' // red-500
}

const averageScore = computed(() => {
  if (processedSubjects.value.length === 0) return 0
  const total = processedSubjects.value.reduce((sum, s) => sum + s.normalizedScore, 0)
  return Math.round(total / processedSubjects.value.length)
})
</script>

<template>
  <div data-testid="radar-chart" class="relative" aria-label="Subject progress radar chart">
    <!-- Empty State -->
    <div v-if="processedSubjects.length === 0" data-testid="empty-state" class="text-center py-8 text-warm-500">
      {{ $t('parent.noData') }}
    </div>

    <!-- Chart -->
    <div v-else class="flex flex-col items-center">
      <svg 
        data-testid="chart-svg"
        viewBox="0 0 300 300" 
        class="w-full max-w-[300px] h-auto"
      >
        <!-- Background circles (grid) -->
        <g data-testid="grid-circles">
          <circle 
            v-for="i in 4" 
            :key="i"
            :cx="chartData?.centerX"
            :cy="chartData?.centerY"
            :r="(chartData?.radius || 100) * (i / 4)"
            fill="none"
            stroke="#e5e7eb"
            stroke-width="1"
            data-testid="grid-circle"
          />
        </g>

        <!-- Axes -->
        <g data-testid="axes">
          <line
            v-for="(axis, index) in chartData?.axes"
            :key="index"
            :x1="chartData?.centerX"
            :y1="chartData?.centerY"
            :x2="axis.x"
            :y2="axis.y"
            stroke="#d1d5db"
            stroke-width="1"
            data-testid="radar-axis"
          />
        </g>

        <!-- Data polygon -->
        <polygon
          v-if="chartData?.points"
          :points="chartData.points"
          :fill="getScoreColor(averageScore)"
          fill-opacity="0.3"
          :stroke="getScoreColor(averageScore)"
          stroke-width="2"
          data-testid="radar-polygon"
        />

        <!-- Data points -->
        <g v-if="chartData">
          <circle
            v-for="(subject, index) in processedSubjects"
            :key="`point-${index}`"
            :cx="chartData.centerX + ((subject.normalizedScore / 100) * chartData.radius) * Math.cos(index * ((2 * Math.PI) / processedSubjects.length) - Math.PI / 2)"
            :cy="chartData.centerY + ((subject.normalizedScore / 100) * chartData.radius) * Math.sin(index * ((2 * Math.PI) / processedSubjects.length) - Math.PI / 2)"
            r="4"
            :fill="getScoreColor(subject.normalizedScore)"
            data-testid="subject-point"
          />
        </g>

        <!-- Labels -->
        <g data-testid="labels">
          <text
            v-for="(label, index) in chartData?.labels"
            :key="index"
            :x="label.x"
            :y="label.y"
            text-anchor="middle"
            dominant-baseline="middle"
            class="text-xs fill-warm-600"
            style="font-size: 10px;"
          >
            {{ label.text }}
          </text>
        </g>
      </svg>

      <!-- Legend -->
      <div class="flex flex-wrap justify-center gap-4 mt-4 text-xs">
        <div class="flex items-center gap-1">
          <div class="w-3 h-3 rounded-full bg-green-500"></div>
          <span class="text-warm-600">{{ $t('mastery.mastered') }}</span>
        </div>
        <div class="flex items-center gap-1">
          <div class="w-3 h-3 rounded-full bg-blue-500"></div>
          <span class="text-warm-600">{{ $t('mastery.proficient') }}</span>
        </div>
        <div class="flex items-center gap-1">
          <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
          <span class="text-warm-600">{{ $t('mastery.familiar') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
