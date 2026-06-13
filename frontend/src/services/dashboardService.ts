// ── Dashboard Service Types ────────────────────────────────────────

export interface ChildSummary {
  child_id: string
  name: string
  grade_level: string
  needs_attention: boolean
}

export interface SubjectData {
  competency_id: string
  name: string
  score: number
  mastery_level: string
}

export interface Recommendation {
  title: string
  description: string
  duration?: string
  priority: 'high' | 'medium' | 'low'
}

export interface Activity {
  type: string
  title: string
  timestamp: string
}

export interface ChildDashboardData {
  name: string
  summary: string
  overall_progress: number
  subjects: SubjectData[]
  recommendations: Recommendation[]
  recent_activities: Activity[]
}

// ── Mock Data ──────────────────────────────────────────────────────

const mockChildren: ChildSummary[] = [
  { child_id: 'stu-001', name: 'أحمد', grade_level: 'السنة الرابعة', needs_attention: true },
  { child_id: 'stu-002', name: 'فاطمة', grade_level: 'السنة الخامسة', needs_attention: false },
]

const mockChildData: Record<string, ChildDashboardData> = {
  'stu-001': {
    name: 'أحمد',
    summary: 'أحمد يتفوق في الرياضيات ويحتاج إلى تركيز إضافي في اللغة العربية. أداؤه العام في تحسن مستمر.',
    overall_progress: 68,
    subjects: [
      { competency_id: 'math', name: 'الرياضيات', score: 85, mastery_level: 'PROFICIENT' },
      { competency_id: 'arabic', name: 'اللغة العربية', score: 58, mastery_level: 'FAMILIAR' },
      { competency_id: 'french', name: 'اللغة الفرنسية', score: 45, mastery_level: 'ATTEMPTED' },
    ],
    recommendations: [
      { title: 'تمارين الإملاء', description: '٥ دقائق يومياً من تمارين التاء المربوطة', duration: '5 دقائق', priority: 'high' },
      { title: 'قراءة موجهة', description: 'قراءة قصة قصيرة مع أسئلة الفهم', duration: '10 دقائق', priority: 'medium' },
    ],
    recent_activities: [
      { type: 'DIAGNOSTIC', title: 'اختبار تشخيصي — الكسور', timestamp: new Date(Date.now() - 2 * 3600000).toISOString() },
      { type: 'REMEDIATION', title: 'تمارين جمع الكسور', timestamp: new Date(Date.now() - 86400000).toISOString() },
      { type: 'PASSPORT', title: 'اختبار الجواز — الضرب', timestamp: new Date(Date.now() - 2 * 86400000).toISOString() },
      { type: 'ACHIEVEMENT', title: 'وسام الرياضيات 🏆', timestamp: new Date(Date.now() - 3 * 86400000).toISOString() },
    ],
  },
  'stu-002': {
    name: 'فاطمة',
    summary: 'فاطمة متميزة في جميع المواد. مستواها في تقدم مستمر وتحتاج لأنشطة إثراء.',
    overall_progress: 88,
    subjects: [
      { competency_id: 'math', name: 'الرياضيات', score: 92, mastery_level: 'MASTERED' },
      { competency_id: 'arabic', name: 'اللغة العربية', score: 88, mastery_level: 'PROFICIENT' },
      { competency_id: 'french', name: 'اللغة الفرنسية', score: 78, mastery_level: 'PROFICIENT' },
    ],
    recommendations: [
      { title: 'مسائل متقدمة', description: 'تحديات رياضية للأسبوع', duration: '15 دقيقة', priority: 'low' },
    ],
    recent_activities: [
      { type: 'ACHIEVEMENT', title: 'المركز الأول في التحدي 🥇', timestamp: new Date(Date.now() - 86400000).toISOString() },
      { type: 'REMEDIATION', title: 'مراجعة القواعد', timestamp: new Date(Date.now() - 2 * 86400000).toISOString() },
    ],
  },
}

// ── Service ────────────────────────────────────────────────────────

export const dashboardService = {
  async getChildrenList(): Promise<ChildSummary[]> {
    return Promise.resolve(mockChildren)
  },

  async getChildDetails(childId: string): Promise<ChildDashboardData> {
    const data = mockChildData[childId]
    if (!data) throw new Error(`Child ${childId} not found`)
    return Promise.resolve(data)
  },
}
