<script setup lang="ts">
const props = defineProps<{
  masteryLevel: string
  masteryProbability: number
  recommendedGroup: string
  totalQuestions: number
  correctAnswers: number
  errors: { classification: string; count: number }[]
}>()

const masteryLabels: Record<string, string> = {
  NOT_STARTED: 'لم يبدأ',
  ATTEMPTED: 'بدأ التعلم',
  FAMILIAR: 'متوسط',
  PROFICIENT: 'متقن',
  MASTERED: 'متمكن',
}

const groupLabels: Record<string, { label: string; color: string; desc: string }> = {
  A: { label: 'المجموعة أ — إتقان', color: 'bg-[#2e5a3b]', desc: 'أنت متقن! استمر في أنشطة الإثراء' },
  B: { label: 'المجموعة ب — إتقان جزئي', color: 'bg-[#8c4e35]', desc: 'تحتاج لتقوية في بعض النقاط' },
  C: { label: 'المجموعة ج — يحتاج دعماً', color: 'bg-[#b33a3a]', desc: 'سنبني معاً من البداية' },
}

const errorLabels: Record<string, string> = {
  RESOURCE: 'نقص في المكتسبات',
  PROCESS: 'خطأ في المنهجية',
  INCIDENTAL: 'سهو / تركيز',
  NONE: 'إجابة صحيحة',
}

const accuracy = props.totalQuestions > 0
  ? Math.round((props.correctAnswers / props.totalQuestions) * 100)
  : 0
</script>

<template>
  <div class="max-w-lg mx-auto">
    <!-- Group banner -->
    <div
      :class="`${groupLabels[recommendedGroup]?.color || 'bg-primary'} text-on-primary rounded-[2rem] p-8 text-center mb-6 shadow-lg`"
    >
      <span class="material-symbols-outlined text-5xl mb-3 block">
        {{ recommendedGroup === 'A' ? 'workspace_premium' : recommendedGroup === 'B' ? 'lightbulb' : 'favorite' }}
      </span>
      <h2 class="text-2xl font-black mb-2">{{ groupLabels[recommendedGroup]?.label || recommendedGroup }}</h2>
      <p class="text-on-primary/80">{{ groupLabels[recommendedGroup]?.desc || '' }}</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 gap-4 mb-6">
      <div class="bg-surface-container rounded-2xl p-5 text-center">
        <p class="text-3xl font-black text-primary">{{ accuracy }}%</p>
        <p class="text-sm text-on-surface-variant mt-1">نسبة النجاح</p>
      </div>
      <div class="bg-surface-container rounded-2xl p-5 text-center">
        <p class="text-3xl font-black text-primary">{{ correctAnswers }}/{{ totalQuestions }}</p>
        <p class="text-sm text-on-surface-variant mt-1">الإجابات الصحيحة</p>
      </div>
    </div>

    <!-- Mastery -->
    <div class="bg-surface-container rounded-2xl p-5 mb-6">
      <div class="flex justify-between items-center mb-3">
        <span class="font-bold text-on-surface">مستوى الإتقان</span>
        <span class="text-primary font-black">{{ masteryLabels[masteryLevel] || masteryLevel }}</span>
      </div>
      <div class="w-full h-3 bg-surface-container-highest rounded-full overflow-hidden">
        <div
          class="h-full bg-primary rounded-full transition-all duration-700"
          :style="{ width: (masteryProbability * 100) + '%' }"
        />
      </div>
      <p class="text-xs text-on-surface-variant mt-2 text-end">{{ Math.round(masteryProbability * 100) }}%</p>
    </div>

    <!-- Error breakdown -->
    <div v-if="errors.length > 0" class="bg-surface-container rounded-2xl p-5">
      <h3 class="font-bold text-on-surface mb-3">تحليل الأخطاء</h3>
      <div v-for="e in errors" :key="e.classification" class="flex justify-between items-center py-2 border-b border-outline-variant/30 last:border-0">
        <span class="text-sm text-on-surface-variant">{{ errorLabels[e.classification] || e.classification }}</span>
        <span class="font-bold text-on-surface">{{ e.count }}</span>
      </div>
    </div>
  </div>
</template>
