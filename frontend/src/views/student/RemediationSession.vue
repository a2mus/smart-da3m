<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRemediationStore } from '@/stores/remediationStore'
import { useOfflineSync } from '@/composables/useOfflineSync'
import PathwayOverview from '@/components/student/PathwayOverview.vue'
import type { PathwayAtom } from '@/components/student/PathwayOverview.vue'
import PassportAssessment from '@/components/student/PassportAssessment.vue'
import DifficultyMeter from '@/components/student/DifficultyMeter.vue'
import type { PassportEvaluation } from '@/services/remediationService'

const route = useRoute()
const router = useRouter()
const remediationStore = useRemediationStore()
const { isOnline, isSyncing, queueCompletion } = useOfflineSync()

const competencyId = computed(() => (route.params.competencyId as string) || '')
const difficulty = ref(5)
const previousDifficulty = ref(5)

type ViewState = 'overview' | 'atom' | 'passport' | 'results'
const currentView = ref<ViewState>('overview')
const selectedAtomId = ref<string | null>(null)
const showEngagement = ref(false)

const pathwayAtoms = computed<PathwayAtom[]>(() => {
  if (!remediationStore.pathway || !remediationStore.pathway.atoms) return []
  const completedIds = remediationStore.atomsCompleted
  const atoms = remediationStore.pathway.atoms

  let firstUncompletedFound = false
  return atoms.map((atom) => {
    const isCompleted = completedIds.includes(atom.id)
    let status: 'completed' | 'available' | 'locked' = 'locked'

    if (isCompleted) {
      status = 'completed'
    } else if (!firstUncompletedFound) {
      status = 'available'
      firstUncompletedFound = true
    }

    return {
      id: atom.id,
      title: atom.content?.title || 'كبسولة تعليمية',
      type: atom.remediation_type,
      status,
    }
  })
})

const selectedAtomObj = computed(() => {
  if (!selectedAtomId.value || !remediationStore.pathway) return null
  return remediationStore.pathway.atoms.find((a) => a.id === selectedAtomId.value) || null
})

function selectAtom(atom: PathwayAtom) {
  selectedAtomId.value = atom.id
  currentView.value = 'atom'

  previousDifficulty.value = difficulty.value
  difficulty.value = Math.max(1, Math.min(10, difficulty.value + (atom.status === 'available' ? 1 : -1)))
  showEngagement.value = Math.random() < 0.3
}

async function handleCompleteAtom() {
  if (selectedAtomId.value) {
    try {
      await remediationStore.completeAtom(selectedAtomId.value, {
        time_spent_ms: 15000,
        interactions_count: 1,
        is_correct: true,
      })
      if (remediationStore.pathway?.id) {
        await queueCompletion(remediationStore.pathway.id)
      }
    } catch {
      if (remediationStore.pathway?.id) {
        await queueCompletion(remediationStore.pathway.id)
      }
    }
  }
  currentView.value = 'overview'
  showEngagement.value = false
}

function startPassport() {
  currentView.value = 'passport'
}

function handlePassportCompleted(evaluation: PassportEvaluation) {
  currentView.value = 'results'
}

function goBack() {
  router.push('/student')
}

onMounted(async () => {
  if (competencyId.value) {
    try {
      await remediationStore.fetchPathway(competencyId.value)
    } catch {
      // Error managed in store.error
    }
  }
})
</script>

<template>
  <div
    dir="rtl"
    class="min-h-screen bg-background px-4 py-8"
  >
    <!-- Offline / Syncing Banner -->
    <div
      v-if="!isOnline || isSyncing"
      data-testid="offline-banner"
      class="max-w-lg mx-auto bg-secondary-container text-on-surface-variant border border-outline-variant px-4 py-2 rounded-xl mb-4 flex items-center justify-between text-sm"
    >
      <div class="flex items-center gap-2">
        <span class="material-symbols-outlined text-secondary">{{ isOnline ? 'sync' : 'wifi_off' }}</span>
        <span>{{ isOnline ? 'جاري المزامنة...' : 'أنت تفاعلي حالياً دون اتصال — سيتم حفظ نتائجك ومزامنتها لاحقاً' }}</span>
      </div>
      <span
        v-if="isSyncing"
        class="animate-spin material-symbols-outlined text-primary"
      >progress_activity</span>
    </div>
    <!-- Loading State -->
    <div
      v-if="remediationStore.loading"
      class="text-center py-12"
    >
      <div class="animate-spin inline-block w-10 h-10 border-4 border-primary border-t-transparent rounded-full" />
      <p class="mt-3 text-on-surface-variant">
        جاري تحميل مسار المعالجة...
      </p>
    </div>

    <!-- Error State -->
    <div
      v-else-if="remediationStore.error"
      class="max-w-lg mx-auto bg-error-container border border-error text-error px-4 py-3 rounded-xl mb-4 text-center"
    >
      {{ remediationStore.error }}
    </div>

    <!-- Atom interaction view -->
    <div
      v-else-if="currentView === 'atom' && selectedAtomObj"
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
          {{ selectedAtomObj.remediation_type === 'AUDIO_VISUAL' ? '🎬 سمعي بصري' : selectedAtomObj.remediation_type === 'SIMULATION' ? '🎮 محاكاة' : '🧠 خريطة ذهنية' }}
        </span>
        <h2 class="text-2xl font-black text-on-surface mb-4">
          {{ selectedAtomObj.content?.title || 'كبسولة تعليمية' }}
        </h2>
        <p class="text-on-surface-variant text-sm mb-6 leading-relaxed">
          {{ selectedAtomObj.content?.description }}
        </p>

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

        <!-- Media / Audio Visual Content -->
        <div
          v-if="selectedAtomObj.content?.media_url"
          class="mb-6 rounded-xl overflow-hidden bg-surface-container-lowest p-4 text-center"
        >
          <a
            :href="selectedAtomObj.content.media_url"
            target="_blank"
            class="text-sm text-primary underline"
          >
            عرض المصدر / المقطع التفاعلي
          </a>
        </div>

        <button
          :disabled="remediationStore.actionLoading"
          class="w-full bg-primary text-on-primary py-4 rounded-2xl font-bold text-lg
                 hover:bg-primary/90 active:scale-[0.98] transition-all disabled:opacity-50"
          @click="handleCompleteAtom"
        >
          {{ remediationStore.actionLoading ? 'جاري التسجيل...' : 'أكملت التمرين ✓' }}
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
        :class="remediationStore.passportEvaluation?.passed ? 'bg-tertiary-container' : 'bg-surface-container-high'"
      >
        <span
          class="material-symbols-outlined text-6xl"
          :class="remediationStore.passportEvaluation?.passed ? 'text-tertiary' : 'text-on-surface-variant'"
        >
          {{ remediationStore.passportEvaluation?.passed ? 'workspace_premium' : 'psychology' }}
        </span>
      </div>
      <h2
        class="text-3xl font-black mb-3"
        :class="remediationStore.passportEvaluation?.passed ? 'text-primary' : 'text-on-surface'"
      >
        {{ remediationStore.passportEvaluation?.passed ? 'أحسنت! 🎉' : 'واصل المحاولة! 💪' }}
      </h2>
      <p class="text-on-surface-variant mb-2">
        {{ remediationStore.passportEvaluation?.message || (remediationStore.passportEvaluation?.passed ? 'لقد اجتزت اختبار الجواز بنجاح' : 'لم تتجاوز اختبار الجواز هذه المرة') }}
      </p>
      <p
        class="text-sm font-bold mb-8"
        :class="remediationStore.passportEvaluation?.passed ? 'text-tertiary' : 'text-secondary'"
      >
        المستوى الجديد: {{ remediationStore.passportEvaluation?.new_mastery_level || 'متقن' }}
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
        :atoms="pathwayAtoms"
        :competency-name="`مسار المعالجة — ${competencyId}`"
        :can-take-passport="remediationStore.canTakePassport"
        @select="selectAtom"
        @passport="startPassport"
      />
    </div>
  </div>
</template>
