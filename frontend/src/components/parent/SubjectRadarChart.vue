<script setup lang="ts">
import { computed } from 'vue'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement,
  RadialLinearScale,
  Filler
} from 'chart.js'
import { Radar } from 'vue-chartjs'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement,
  RadialLinearScale,
  Filler
)

const props = defineProps<{
  subjects: {
    name: string
    score: number
    competency_id?: string
    competencyId?: string
    masteryLevel?: string
    mastery_level?: string
  }[]
}>()

const chartData = computed(() => {
  const labels = props.subjects.map((s) => s.name)
  const data = props.subjects.map((s) => (s.score > 1 ? s.score / 100 : s.score))

  return {
    labels,
    datasets: [
      {
        label: 'مستوى التحكم',
        data,
        backgroundColor: 'rgba(0, 83, 91, 0.2)',
        borderColor: '#00535b',
        borderWidth: 2,
        pointBackgroundColor: '#00535b',
        pointBorderColor: '#ffffff',
        pointHoverBackgroundColor: '#ffffff',
        pointHoverBorderColor: '#00535b',
        pointRadius: 4,
        pointHoverRadius: 6
      }
    ]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      rtl: true,
      callbacks: {
        label: (context: { dataset: { label?: string }; raw: unknown }) => {
          const val = Number(context.raw) || 0
          const percentage = Math.round(val * 100)
          return `${context.dataset.label || ''}: ${percentage}%`
        }
      }
    }
  },
  scales: {
    r: {
      min: 0,
      max: 1,
      ticks: {
        stepSize: 0.2,
        callback: (value: string | number) => `${Math.round(Number(value) * 100)}%`,
        backdropColor: 'transparent',
        color: '#7a786e',
        font: {
          family: 'Tajawal, Cairo, sans-serif',
          size: 10
        }
      },
      grid: {
        color: 'rgba(122, 120, 110, 0.2)'
      },
      angleLines: {
        color: 'rgba(122, 120, 110, 0.2)'
      },
      pointLabels: {
        color: '#1c1b19',
        font: {
          family: 'Tajawal, Cairo, sans-serif',
          size: 12,
          weight: 'bold' as const
        }
      }
    }
  }
}))
</script>

<template>
  <div class="w-full">
    <div
      v-if="!subjects || subjects.length === 0"
      class="text-center py-8 text-ink-400"
    >
      لا توجد بيانات للمواد
    </div>
    <div
      v-else
      class="w-full h-64 sm:h-80 relative"
    >
      <Radar
        :data="chartData"
        :options="chartOptions"
      />
    </div>
  </div>
</template>
