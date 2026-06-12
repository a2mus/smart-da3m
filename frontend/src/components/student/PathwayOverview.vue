<script setup lang="ts">
import { computed } from 'vue'

export interface PathwayAtom {
  id: string
  title: string
  type: 'AUDIO_VISUAL' | 'SIMULATION' | 'MIND_MAP'
  status: 'locked' | 'available' | 'completed'
}

const props = defineProps<{
  atoms: PathwayAtom[]
  competencyName: string
  canTakePassport: boolean
}>()

const emit = defineEmits<{
  select: [atom: PathwayAtom]
  passport: []
}>()

const typeIcons: Record<string, string> = {
  AUDIO_VISUAL: 'play_circle',
  SIMULATION: 'joystick',
  MIND_MAP: 'account_tree',
}

const typeLabels: Record<string, string> = {
  AUDIO_VISUAL: 'سمعي بصري',
  SIMULATION: 'محاكاة',
  MIND_MAP: 'خريطة ذهنية',
}

const completed = computed(() => props.atoms.filter(a => a.status === 'completed').length)
const progress = computed(() => props.atoms.length > 0 ? Math.round((completed.value / props.atoms.length) * 100) : 0)
</script>

<template>
  <div class="max-w-lg mx-auto">
    <h2 class="text-2xl font-black text-primary text-center mb-2">{{ competencyName }}</h2>
    <p class="text-on-surface-variant text-center mb-6 text-sm">مسار التقوية الخاص بك</p>

    <!-- Progress -->
    <div class="mb-6">
      <div class="flex justify-between text-sm mb-1">
        <span class="text-on-surface-variant">{{ completed }} / {{ atoms.length }}</span>
        <span class="font-bold text-primary">{{ progress }}%</span>
      </div>
      <div class="w-full h-3 bg-ink-100 dark:bg-ink-700 rounded-full overflow-hidden">
        <div class="h-full bg-primary rounded-full transition-all duration-700" :style="{ width: progress + '%' }" />
      </div>
    </div>

    <!-- Atom list -->
    <div class="space-y-3 mb-8">
      <button
        v-for="(atom, i) in atoms"
        :key="atom.id"
        :disabled="atom.status === 'locked'"
        class="w-full flex items-center gap-4 p-4 rounded-2xl border-2 transition-all duration-200 text-start"
        :class="{
          'bg-surface-container border-outline-variant/50 cursor-pointer hover:border-primary hover:bg-primary/5 active:scale-[0.98]': atom.status === 'available',
          'bg-mint-50 border-mint-300 cursor-default': atom.status === 'completed',
          'bg-ink-50 dark:bg-ink-800 border-ink-100 dark:border-ink-700 cursor-not-allowed opacity-50': atom.status === 'locked',
        }"
        @click="atom.status === 'available' && emit('select', atom)"
      >
        <!-- Icon -->
        <div
          class="w-12 h-12 rounded-xl flex items-center justify-center shrink-0"
          :class="{
            'bg-primary/10 text-primary': atom.status === 'available',
            'bg-mint-100 text-mint-500': atom.status === 'completed',
            'bg-ink-100 text-ink-400': atom.status === 'locked',
          }"
        >
          <span v-if="atom.status === 'completed'" class="material-symbols-outlined text-2xl">check_circle</span>
          <span v-else-if="atom.status === 'locked'" class="material-symbols-outlined text-2xl">lock</span>
          <span v-else class="material-symbols-outlined text-2xl">{{ typeIcons[atom.type] || 'school' }}</span>
        </div>

        <!-- Info -->
        <div class="flex-1 min-w-0">
          <p class="font-bold text-on-surface truncate">{{ atom.title }}</p>
          <p class="text-xs text-on-surface-variant">{{ typeLabels[atom.type] || atom.type }}</p>
        </div>

        <!-- Step number -->
        <span class="text-xs text-on-surface-variant/50 font-mono">{{ i + 1 }}</span>
      </button>

      <!-- Empty state -->
      <div v-if="atoms.length === 0" class="text-center py-12 bg-surface-container rounded-2xl">
        <span class="material-symbols-outlined text-5xl text-ink-300 mb-3">inbox</span>
        <p class="text-on-surface-variant">لا توجد ذرات معرفية متاحة حالياً</p>
        <p class="text-xs text-on-surface-variant/60 mt-1">يرجى التواصل مع المعلم</p>
      </div>
    </div>

    <!-- Passport CTA -->
    <button
      v-if="canTakePassport"
      class="w-full bg-secondary text-on-secondary py-4 rounded-2xl font-bold text-lg
             hover:bg-secondary/90 active:scale-[0.98] transition-all shadow-lg flex items-center justify-center gap-2"
      @click="emit('passport')"
    >
      <span class="material-symbols-outlined">task_alt</span>
      اختبار الجواز
    </button>
  </div>
</template>
