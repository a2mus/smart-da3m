<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import DiagnosticQuestion from '@/components/student/DiagnosticQuestion.vue'
import DiagnosticProgress from '@/components/student/DiagnosticProgress.vue'
import DiagnosticResults from '@/components/student/DiagnosticResults.vue'
import type { QuestionData } from '@/components/student/DiagnosticQuestion.vue'

const router = useRouter()

// ── State ──
type Phase = 'intro' | 'testing' | 'results'
const phase = ref<Phase>('intro')
const questionIndex = ref(0)
const correctCount = ref(0)
const errors = ref<Record<string, number>>({ RESOURCE: 0, PROCESS: 0, INCIDENTAL: 0, NONE: 0 })

const totalQuestions = 10

// ── Mock questions ──
const mockQuestions: QuestionData[] = [
  { id: 'q1', text: 'ما هو ناتج ١/٢ + ١/٤ ؟', difficulty_level: 3, type: 'multiple_choice', options: ['٢/٦', '٣/٤', '١/٤', '٢/٤'] },
  { id: 'q2', text: 'أي الكسرين أكبر: ١/٣ أم ١/٥ ؟', difficulty_level: 4, type: 'multiple_choice', options: ['١/٣', '١/٥', 'متساويان', 'لا يمكن المقارنة'] },
  { id: 'q3', text: 'ما هو ناتج ٣ × ٧ ؟', difficulty_level: 2, type: 'numeric', options: [] },
  { id: 'q4', text: 'إذا كان أحمد يملك ١٢ تفاحة وأعطى ٥ تفاحات لصديقه، فكم تفاحة بقيت معه؟', difficulty_level: 3, type: 'numeric', options: [] },
  { id: 'q5', text: 'ما هو الكسر الذي يمثل الجزء المظلل من الشكل المقسم إلى ٨ أجزاء متساوية إذا ظللت ٣ أجزاء؟', difficulty_level: 4, type: 'multiple_choice', options: ['٣/٨', '٥/٨', '١/٣', '٣/٥'] },
  { id: 'q6', text: 'أكمل النمط: ٢، ٤، ٨، ١٦، ...', difficulty_level: 3, type: 'numeric', options: [] },
  { id: 'q7', text: 'ما هو ناتج ٤٥ ÷ ٥ ؟', difficulty_level: 2, type: 'numeric', options: [] },
  { id: 'q8', text: 'أي الأشكال التالية له ٤ أضلاع متساوية و٤ زوايا قائمة؟', difficulty_level: 3, type: 'multiple_choice', options: ['مستطيل', 'مربع', 'مثلث', 'معين'] },
  { id: 'q9', text: 'إذا كان محيط مربع ٢٠ سم، فما طول ضلعه؟', difficulty_level: 5, type: 'numeric', options: [] },
  { id: 'q10', text: 'رتب الأعداد التالية من الأصغر إلى الأكبر: ٠.٥ ، ١/٤ ، ٠.٧٥ ، ١/٣', difficulty_level: 6, type: 'multiple_choice', options: ['١/٤، ١/٣، ٠.٥، ٠.٧٥', '٠.٥، ٠.٧٥، ١/٤، ١/٣', '١/٣، ١/٤، ٠.٧٥، ٠.٥', '٠.٧٥، ٠.٥، ١/٣، ١/٤'] },
]

// ── Computed ──
const currentQuestion = computed(() => mockQuestions[questionIndex.value])
const progress = computed(() => ({ current: questionIndex.value, total: totalQuestions }))
const mockMasteryLevel = computed(() => {
  const pct = correctCount.value / totalQuestions
  if (pct < 0.1) return 'NOT_STARTED'
  if (pct < 0.4) return 'ATTEMPTED'
  if (pct < 0.7) return 'FAMILIAR'
  if (pct < 0.9) return 'PROFICIENT'
  return 'MASTERED'
})
const mockGroup = computed(() => {
  const pct = correctCount.value / totalQuestions
  if (pct >= 0.7) return 'A'
  if (pct >= 0.4) return 'B'
  return 'C'
})
const errorList = computed(() =>
  Object.entries(errors.value)
    .filter(([, c]) => c > 0)
    .map(([classification, count]) => ({ classification, count }))
)

// ── Actions ──
function startTest() {
  phase.value = 'testing'
  questionIndex.value = 0
  correctCount.value = 0
  errors.value = { RESOURCE: 0, PROCESS: 0, INCIDENTAL: 0, NONE: 0 }
}

function handleAnswer(_answer: string | number) {
  // Mock: randomly determine correctness based on difficulty (harder = less chance)
  const q = currentQuestion.value
  const correctChance = Math.max(0.2, 1 - q.difficulty_level * 0.1 + Math.random() * 0.3)
  const isCorrect = Math.random() < correctChance

  if (isCorrect) {
    correctCount.value++
    errors.value.NONE++
  } else {
    // Random error type for mock
    const types = ['RESOURCE', 'PROCESS', 'INCIDENTAL'] as const
    const errType = types[Math.floor(Math.random() * types.length)]
    errors.value[errType]++
  }

  if (questionIndex.value < totalQuestions - 1) {
    questionIndex.value++
  } else {
    phase.value = 'results'
  }
}

function goBack() {
  router.push('/student')
}
</script>

<template>
  <div dir="rtl" class="min-h-screen bg-background px-4 py-8">
    <!-- Intro phase -->
    <div v-if="phase === 'intro'" class="max-w-lg mx-auto text-center pt-20">
      <div class="w-24 h-24 mx-auto mb-8 bg-primary rounded-full flex items-center justify-center shadow-lg">
        <span class="material-symbols-outlined text-5xl text-on-primary" data-icon="psychology">psychology</span>
      </div>
      <h1 class="text-3xl font-black text-primary mb-4">اختبار تشخيصي</h1>
      <p class="text-on-surface-variant mb-8 leading-relaxed">
        مرحباً بك في الاختبار التشخيصي! سنجري معاً {{ totalQuestions }} أسئلة لمعرفة مستواك.
        لا تقلق — ليس هناك علامات، فقط نريد مساعدتك على التعلم بشكل أفضل.
      </p>
      <button
        class="bg-primary text-on-primary px-10 py-4 rounded-2xl text-xl font-bold
               hover:bg-primary/90 active:scale-95 transition-all shadow-lg"
        @click="startTest"
      >
        ابدأ الاختبار
      </button>
    </div>

    <!-- Testing phase -->
    <div v-else-if="phase === 'testing'" class="max-w-2xl mx-auto">
      <DiagnosticProgress v-bind="progress" />
      <DiagnosticQuestion
        :question="currentQuestion"
        :question-number="questionIndex + 1"
        :total-questions="totalQuestions"
        @answer="handleAnswer"
      />
    </div>

    <!-- Results phase -->
    <div v-else-if="phase === 'results'" class="pt-8">
      <DiagnosticResults
        :mastery-level="mockMasteryLevel"
        :mastery-probability="correctCount / totalQuestions"
        :recommended-group="mockGroup"
        :total-questions="totalQuestions"
        :correct-answers="correctCount"
        :errors="errorList"
      />
      <div class="text-center mt-8">
        <button
          class="bg-primary text-on-primary px-8 py-3 rounded-xl font-bold
                 hover:bg-primary/90 active:scale-95 transition-all"
          @click="goBack"
        >
          العودة للوحة التحكم
        </button>
      </div>
    </div>
  </div>
</template>
