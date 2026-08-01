<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { remediationService, type ValidationQueueItem } from '@/services/remediationService'

const queueItems = ref<ValidationQueueItem[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const activeRejectId = ref<string | null>(null)
const rejectFeedback = ref('')
const submitting = ref(false)

async function fetchQueue() {
  loading.value = true
  error.value = null
  try {
    queueItems.value = await remediationService.getValidationQueue()
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'فشل في تحميل قائمة التقييم'
  } finally {
    loading.value = false
  }
}

async function handleValidate(id: string) {
  submitting.value = true
  try {
    await remediationService.validateProposal(id)
    queueItems.value = queueItems.value.filter((item) => item.id !== id)
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'فشل في الاعتماد')
  } finally {
    submitting.value = false
  }
}

function openRejectDialog(id: string) {
  activeRejectId.value = id
  rejectFeedback.value = ''
}

function cancelReject() {
  activeRejectId.value = null
  rejectFeedback.value = ''
}

async function handleReject(id: string) {
  if (!rejectFeedback.value.trim()) {
    alert('يرجى تقديم ملاحظات التوجيه أو الرفض')
    return
  }

  submitting.value = true
  try {
    await remediationService.rejectProposal(id, rejectFeedback.value)
    queueItems.value = queueItems.value.filter((item) => item.id !== id)
    activeRejectId.value = null
    rejectFeedback.value = ''
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'فشل في رفض المقترح')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchQueue()
})
</script>

<template>
  <div
    dir="rtl"
    class="min-h-screen bg-surface px-4 py-8"
  >
    <div class="max-w-4xl mx-auto">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-3xl font-black text-primary mb-2">
            قائمة مراجعة خطط المعالجة
          </h1>
          <p class="text-on-surface-variant">
            مراجعة واعتتماد مقترحات المعالجة البيداغوجية قبل إتاحتها للتلميذ
          </p>
        </div>
        <router-link
          to="/expert"
          class="px-4 py-2 bg-surface-container border border-outline-variant rounded-xl text-on-surface hover:bg-surface-container-high transition-colors text-sm font-medium"
        >
          العودة للوحة التحكّم
        </router-link>
      </div>

      <div
        v-if="loading"
        class="text-center py-12 text-on-surface-variant"
      >
        جاري تحميل خطط المعالجة المقترحة...
      </div>

      <div
        v-else-if="error"
        class="bg-error-container text-on-surface rounded-2xl p-6 mb-6"
      >
        <p class="font-bold text-error mb-2">
          حدث خطأ
        </p>
        <p class="text-sm">
          {{ error }}
        </p>
        <button
          class="mt-4 px-4 py-2 bg-primary text-on-primary rounded-xl text-sm font-medium"
          @click="fetchQueue"
        >
          إعادة المحاولة
        </button>
      </div>

      <div
        v-else-if="queueItems.length === 0"
        class="bg-surface-container-low rounded-2xl p-12 text-center border border-outline-variant"
      >
        <span class="material-symbols-outlined text-5xl text-primary mb-3">verified</span>
        <h2 class="text-xl font-bold text-on-surface mb-1">
          لا توجد مقترحات معلقة
        </h2>
        <p class="text-on-surface-variant text-sm">
          جميع خطط المعالجة البيداغوجية تمت مراجعتها واعتمادها.
        </p>
      </div>

      <div
        v-else
        class="space-y-6"
      >
        <div
          v-for="item in queueItems"
          :key="item.id"
          class="bg-surface-container-lowest border border-outline-variant rounded-2xl p-6 shadow-sm"
        >
          <div class="flex items-start justify-between mb-4">
            <div>
              <span class="inline-block px-3 py-1 bg-primary-container text-on-surface text-xs font-bold rounded-full mb-2">
                كفاءة: {{ item.competency_id }}
              </span>
              <h2 class="text-xl font-bold text-on-surface">
                التلميذ: {{ item.student_name }}
              </h2>
            </div>
            <span class="px-3 py-1 bg-secondary-container text-on-surface text-xs font-medium rounded-lg">
              حالة: {{ item.status }}
            </span>
          </div>

          <!-- AI Justification -->
          <div
            v-if="item.ai_pedagogical_justification"
            class="bg-surface-container-low rounded-xl p-4 mb-4 border-s-4 border-primary"
          >
            <p class="text-xs font-bold text-primary mb-1">
              التبرير البيداغوجي للذكاء الاصطناعي:
            </p>
            <p class="text-sm text-on-surface">
              {{ item.ai_pedagogical_justification }}
            </p>
          </div>

          <!-- Selected Atoms -->
          <div
            v-if="item.selected_atoms && item.selected_atoms.length > 0"
            class="mb-6"
          >
            <p class="text-xs font-bold text-on-surface-variant mb-2">
              الموارد المعرفية المختارة (العناصر):
            </p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div
                v-for="atom in item.selected_atoms"
                :key="atom.id"
                class="bg-surface-container p-3 rounded-lg border border-outline-variant text-xs"
              >
                <span class="font-bold text-primary block">{{ atom.remediation_type }}</span>
                <span class="text-on-surface block mt-1">{{ atom.content?.title || atom.id }}</span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-3 pt-4 border-t border-outline-variant">
            <button
              :disabled="submitting"
              class="px-5 py-2.5 bg-primary text-on-primary font-bold rounded-xl text-sm hover:opacity-95 transition-opacity disabled:opacity-50"
              @click="handleValidate(item.id)"
            >
              اعتماد المقترح (Validate)
            </button>

            <button
              v-if="activeRejectId !== item.id"
              :disabled="submitting"
              class="px-5 py-2.5 bg-error-container text-on-surface font-bold rounded-xl text-sm hover:bg-opacity-80 transition-colors disabled:opacity-50"
              @click="openRejectDialog(item.id)"
            >
              إعادة للتوجيه (Reject)
            </button>
          </div>

          <!-- Reject Dialog / Textarea -->
          <div
            v-if="activeRejectId === item.id"
            class="mt-4 p-4 bg-surface-container rounded-xl border border-outline"
          >
            <label class="block text-xs font-bold text-on-surface mb-2">
              سبب الإعادة وملاحظات التوجيه للذكاء الاصطناعي:
            </label>
            <textarea
              v-model="rejectFeedback"
              rows="3"
              class="w-full p-3 rounded-lg border border-outline-variant bg-surface text-on-surface text-sm focus:outline-none focus:border-primary mb-3"
              placeholder="اكتب ملاحظاتك البيداغوجية لإعادة التوليد (مثلاً: تركيز أكبر على المحسوس البصري)..."
            />
            <div class="flex items-center gap-2">
              <button
                :disabled="submitting || !rejectFeedback.trim()"
                class="px-4 py-2 bg-error text-on-primary rounded-lg text-xs font-bold disabled:opacity-50"
                @click="handleReject(item.id)"
              >
                تأكيد الإعادة
              </button>
              <button
                class="px-4 py-2 bg-surface border border-outline-variant rounded-lg text-xs text-on-surface font-medium"
                @click="cancelReject"
              >
                إلغاء
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>