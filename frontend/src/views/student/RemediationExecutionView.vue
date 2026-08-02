<template>
  <div class="min-h-screen bg-surface p-6 font-sans dir-rtl">
    <div class="mx-auto max-w-4xl">
      <!-- Header & Progress Navigation -->
      <div class="mb-6 rounded-2xl bg-surface-bright p-6 shadow-sm border border-outline-variant">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-on-surface">
              مسار المعالجة: {{ competencyId }}
            </h1>
            <p class="text-sm text-on-surface-variant">
              التقدم في المسار المعرفي (من المحسوس إلى المجرد)
            </p>
          </div>
          <span
            class="rounded-full px-4 py-1.5 text-xs font-semibold"
            :class="statusBadgeClass"
          >
            {{ pathStatusText }}
          </span>
        </div>

        <!-- Progress Bar -->
        <div class="mt-6">
          <div class="flex items-center justify-between text-xs text-on-surface-variant mb-2">
            <span>نسبة الإنجاز</span>
            <span>{{ Math.round(progressPercent) }}%</span>
          </div>
          <div class="h-3 w-full overflow-hidden rounded-full bg-surface-container">
            <div
              class="h-full bg-primary transition-all duration-300"
              :style="{ width: `${progressPercent}%` }"
            />
          </div>
        </div>
      </div>

      <!-- Loading & Error States -->
      <div
        v-if="remediationStore.loading"
        class="text-center py-12"
      >
        <p class="text-on-surface-variant">
          جاري تحميل مسار المعالجة...
        </p>
      </div>

      <div
        v-else-if="remediationStore.error"
        class="rounded-xl bg-error-container p-4 text-error mb-6"
      >
        {{ remediationStore.error }}
      </div>

      <!-- Start Pathway Prompt (COMPLETED or IN_PROGRESS state) -->
      <div
        v-else-if="pathway && (pathway.status as string) === 'VALIDATED'"
        class="rounded-2xl bg-surface-bright p-8 text-center border border-outline-variant"
      >
        <h2 class="text-xl font-bold text-on-surface mb-2">
          تمت الموافقة على مسار المعالجة الخاص بك!
        </h2>
        <p class="text-on-surface-variant mb-6">
          انقر فوق زر البدء لبدء الكبسولات التعليمية المخصصة.
        </p>
        <button
          :disabled="remediationStore.actionLoading"
          class="rounded-xl bg-primary px-8 py-3 font-medium text-on-primary shadow-sm hover:opacity-90 transition-opacity"
          @click="startPathway"
        >
          {{ remediationStore.actionLoading ? 'جاري البدء...' : 'ابدأ مسار المعالجة الآن' }}
        </button>
      </div>

      <!-- Pathway Execution View (IN_PROGRESS) -->
      <div
        v-else-if="pathway && currentAtom"
        class="space-y-6"
      >
        <!-- Atom Navigation Tabs / Badges -->
        <div class="flex items-center gap-2 overflow-x-auto pb-2">
          <div
            v-for="(atom, idx) in pathway.atoms"
            :key="atom.id"
            class="flex items-center gap-2 rounded-xl px-4 py-2 border text-xs font-semibold"
            :class="[
              isAtomCompleted(atom.id)
                ? 'bg-tertiary-container text-tertiary border-tertiary'
                : idx === currentAtomIndex
                  ? 'bg-primary-container text-primary border-primary'
                  : 'bg-surface-container-low text-on-surface-variant border-outline-variant'
            ]"
          >
            <span>{{ idx + 1 }}. {{ getRemediationTypeName(atom.remediation_type) }}</span>
            <span v-if="isAtomCompleted(atom.id)">✓</span>
          </div>
        </div>

        <!-- Current Atom Interactive Card -->
        <div class="rounded-2xl bg-surface-bright p-8 border border-outline-variant shadow-sm">
          <div class="flex items-center justify-between mb-4">
            <span class="rounded-lg bg-primary-fixed-dim px-3 py-1 text-xs font-bold text-primary">
              {{ getRemediationTypeName(currentAtom.remediation_type) }}
            </span>
            <span class="text-xs text-on-surface-variant">
              الكبسولة {{ currentAtomIndex + 1 }} من {{ pathway.atoms.length }}
            </span>
          </div>

          <h2 class="text-xl font-bold text-on-surface mb-3">
            {{ currentAtom.content?.title || 'كبسولة تعليمية' }}
          </h2>
          <p class="text-on-surface-variant text-sm mb-6 leading-relaxed">
            {{ currentAtom.content?.description }}
          </p>

          <!-- Media / Audio Visual Content -->
          <div
            v-if="currentAtom.content?.media_url"
            class="mb-6 rounded-xl overflow-hidden bg-surface-container p-4"
          >
            <a
              :href="currentAtom.content.media_url"
              target="_blank"
              class="text-sm text-primary underline"
            >
              عرض المصدر / المقطع التفاعلي
            </a>
          </div>

          <!-- Atom Complete Button -->
          <div class="flex justify-end mt-8">
            <button
              :disabled="remediationStore.actionLoading"
              class="rounded-xl bg-primary px-6 py-2.5 text-sm font-medium text-on-primary hover:opacity-90 transition-opacity"
              @click="handleCompleteAtom"
            >
              {{ remediationStore.actionLoading ? 'جاري التسجيل...' : 'إكمال الكبسولة والانتقال للبعد التالي' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Completed State (COMPLETED) -->
      <div
        v-else-if="pathway && pathway.status === 'COMPLETED'"
        class="rounded-2xl bg-tertiary-container p-8 text-center border border-tertiary"
      >
        <h2 class="text-2xl font-bold text-tertiary mb-2">
          تهانينا! أكملت جميع كبسولات المعالجة
        </h2>
        <p class="text-on-surface-variant mb-6 text-sm">
          أصبحت جاهزاً الآن لإجراء اختبار الجواز (Passport Test) لتأكيد الإتقان.
        </p>
        <router-link
          :to="`/student/passport/${competencyId}`"
          class="inline-block rounded-xl bg-tertiary px-8 py-3 text-sm font-bold text-on-primary hover:opacity-90 transition-opacity"
        >
          خوض اختبار الجواز (Passport Test)
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useRemediationStore } from '@/stores/remediationStore'
import type { KnowledgeAtom } from '@/services/remediationService'

const route = useRoute()
const remediationStore = useRemediationStore()

const competencyId = computed(() => (route.params.competencyId as string) || '')

const pathway = computed(() => remediationStore.pathway)
const currentAtomIndex = computed(() => remediationStore.currentAtomIndex)
const currentAtom = computed<KnowledgeAtom | null>(() => remediationStore.currentAtom)
const progressPercent = computed(() => remediationStore.progressPercent)

const pathStatusText = computed(() => {
  if (!pathway.value) return ''
  switch (pathway.value.status as string) {
    case 'VALIDATED': return 'مؤكد من الخبير'
    case 'IN_PROGRESS': return 'قيد التنفيذ'
    case 'COMPLETED': return 'مكتمل'
    default: return pathway.value.status
  }
})

const statusBadgeClass = computed(() => {
  if (!pathway.value) return ''
  switch (pathway.value.status as string) {
    case 'VALIDATED': return 'bg-primary-fixed text-primary'
    case 'IN_PROGRESS': return 'bg-secondary-container text-secondary'
    case 'COMPLETED': return 'bg-tertiary-container text-tertiary'
    default: return 'bg-surface-container text-on-surface-variant'
  }
})

function isAtomCompleted(atomId: string): boolean {
  return remediationStore.isAtomCompleted(atomId)
}

function getRemediationTypeName(type: string): string {
  switch (type) {
    case 'AUDIO_VISUAL': return 'سمعي بصري (ملموس)'
    case 'SIMULATION': return 'محاكاة تفاعلية (تمثيلي)'
    case 'MIND_MAP': return 'خريطة ذهنية (مجرد)'
    default: return type
  }
}

async function loadPathway() {
  if (competencyId.value) {
    try {
      await remediationStore.fetchPathway(competencyId.value)
    } catch {
      // Handled in store.error
    }
  }
}

async function startPathway() {
  if (!pathway.value) return
  try {
    await remediationStore.startPathway(pathway.value.id)
    await loadPathway()
  } catch {
    // Handled in store.error
  }
}

async function handleCompleteAtom() {
  if (!currentAtom.value) return
  try {
    await remediationStore.completeAtom(currentAtom.value.id, {
      time_spent_ms: 15000,
      interactions_count: 1,
      is_correct: true,
    })
    await loadPathway()
  } catch {
    // Handled in store.error
  }
}

onMounted(() => {
  loadPathway()
})
</script>
