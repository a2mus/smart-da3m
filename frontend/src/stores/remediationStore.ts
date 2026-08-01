import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  remediationService,
  type RemediationPath,
  type KnowledgeAtom,
  type AtomCompletion,
  type PassportQuestion,
  type PassportEvaluation,
} from '@/services/remediationService'

export const useRemediationStore = defineStore('remediation', () => {
  // State
  const pathway = ref<RemediationPath | null>(null)
  const currentAtomIndex = ref<number>(0)
  const loading = ref<boolean>(false)
  const actionLoading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const passportQuestions = ref<PassportQuestion[]>([])
  const passportEvaluation = ref<PassportEvaluation | null>(null)

  // Getters & Computed
  const currentAtom = computed<KnowledgeAtom | null>(() => {
    if (!pathway.value || !pathway.value.atoms || pathway.value.atoms.length === 0) return null
    return pathway.value.atoms[currentAtomIndex.value] || null
  })

  const atomsCompleted = computed<string[]>(() => {
    return pathway.value?.atoms_completed || []
  })

  const progressPercent = computed<number>(() => {
    return pathway.value?.progress_percent || 0
  })

  const canTakePassport = computed<boolean>(() => {
    if (!pathway.value) return false
    return pathway.value.status === 'COMPLETED' || (pathway.value.atoms_completed?.length || 0) >= (pathway.value.atoms?.length || 1)
  })

  function isAtomCompleted(atomId: string): boolean {
    return atomsCompleted.value.includes(atomId)
  }

  // Actions
  async function fetchPathway(competencyId: string, studentGroup = 'B') {
    loading.value = true
    error.value = null
    try {
      const data = await remediationService.getPathway(competencyId, studentGroup)
      pathway.value = data
      if (data && data.atoms) {
        const firstUncompleted = data.atoms.findIndex((a) => !isAtomCompleted(a.id))
        currentAtomIndex.value = firstUncompleted !== -1 ? firstUncompleted : 0
      }
      return data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'تعذر تحميل مسار المعالجة'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function startPathway(pathId: string) {
    actionLoading.value = true
    error.value = null
    try {
      const res = await remediationService.startPathway(pathId)
      if (pathway.value) {
        pathway.value.status = 'IN_PROGRESS'
      }
      return res
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'تعذر بدء مسار المعالجة'
      throw err
    } finally {
      actionLoading.value = false
    }
  }

  async function completeAtom(
    atomId: string,
    data: { time_spent_ms: number; interactions_count: number; is_correct: boolean } = {
      time_spent_ms: 15000,
      interactions_count: 1,
      is_correct: true,
    }
  ): Promise<AtomCompletion> {
    actionLoading.value = true
    error.value = null
    try {
      const res = await remediationService.completeAtom(atomId, data)
      if (pathway.value) {
        if (!pathway.value.atoms_completed.includes(atomId)) {
          pathway.value.atoms_completed.push(atomId)
        }
        pathway.value.progress_percent = res.progress_percent
        if (res.atoms_completed >= (pathway.value.atoms?.length || 0)) {
          pathway.value.status = 'COMPLETED'
        }
      }
      if (currentAtomIndex.value < (pathway.value?.atoms?.length || 0) - 1) {
        currentAtomIndex.value++
      }
      return res
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'تعذر تسجيل إكمال الكبسولة'
      throw err
    } finally {
      actionLoading.value = false
    }
  }

  async function fetchPassportQuestions(competencyId: string) {
    loading.value = true
    error.value = null
    try {
      const res = await remediationService.getPassportQuestions(competencyId)
      passportQuestions.value = res.questions
      return res
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'تعذر تحميل أسئلة اختبار الجواز'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function evaluatePassport(
    competencyId: string,
    answers: { question_id: string; answer: string; time_ms: number }[]
  ): Promise<PassportEvaluation> {
    actionLoading.value = true
    error.value = null
    try {
      const evaluation = await remediationService.evaluatePassport(competencyId, answers)
      passportEvaluation.value = evaluation
      if (pathway.value) {
        pathway.value.status = evaluation.passed ? 'COMPLETED' : 'IN_PROGRESS'
      }
      return evaluation
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'تعذر تقييم نتائج اختبار الجواز'
      throw err
    } finally {
      actionLoading.value = false
    }
  }

  function reset() {
    pathway.value = null
    currentAtomIndex.value = 0
    loading.value = false
    actionLoading.value = false
    error.value = null
    passportQuestions.value = []
    passportEvaluation.value = null
  }

  return {
    pathway,
    currentAtomIndex,
    loading,
    actionLoading,
    error,
    passportQuestions,
    passportEvaluation,
    currentAtom,
    atomsCompleted,
    progressPercent,
    canTakePassport,
    isAtomCompleted,
    fetchPathway,
    startPathway,
    completeAtom,
    fetchPassportQuestions,
    evaluatePassport,
    reset,
  }
})
