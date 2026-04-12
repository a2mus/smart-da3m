<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { KnowledgeAtom } from '@/services/remediationService'

const { t } = useI18n()

interface Props {
  atom: KnowledgeAtom
  isCompleted: boolean
  progressPercent: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'complete', timeMs: number, interactions: number): void
}>()

const startTime = ref<number>(Date.now())
const interactions = ref<number>(0)

const atomIcon = computed(() => {
  switch (props.atom.remediation_type) {
    case 'AUDIO_VISUAL':
      return '🎬'
    case 'SIMULATION':
      return '🎮'
    case 'MIND_MAP':
      return '🧠'
    default:
      return '📚'
  }
})

const atomTypeLabel = computed(() => {
  switch (props.atom.remediation_type) {
    case 'AUDIO_VISUAL':
      return t('remediation.audioVisual')
    case 'SIMULATION':
      return t('remediation.simulation')
    case 'MIND_MAP':
      return t('remediation.mindMap')
    default:
      return t('remediation.learning')
  }
})

const handleInteraction = () => {
  interactions.value++
}

const handleComplete = () => {
  const timeMs = Date.now() - startTime.value
  emit('complete', timeMs, interactions.value)
}
</script>

<template>
  <div class="bg-white rounded-2xl p-6 shadow-soft" data-testid="knowledge-atom">
    <!-- Header -->
    <div class="flex items-start gap-4 mb-6">
      <div class="text-4xl">{{ atomIcon }}</div>
      <div class="flex-1">
        <span class="text-xs font-medium text-primary-600 bg-primary-50 px-2 py-1 rounded-full">
          {{ atomTypeLabel }}
        </span>
        <h2 class="text-xl font-bold text-warm-800 mt-2">{{ atom.content.title }}</h2>
        <p class="text-warm-600 mt-1">{{ atom.content.description }}</p>
      </div>
      <div v-if="isCompleted" class="text-green-500 text-2xl">✓</div>
    </div>

    <!-- Media Content -->
    <div v-if="atom.content.media_url" class="mb-6" @click="handleInteraction">
      <div class="aspect-video bg-warm-100 rounded-xl flex items-center justify-center">
        <div class="text-6xl">▶️</div>
      </div>
    </div>

    <!-- Interactive Content for SIMULATION -->
    <div v-if="atom.remediation_type === 'SIMULATION'" class="mb-6 p-6 bg-warm-50 rounded-xl" @click="handleInteraction">
      <div class="flex justify-center gap-4">
        <div class="w-16 h-16 bg-primary-200 rounded-lg flex items-center justify-center text-2xl cursor-pointer hover:bg-primary-300 transition-colors">
          🟢
        </div>
        <div class="w-16 h-16 bg-warm-200 rounded-lg flex items-center justify-center text-2xl cursor-pointer hover:bg-warm-300 transition-colors">
          🔵
        </div>
        <div class="w-16 h-16 bg-warm-200 rounded-lg flex items-center justify-center text-2xl cursor-pointer hover:bg-warm-300 transition-colors">
          🟡
        </div>
      </div>
      <p class="text-center text-warm-600 mt-4">{{ t('remediation.dragToInteract') }}</p>
    </div>

    <!-- Mind Map Content -->
    <div v-if="atom.remediation_type === 'MIND_MAP'" class="mb-6 p-6 bg-warm-50 rounded-xl" @click="handleInteraction">
      <div class="flex flex-wrap justify-center gap-3">
        <div class="px-4 py-2 bg-primary-500 text-white rounded-full text-sm">{{ t('remediation.mainConcept') }}</div>
        <div class="px-4 py-2 bg-primary-200 text-primary-800 rounded-full text-sm">{{ t('remediation.subConcept1') }}</div>
        <div class="px-4 py-2 bg-primary-200 text-primary-800 rounded-full text-sm">{{ t('remediation.subConcept2') }}</div>
        <div class="px-4 py-2 bg-warm-200 text-warm-700 rounded-full text-sm">{{ t('remediation.related') }}</div>
      </div>
    </div>

    <!-- Progress -->
    <div class="mb-6">
      <div class="flex justify-between text-sm text-warm-600 mb-1">
        <span>{{ t('remediation.pathwayProgress') }}</span>
        <span>{{ Math.round(progressPercent) }}%</span>
      </div>
      <div class="h-2 bg-warm-200 rounded-full overflow-hidden">
        <div class="h-full bg-primary-500 rounded-full transition-all duration-500" :style="{ width: `${progressPercent}%` }"></div>
      </div>
    </div>

    <!-- Complete Button -->
    <button
      v-if="!isCompleted"
      @click="handleComplete"
      class="w-full py-4 bg-primary-500 hover:bg-primary-600 text-white font-semibold rounded-xl transition-colors"
    >
      {{ t('remediation.markComplete') }}
    </button>
    <div
      v-else
      class="w-full py-4 bg-green-100 text-green-700 font-semibold rounded-xl text-center"
    >
      {{ t('remediation.completed') }} ✓
    </div>
  </div>
</template>
