<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { StudentRemediationCard } from '@/services/analyticsService'

const { locale, t } = useI18n()

defineProps<{
  cards: StudentRemediationCard[]
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const handlePrint = () => {
  window.print()
}
</script>

<template>
  <div
    class="printable-remediation-wrapper bg-surface text-on-surface font-['Tajawal'] min-h-screen p-6"
    dir="rtl"
  >
    <!-- Header Controls (Hidden during print) -->
    <div class="no-print flex items-center justify-between mb-8 pb-4 border-b border-outline-variant">
      <div>
        <h2 class="text-2xl font-bold text-primary font-['Cairo']">
          {{ t('remediation.printableCardsTitle', 'بطاقات المعالجة التربوية المطبوعة') }}
        </h2>
        <p class="text-sm text-on-surface-variant mt-1">
          {{ t('remediation.printableCardsSubtitle', 'بطاقات فردية مخصصة لكل تلميذ تحتوي على الكفاءات المستهدفة وخطة التدخل البيداغوجي.') }}
        </p>
      </div>
      <div class="flex items-center gap-3">
        <button
          type="button"
          class="flex items-center gap-2 px-5 py-2.5 bg-primary hover:bg-[#003f45] text-on-primary font-bold text-sm rounded-xl shadow-sm transition-all"
          @click="handlePrint"
        >
          <span class="material-symbols-outlined text-lg">print</span>
          <span>{{ t('common.print', 'طباعة البطاقات') }}</span>
        </button>
        <button
          type="button"
          class="flex items-center gap-2 px-4 py-2.5 bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-bold text-sm rounded-xl border border-outline-variant transition-all"
          @click="emit('close')"
        >
          <span>{{ t('common.close', 'إغلاق') }}</span>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div
      v-if="loading"
      class="no-print flex flex-col items-center justify-center py-16"
    >
      <div class="animate-spin w-10 h-10 border-4 border-primary border-t-transparent rounded-full mb-3" />
      <span class="text-sm font-semibold text-on-surface-variant">{{ t('common.loading', 'جاري تحميل بطاقات المعالجة...') }}</span>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="!cards || cards.length === 0"
      class="no-print text-center py-16 bg-surface-container-lowest rounded-2xl border border-outline-variant/30"
    >
      <span class="material-symbols-outlined text-4xl text-on-surface-variant mb-2">assignment_turned_in</span>
      <p class="text-lg font-bold text-on-surface">
        {{ t('remediation.noCardsTitle', 'لا توجد بطاقات معالجة مطلوبة حالياً') }}
      </p>
      <p class="text-sm text-on-surface-variant mt-1">
        {{ t('remediation.noCardsSubtitle', 'جميع التلاميذ في هذه المجموعة أظهروا تمكناً من الكفاءات المقيّمة.') }}
      </p>
    </div>

    <!-- Printable Cards Layout -->
    <div
      v-else
      class="cards-container space-y-8"
    >
      <div
        v-for="card in cards"
        :key="card.student_id"
        class="remediation-card bg-surface-bright rounded-2xl p-6 border-2 border-outline-variant shadow-sm break-after-page page-break-after"
      >
        <!-- Card Header -->
        <div class="flex items-center justify-between pb-4 border-b-2 border-primary/20 mb-5">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-primary-container text-on-primary-container flex items-center justify-center font-bold text-lg">
              {{ card.student_name.charAt(0).toUpperCase() }}
            </div>
            <div>
              <h3 class="text-xl font-bold text-primary font-['Cairo']">
                {{ card.student_name }}
              </h3>
              <p class="text-xs text-on-surface-variant">
                {{ t('remediation.level', 'المستوى الدراسي') }}: {{ card.grade_level }}
              </p>
            </div>
          </div>
          <div class="text-end">
            <span class="px-3 py-1 bg-secondary-container text-on-secondary-container rounded-full text-xs font-bold font-['Inter']">
              {{ t('remediation.cardType', 'بطاقة معالجة فردية') }}
            </span>
            <p class="text-[10px] text-on-surface-variant mt-1">
              {{ new Date(card.generated_at).toLocaleDateString(locale === 'fr' ? 'fr-FR' : 'ar-DZ') }}
            </p>
          </div>
        </div>

        <!-- Section 1: Target Failed Competencies -->
        <div class="mb-5">
          <h4 class="text-sm font-bold text-primary mb-2 flex items-center gap-2">
            <span class="material-symbols-outlined text-base">warning</span>
            <span>{{ t('remediation.targetCompetencies', 'الكفاءات غير المكتسبة (محل المعالجة)') }}</span>
          </h4>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="comp in card.failed_competencies"
              :key="comp"
              class="px-3 py-1.5 bg-error-container text-on-error-container rounded-lg text-xs font-bold border border-error/20"
            >
              {{ comp }}
            </span>
          </div>
        </div>

        <!-- Section 2: Error Classifications -->
        <div class="mb-5">
          <h4 class="text-sm font-bold text-secondary mb-2 flex items-center gap-2">
            <span class="material-symbols-outlined text-base">psychology</span>
            <span>{{ t('remediation.errorTypes', 'تصنيف التعثر والأخطاء') }}</span>
          </h4>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="errType in card.error_classifications"
              :key="errType"
              class="px-3 py-1.5 bg-secondary-container text-on-secondary-container rounded-lg text-xs font-semibold"
            >
              {{ errType }}
            </span>
          </div>
        </div>

        <!-- Section 3: Recommended Remediation Atoms -->
        <div class="mb-4">
          <h4 class="text-sm font-bold text-tertiary mb-2 flex items-center gap-2">
            <span class="material-symbols-outlined text-base">menu_book</span>
            <span>{{ t('remediation.recommendedAtoms', 'الكبسولات والأنشطة العلاجية الموصى بها') }}</span>
          </h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div
              v-for="atom in card.recommended_atoms"
              :key="atom.id || atom.title"
              class="p-3 bg-tertiary-container/30 border border-tertiary-container rounded-xl"
            >
              <h5 class="text-xs font-bold text-tertiary">
                {{ atom.title }}
              </h5>
              <p class="text-xs text-on-surface-variant mt-1">
                {{ atom.description }}
              </p>
            </div>
          </div>
        </div>

        <!-- Card Footer Note -->
        <div class="pt-4 border-t border-outline-variant/40 flex items-center justify-between text-[11px] text-on-surface-variant">
          <span>منصة إحسان البيداغوجية - مسار المعالجة الفردية</span>
          <span>توقيع الأستاذ / الخبير البيداغوجي: ........................</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@media print {
  /* Hide UI Navigation & Controls */
  .no-print,
  aside,
  header,
  nav,
  button {
    display: none !important;
  }

  /* Page setup for clean printable output */
  body,
  .printable-remediation-wrapper {
    background: transparent !important;
    color: inherit !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  .remediation-card {
    border: 2px solid currentcolor !important;
    box-shadow: none !important;
    background: transparent !important;
    break-after: page !important;
    margin-bottom: 2rem !important;
  }
}
</style>
