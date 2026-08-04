<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-on-surface/40 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="pin-modal-title"
      tabindex="-1"
      @keydown.escape="handleClose"
    >
      <div
        class="w-full max-w-lg rounded-2xl bg-surface-bright p-6 shadow-xl border border-outline-variant text-start transition-all"
      >
        <!-- Header -->
        <div class="flex items-center justify-between pb-4 border-b border-outline-variant">
          <div>
            <h2
              id="pin-modal-title"
              class="text-xl font-bold text-on-surface"
            >
              {{ t('parent.pinModalTitle') }}
            </h2>
            <p class="text-sm text-on-surface-variant mt-1">
              {{ t('parent.pinModalSub') }}
            </p>
          </div>
          <button
            type="button"
            class="rounded-full p-2 text-on-surface-variant hover:bg-surface-container-high transition-colors"
            :aria-label="t('parent.close')"
            @click="handleClose"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <!-- Notification / Message -->
        <div
          v-if="successMessage"
          class="mt-4 p-3 rounded-lg bg-tertiary-container text-tertiary text-sm font-medium flex items-center justify-between"
        >
          <span>{{ successMessage }}</span>
          <button
            class="me-2 font-bold"
            @click="successMessage = ''"
          >
            &times;
          </button>
        </div>

        <div
          v-if="errorMessage"
          class="mt-4 p-3 rounded-lg bg-error-container text-error text-sm font-medium flex items-center justify-between"
        >
          <span>{{ errorMessage }}</span>
          <button
            class="me-2 font-bold"
            @click="errorMessage = ''"
          >
            &times;
          </button>
        </div>

        <!-- Children PIN List -->
        <div class="mt-5 space-y-4 max-h-[60vh] overflow-y-auto pe-1">
          <div
            v-for="child in childrenList"
            :key="getChildId(child)"
            class="p-4 rounded-xl bg-surface-container-low border border-outline-variant space-y-3"
          >
            <div class="flex items-center justify-between">
              <div>
                <h3 class="font-semibold text-on-surface text-base">
                  {{ child.name }}
                </h3>
                <span
                  v-if="getChildGrade(child)"
                  class="text-xs text-on-surface-variant"
                >
                  {{ getChildGrade(child) }}
                </span>
              </div>

              <!-- Masked / Revealed PIN display -->
              <div class="flex items-center gap-2">
                <span class="font-mono text-lg font-bold tracking-wider px-3 py-1 bg-surface-bright rounded-md border border-outline-variant text-on-surface">
                  {{ isRevealed(getChildId(child)) ? (revealedPins[getChildId(child)] || '••••') : '••••' }}
                </span>

                <button
                  type="button"
                  class="px-3 py-1 text-xs font-medium rounded-lg border border-outline-variant bg-surface-bright hover:bg-surface-container text-on-surface-variant transition-colors"
                  @click="toggleReveal(getChildId(child))"
                >
                  {{ isRevealed(getChildId(child)) ? t('parent.hidePin') : t('parent.revealPin') }}
                </button>
              </div>
            </div>

            <!-- Toggle PIN Reset Form -->
            <div class="pt-2 border-t border-outline-variant/60 flex items-center justify-between gap-2">
              <button
                v-if="activeResetChildId !== getChildId(child)"
                type="button"
                class="text-xs font-medium text-primary hover:underline"
                @click="startReset(getChildId(child))"
              >
                {{ t('parent.resetPin') }}
              </button>

              <form
                v-else
                class="w-full flex items-center gap-2 mt-1"
                @submit.prevent="submitPinReset(getChildId(child))"
              >
                <input
                  v-model="newPinInput"
                  type="password"
                  inputmode="numeric"
                  pattern="[0-9]{4,6}"
                  maxlength="6"
                  required
                  :placeholder="t('parent.newPinPlaceholder')"
                  class="flex-1 px-3 py-1.5 text-xs rounded-lg border border-outline bg-surface-bright text-on-surface focus:outline-none focus:ring-2 focus:ring-primary"
                >

                <button
                  type="submit"
                  :disabled="isSubmitting"
                  class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-primary text-on-primary hover:bg-primary/90 disabled:opacity-50 transition-colors"
                >
                  {{ t('parent.savePin') }}
                </button>

                <button
                  type="button"
                  class="px-2 py-1.5 text-xs text-on-surface-variant hover:bg-surface-container rounded-lg"
                  @click="cancelReset"
                >
                  &times;
                </button>
              </form>
            </div>
          </div>

          <div
            v-if="!childrenList || childrenList.length === 0"
            class="text-center py-6 text-on-surface-variant text-sm"
          >
            {{ t('parent.noChildren') }}
          </div>
        </div>

        <!-- Footer -->
        <div class="mt-6 pt-4 border-t border-outline-variant flex justify-end">
          <button
            type="button"
            class="px-4 py-2 text-sm font-medium rounded-xl border border-outline-variant bg-surface-bright text-on-surface hover:bg-surface-container transition-colors"
            @click="handleClose"
          >
            {{ t('parent.close') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { dashboardService, type ChildSummary, type ChildDashboardData } from '@/services/dashboardService'

defineProps<{
  isOpen: boolean
  childrenList: (ChildSummary | ChildDashboardData)[]
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'updated'): void
}>()

const { t } = useI18n()

const revealedPins = ref<Record<string, string>>({})
const revealTimers = ref<Record<string, number>>({})
const activeResetChildId = ref<string | null>(null)
const newPinInput = ref('')
const isSubmitting = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

function getChildId(child: ChildSummary | ChildDashboardData): string {
  const id = (child as any).childId || (child as any).child_id || (child as any).id || ''
  return id
}

function getChildGrade(child: ChildSummary | ChildDashboardData): string {
  return (child as any).gradeLevel || (child as any).grade_level || ''
}

function isRevealed(childId: string): boolean {
  return Boolean(revealedPins.value[childId])
}

function toggleReveal(childId: string) {
  if (!childId) return
  if (isRevealed(childId)) {
    hidePin(childId)
  } else {
    // If not recently updated in session, pin remains masked / unretrievable
    if (!revealedPins.value[childId]) {
      revealedPins.value[childId] = '••••'
    }
    if (revealTimers.value[childId]) {
      clearTimeout(revealTimers.value[childId])
    }
    revealTimers.value[childId] = window.setTimeout(() => {
      hidePin(childId)
    }, 5000)
  }
}

function hidePin(childId: string) {
  delete revealedPins.value[childId]
  if (revealTimers.value[childId]) {
    clearTimeout(revealTimers.value[childId])
    delete revealTimers.value[childId]
  }
}

function startReset(childId: string) {
  activeResetChildId.value = childId
  newPinInput.value = ''
  errorMessage.value = ''
  successMessage.value = ''
}

function cancelReset() {
  activeResetChildId.value = null
  newPinInput.value = ''
}

async function submitPinReset(childId: string) {
  if (!childId) return
  if (!newPinInput.value || !/^\d{4,6}$/.test(newPinInput.value)) {
    errorMessage.value = t('auth.pinCodeLabel')
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await dashboardService.updateChildPin(childId, newPinInput.value)
    revealedPins.value[childId] = newPinInput.value
    if (revealTimers.value[childId]) clearTimeout(revealTimers.value[childId])
    revealTimers.value[childId] = window.setTimeout(() => {
      hidePin(childId)
    }, 5000)

    successMessage.value = t('parent.pinUpdatedSuccess')
    cancelReset()
    emit('updated')
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    errorMessage.value = Array.isArray(detail) ? detail[0]?.msg : (detail || 'Failed to update PIN')
  } finally {
    isSubmitting.value = false
  }
}

function handleClose() {
  cancelReset()
  successMessage.value = ''
  errorMessage.value = ''
  Object.keys(revealTimers.value).forEach(id => hidePin(id))
  emit('close')
}

onUnmounted(() => {
  Object.keys(revealTimers.value).forEach(id => clearTimeout(revealTimers.value[id]))
  revealTimers.value = {}
  revealedPins.value = {}
})
</script>
