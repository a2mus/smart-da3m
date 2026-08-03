<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useAnalyticsStore } from '@/stores/analyticsStore'

const { t } = useI18n()
const analyticsStore = useAnalyticsStore()

const handlePrint = () => {
  window.print()
}

const handleClose = () => {
  analyticsStore.showPrintCardsModal = false
}
</script>

<template>
  <div
    v-if="analyticsStore.showPrintCardsModal"
    class="fixed inset-0 z-50 overflow-y-auto bg-black/50 p-4 print:p-0 print:static print:bg-white print:overflow-visible"
  >
    <!-- Screen-only toolbar -->
    <div class="mx-auto max-w-4xl mb-4 flex items-center justify-between bg-surface-bright p-4 rounded-xl shadow-lg border border-outline-variant print:hidden">
      <div>
        <h3 class="text-base font-bold text-on-surface">
          {{ t('analytics.remediationCardsPrint', 'بطاقات المعالجة التربوية (جاهزة للطباعة)') }}
        </h3>
        <p class="text-xs text-on-surface-variant">
          {{ t('analytics.remediationCardsSubtitle', 'بطاقة مخصصة لكل تلميذ تحتوي على الكفاءات والأخطاء والأنشطة المقترحة') }}
        </p>
      </div>
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="px-4 py-2 text-xs font-bold text-on-primary bg-primary rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-1.5 shadow-sm"
          @click="handlePrint"
        >
          <span class="i-lucide-printer w-4 h-4" />
          {{ t('analytics.printNow', 'طباعة الآن') }}
        </button>
        <button
          type="button"
          class="px-3 py-2 text-xs font-semibold text-on-surface-variant bg-surface-container hover:bg-surface-container-high rounded-lg transition-colors"
          @click="handleClose"
        >
          {{ t('common.close', 'إغلاق') }}
        </button>
      </div>
    </div>

    <!-- Cards container -->
    <div class="mx-auto max-w-4xl space-y-6 print:space-y-0 print:max-w-none">
      <div
        v-for="card in analyticsStore.remediationCards"
        :key="card.student_id"
        class="remediation-card bg-surface-bright p-6 rounded-2xl border-2 border-outline-variant shadow-sm print:shadow-none print:border-black print:rounded-none print:p-4 print:my-0 page-break-after"
      >
        <!-- Header -->
        <div class="flex items-center justify-between border-b-2 border-primary/20 pb-4 mb-4 print:border-black">
          <div>
            <h2 class="text-lg font-black text-primary print:text-black">
              {{ t('analytics.remediationCardHeader', 'بطاقة معالجة فردية') }}
            </h2>
            <div class="flex items-center gap-3 mt-1 text-xs text-on-surface-variant print:text-black">
              <span class="font-bold text-on-surface print:text-black">{{ t('analytics.studentName', 'التلميذ') }}: {{ card.student_name }}</span>
              <span>•</span>
              <span>{{ t('analytics.gradeLevel', 'المستوى') }}: {{ card.grade_level }}</span>
              <span v-if="card.group_name">•</span>
              <span v-if="card.group_name">{{ t('analytics.group', 'المجموعة') }}: {{ card.group_name }}</span>
            </div>
          </div>
          <div class="text-end text-xs text-on-surface-variant print:text-black">
            <div class="font-bold">
              {{ t('app.title', 'منصة إحسان التربوية') }}
            </div>
            <div class="text-[10px]">
              {{ new Date().toLocaleDateString('ar-DZ') }}
            </div>
          </div>
        </div>

        <!-- Competency Items -->
        <div
          v-if="card.items && card.items.length > 0"
          class="space-y-4"
        >
          <div
            v-for="item in card.items"
            :key="item.competency_id"
            class="bg-surface-container-lowest p-4 rounded-xl border border-outline-variant print:border-black print:bg-white"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-bold text-on-surface print:text-black">
                {{ item.competency_name || item.competency_id }}
              </span>
              <span class="px-2.5 py-1 text-xs font-bold rounded-full bg-error-container text-error print:border print:border-black print:text-black print:bg-white">
                {{ item.mastery_level }}
              </span>
            </div>

            <!-- Error classifications -->
            <div
              v-if="item.error_classifications && item.error_classifications.length > 0"
              class="mt-2 text-xs"
            >
              <span class="font-semibold text-secondary print:text-black">{{ t('analytics.errorClassification', 'تشخيص نوع الخطأ') }}: </span>
              <span class="text-on-surface-variant print:text-black">{{ item.error_classifications.join(', ') }}</span>
            </div>

            <!-- Recommended atoms -->
            <div
              v-if="item.recommended_atoms && item.recommended_atoms.length > 0"
              class="mt-2 text-xs"
            >
              <span class="font-semibold text-tertiary print:text-black">{{ t('analytics.recommendedAtoms', 'كبسولات الدعم المعرفي المقترحة') }}: </span>
              <ul class="list-disc list-inside mt-1 space-y-0.5 text-on-surface print:text-black">
                <li
                  v-for="atom in item.recommended_atoms"
                  :key="atom"
                >
                  {{ atom }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-else
          class="text-center py-8 text-xs text-on-surface-variant"
        >
          {{ t('analytics.noGapsIdentified', 'لا توجد ثغرات معرفية مسجلة لهذا التلميذ') }}
        </div>

        <!-- Teacher Notes / Signature footer for print -->
        <div class="mt-6 border-t border-dashed border-outline-variant pt-4 text-xs text-on-surface-variant print:border-black">
          <div class="flex justify-between items-end">
            <div>
              <span class="font-bold text-on-surface print:text-black">{{ t('analytics.expertNotes', 'ملاحظات وتوجيهات الأستاذ') }}: </span>
              <div class="h-12 border-b border-dotted border-outline-variant mt-1 w-64 print:border-black" />
            </div>
            <div class="text-center">
              <div class="font-bold text-on-surface print:text-black mb-6">
                {{ t('analytics.expertSignature', 'توقيع الخبير البيداغوجي') }}
              </div>
              <div class="text-[10px]">
                ____________________
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@media print {
  body * {
    visibility: hidden;
  }
  .remediation-card,
  .remediation-card * {
    visibility: visible;
  }
  .page-break-after {
    break-after: always;
    break-after: page;
  }
}
</style>