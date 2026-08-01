<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PathwayOverview from '@/components/student/PathwayOverview.vue'
import type { PathwayAtom } from '@/components/student/PathwayOverview.vue'
import PassportAssessment from '@/components/student/PassportAssessment.vue'
import DifficultyMeter from '@/components/student/DifficultyMeter.vue'
import type { PassportEvaluation } from '@/services/remediationService'

const route = useRoute()
const router = useRouter()

const competencyId = computed(() => route.params.competencyId as string)
const difficulty = ref(5)
const previousDifficulty = ref(5)

// ── Mock pathway data ──
const mockAtoms: PathwayAtom[] = [
  { id: 'a1', title: 'مقدمة في الكسور', type: 'AUDIO_VISUAL', status: 'completed' },
  { id: 'a2', title: 'تمثيل الكسور بالرسوم', type: 'SIMULATION', status: 'completed' },
  { id: 'a3', title: 'مقارنة الكسور', type: 'MIND_MAP', status: 'available' },
  { id: 'a4', title: 'جمع وطرح الكسور', type: 'SIMULATION', status: 'locked' },
  { id: 'a5', title: 'ضرب الكسور', type: 'AUDIO_VISUAL', status: 'locked' },
]

type ViewState = 'overview' | 'atom' | 'passport' | 'results'
const currentView = ref<ViewState>('overview')
const selectedAtom = ref<PathwayAtom | null>(null)
const showEngagement = ref(false)
const passportEvaluation = ref<PassportEvaluation | null>(null)

const canTakePassport = computed(() =>
  mockAtoms.filter(a => a.status === 'completed').length >= 3
)

function selectAtom(atom: PathwayAtom) {
  selectedAtom.value = atom
  currentView.value = 'atom'

  // Simulate difficulty adjustment
  previousDifficulty.value = difficulty.value
  difficulty.value = Math.max(1, Math.min(10, difficulty.value + (atom.status === 'available' ? 1 : -1)))

  // Simulate engagement detection (30% chance)
  showEngagement.value = Math.random() < 0.3
}

function completeAtom() {
  if (selectedAtom.value) {
    const idx = mockAtoms.findIndex(a => a.id === selectedAtom.value!.id)
    if (idx >= 0) mockAtoms[idx].status = 'completed'
    // Unlock next atom
    const nextLocked = mockAtoms.find(a => a.status === 'locked')
    if (nextLocked) nextLocked.status = 'available'
  }
  currentView.value = 'overview'
  showEngagement.value = false
}

function startPassport() {
  currentView.value = 'passport'
}

function handlePassportCompleted(evaluation: PassportEvaluation) {
  passportEvaluation.value = evaluation
  currentView.value = 'results'
}

function goBack() {
  router.push('/student')
}
</script>

<template>
  <div
    dir="rtl"
    class="min-h-screen bg-background px-4 py-8"
  >
    <!-- Atom interaction view -->
    <div
      v-if="currentView === 'atom' && selectedAtom"
      class="max-w-lg mx-auto"
    >
      <button
        class="text-on-surface-variant hover:text-primary mb-6 flex items-center gap-1"
        @click="currentView = 'overview'"
      >
        <span class="material-symbols-outlined">arrow_back</span> العودة للمسار
      </button>

      <div class="bg-surface-container rounded-[2.5rem] p-8 shadow-lg">
        <span class="bg-primary/10 text-primary px-4 py-1 rounded-full text-sm font-bold inline-block mb-4">
          {{ selectedAtom.type === 'AUDIO_VISUAL' ? '🎬 سمعي بصري' : selectedAtom.type === 'SIMULATION' ? '🎮 محاكاة' : '🧠 خريطة ذهنية' }}
        </span>
        <h2 class="text-2xl font-black text-on-surface mb-4">
          {{ selectedAtom.title }}
        </h2>

        <!-- Difficulty meter -->
        <DifficultyMeter
          :current="difficulty"
          :previous="previousDifficulty"
          class="mb-6"
        />

        <!-- Engagement banner -->
        <div
          v-if="showEngagement"
          class="bg-amber-50 border border-amber-300 rounded-2xl p-4 mb-6 text-center"
        >
          <span class="text-2xl">💆</span>
          <p class="text-amber-700 font-medium mt-1">
            خذ نفساً عميقاً — أنت تبلي حسناً!
          </p>
          <p class="text-xs text-amber-500 mt-1">
            استرخ قليلاً ثم تابع
          </p>
        </div>

        <!-- Mock interaction area -->
        <div class="bg-surface-container-lowest rounded-2xl p-8 text-center mb-6 min-h-[200px] flex items-center justify-center">
          <p class="text-on-surface-variant">
            تفاعل مع المحتوى هنا...
          </p>
        </div>

        <button
          class="w-full bg-primary text-on-primary py-4 rounded-2xl font-bold text-lg
                 hover:bg-primary/90 active:scale-[0.98] transition-all"
          @click="completeAtom"
        >
          أكملت التمرين ✓
        </button>
      </div>
    </div>

    <!-- Passport assessment component -->
    <div v-else-if="currentView === 'passport'">
      <button
        class="text-on-surface-variant hover:text-primary mb-4 flex items-center gap-1 max-w-3xl mx-auto"
        @click="currentView = 'overview'"
      >
        <span class="material-symbols-outlined">arrow_back</span> العودة للمسار
      </button>
      <PassportAssessment
        :competency-id="competencyId"
        @completed="handlePassportCompleted"
        @close="currentView = 'overview'"
      />
    </div>

    <!-- Results -->
    <div
      v-else-if="currentView === 'results'"
      class="max-w-lg mx-auto text-center pt-12"
    >
      <div
        class="w-24 h-24 mx-auto mb-6 rounded-full flex items-center justify-center"
        :class="passportEvaluation?.passed ? 'bg-tertiary-container' : 'bg-surface-container-high'"
      >
        <span
          class="material-symbols-outlined text-6xl"
          :class="passportEvaluation?.passed ? 'text-tertiary' : 'text-on-surface-variant'"
        >
          {{ passportEvaluation?.passed ? 'workspace_premium' : 'psychology' }}
        </span>
      </div>
      <h2
        class="text-3xl font-black mb-3"
        :class="passportEvaluation?.passed ? 'text-primary' : 'text-on-surface'"
      >
        {{ passportEvaluation?.passed ? 'أحسنت! 🎉' : 'واصل المحاولة! 💪' }}
      </h2>
      <p class="text-on-surface-variant mb-2">
        {{ passportEvaluation?.message || (passportEvaluation?.passed ? 'لقد اجتزت اختبار الجواز بنجاح' : 'لم تتجاوز اختبار الجواز هذه المرة') }}
      </p>
      <p
        class="text-sm font-bold mb-8"
        :class="passportEvaluation?.passed ? 'text-tertiary' : 'text-secondary'"
      >
        المستوى الجديد: {{ passportEvaluation?.new_mastery_level || 'متقن' }}
      </p>
      <button
        class="bg-primary text-on-primary px-10 py-4 rounded-2xl font-bold text-lg
               hover:bg-primary/90 active:scale-95 transition-all"
        @click="goBack"
      >
        العودة للوحة التحكم
      </button>
    </div>

    <!-- Pathway Overview (default) -->
    <div v-else>
      <PathwayOverview
        :atoms="mockAtoms"
        :competency-name="`الكسور — ${competencyId}`"
        :can-take-passport="canTakePassport"
        @select="selectAtom"
        @passport="startPassport"
      />
    </div>
  </div>
</template>
