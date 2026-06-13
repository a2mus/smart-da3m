import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { User } from '@/types/auth'

// ── Mock Data Types ──────────────────────────────────────────────

export interface MockStudentProfile {
  id: string
  nameAr: string
  nameFr: string
  grade: string
  school: string
  competencies: MockCompetency[]
}

export interface MockCompetency {
  subject: 'MATH' | 'ARABIC' | 'FRENCH'
  name: string
  mastery: 'NOT_STARTED' | 'ATTEMPTED' | 'FAMILIAR' | 'PROFICIENT' | 'MASTERED'
  score: number
}

export interface MockAlert {
  id: string
  severity: 'INFO' | 'WARNING' | 'CRITICAL'
  messageAr: string
  messageFr: string
  timestamp: string
  read: boolean
}

export type MockRole = 'STUDENT' | 'PARENT' | 'EXPERT'

// ── Pre-seeded Mock Data ─────────────────────────────────────────

function createMockUser(role: MockRole): User {
  const users: Record<MockRole, User> = {
    STUDENT: {
      id: 'mock-student-001',
      email: 'ahmed.benali@mock.ihsane.dz',
      role: 'STUDENT',
      language: 'AR',
    },
    PARENT: {
      id: 'mock-parent-001',
      email: 'karima.benali@mock.ihsane.dz',
      role: 'PARENT',
      language: 'AR',
    },
    EXPERT: {
      id: 'mock-expert-001',
      email: 'dr.farid.laouar@mock.ihsane.dz',
      role: 'EXPERT',
      language: 'FR',
    },
  }
  return { ...users[role] }
}

function createMockStudents(): MockStudentProfile[] {
  return [
    {
      id: 'stu-001',
      nameAr: 'أحمد بن علي',
      nameFr: 'Ahmed Benali',
      grade: 'السنة الرابعة',
      school: 'مدرسة الأمير عبد القادر - الجزائر العاصمة',
      competencies: [
        { subject: 'MATH', name: 'الكسور', mastery: 'PROFICIENT', score: 85 },
        { subject: 'MATH', name: 'الضرب', mastery: 'MASTERED', score: 95 },
        { subject: 'MATH', name: 'الهندسة', mastery: 'FAMILIAR', score: 62 },
        { subject: 'ARABIC', name: 'القراءة', mastery: 'PROFICIENT', score: 88 },
        { subject: 'ARABIC', name: 'الإملاء', mastery: 'FAMILIAR', score: 70 },
        { subject: 'ARABIC', name: 'التعبير الكتابي', mastery: 'ATTEMPTED', score: 45 },
        { subject: 'FRENCH', name: 'Lecture', mastery: 'FAMILIAR', score: 65 },
        { subject: 'FRENCH', name: 'Vocabulaire', mastery: 'ATTEMPTED', score: 40 },
        { subject: 'FRENCH', name: 'Grammaire', mastery: 'NOT_STARTED', score: 15 },
      ],
    },
    {
      id: 'stu-002',
      nameAr: 'فاطمة بن علي',
      nameFr: 'Fatima Benali',
      grade: 'السنة الخامسة',
      school: 'مدرسة الأمير عبد القادر - الجزائر العاصمة',
      competencies: [
        { subject: 'MATH', name: 'الكسور', mastery: 'MASTERED', score: 98 },
        { subject: 'MATH', name: 'الضرب', mastery: 'MASTERED', score: 92 },
        { subject: 'MATH', name: 'الهندسة', mastery: 'PROFICIENT', score: 80 },
        { subject: 'ARABIC', name: 'القراءة', mastery: 'MASTERED', score: 95 },
        { subject: 'ARABIC', name: 'الإملاء', mastery: 'PROFICIENT', score: 82 },
        { subject: 'ARABIC', name: 'التعبير الكتابي', mastery: 'PROFICIENT', score: 78 },
        { subject: 'FRENCH', name: 'Lecture', mastery: 'PROFICIENT', score: 80 },
        { subject: 'FRENCH', name: 'Vocabulaire', mastery: 'FAMILIAR', score: 68 },
        { subject: 'FRENCH', name: 'Grammaire', mastery: 'FAMILIAR', score: 60 },
      ],
    },
  ]
}

function createMockAlerts(): MockAlert[] {
  const now = new Date()
  const fmt = (d: Date) => d.toISOString()
  return [
    {
      id: 'alt-001',
      severity: 'WARNING',
      messageAr: 'أحمد فشل في نفس نوع التمرين ٣ مرات متتالية في مادة الكسور',
      messageFr: 'Ahmed a échoué au même type d\'exercice 3 fois consécutives en fractions',
      timestamp: fmt(new Date(now.getTime() - 2 * 60 * 60 * 1000)),
      read: false,
    },
    {
      id: 'alt-002',
      severity: 'INFO',
      messageAr: 'فاطمة أتمت وحدة "الضرب" بنجاح — انتقلت إلى مرحلة الإتقان',
      messageFr: 'Fatima a terminé le module "Multiplication" avec succès — niveau Maîtrise atteint',
      timestamp: fmt(new Date(now.getTime() - 24 * 60 * 60 * 1000)),
      read: true,
    },
    {
      id: 'alt-003',
      severity: 'CRITICAL',
      messageAr: 'أحمد بحاجة إلى دعم فردي في مادة التعبير الكتابي — يُنصح بجلسة تقوية',
      messageFr: 'Ahmed a besoin d\'un soutien individuel en expression écrite — séance de renforcement recommandée',
      timestamp: fmt(new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000)),
      read: false,
    },
    {
      id: 'alt-004',
      severity: 'INFO',
      messageAr: 'لم يسجل أحمد دخوله منذ ٥ أيام — ننصح بتشجيعه على العودة',
      messageFr: 'Ahmed ne s\'est pas connecté depuis 5 jours — encouragez-le à revenir',
      timestamp: fmt(new Date(now.getTime() - 5 * 24 * 60 * 60 * 1000)),
      read: false,
    },
  ]
}

// ── Route mapping ─────────────────────────────────────────────────

const ROLE_ROUTES: Record<MockRole, string> = {
  STUDENT: 'StitchStudentJourney',
  PARENT: 'StitchParentDashboard',
  EXPERT: 'StitchAnalyticsView',
}

// ── Store ─────────────────────────────────────────────────────────

export const useMockUiStore = defineStore('mockUi', () => {
  // ── State ──
  const currentMockRole = ref<MockRole | null>(null)
  const mockUser = ref<User | null>(null)
  const mockStudents = ref<MockStudentProfile[]>([])
  const mockAlerts = ref<MockAlert[]>([])
  const mockCompetencyData = ref<Record<string, MockCompetency[]>>({})

  // ── Getters ──
  const isMockAuthenticated = computed(() => currentMockRole.value !== null)

  const activeRoleRedirect = computed(() => {
    if (!currentMockRole.value) return null
    return ROLE_ROUTES[currentMockRole.value]
  })

  // ── Actions ──
  function selectRole(role: MockRole): string {
    currentMockRole.value = role
    mockUser.value = createMockUser(role)
    mockAlerts.value = createMockAlerts()

    if (role === 'PARENT' || role === 'EXPERT') {
      const students = createMockStudents()
      mockStudents.value = students
      const compData: Record<string, MockCompetency[]> = {}
      for (const s of students) {
        compData[s.id] = s.competencies
      }
      mockCompetencyData.value = compData
    } else {
      // Student: include self as mock student profile
      const selfProfile: MockStudentProfile = {
        id: 'mock-student-001',
        nameAr: 'أحمد بن علي',
        nameFr: 'Ahmed Benali',
        grade: 'السنة الرابعة',
        school: 'مدرسة الأمير عبد القادر - الجزائر العاصمة',
        competencies: [
          { subject: 'MATH', name: 'الكسور', mastery: 'FAMILIAR', score: 65 },
          { subject: 'MATH', name: 'الضرب', mastery: 'PROFICIENT', score: 82 },
          { subject: 'ARABIC', name: 'القراءة', mastery: 'MASTERED', score: 92 },
          { subject: 'ARABIC', name: 'الإملاء', mastery: 'FAMILIAR', score: 68 },
          { subject: 'FRENCH', name: 'Lecture', mastery: 'ATTEMPTED', score: 40 },
        ],
      }
      mockStudents.value = [selfProfile]
      mockCompetencyData.value = { [selfProfile.id]: selfProfile.competencies }
    }

    return ROLE_ROUTES[role]
  }

  function clearSession(): void {
    currentMockRole.value = null
    mockUser.value = null
    mockStudents.value = []
    mockAlerts.value = []
    mockCompetencyData.value = {}
  }

  function getMockDataForRole(role: MockRole) {
    return {
      mockUser: createMockUser(role),
      mockStudents: createMockStudents(),
      mockAlerts: createMockAlerts(),
    }
  }

  return {
    // State
    currentMockRole,
    mockUser,
    mockStudents,
    mockAlerts,
    mockCompetencyData,
    // Getters
    isMockAuthenticated,
    activeRoleRedirect,
    // Actions
    selectRole,
    clearSession,
    getMockDataForRole,
  }
})
