export interface HeatmapCell {
  student_id: string
  student_name: string
  competency_id: string
  mastery_level: string
  score: number
}

export interface HeatmapResponse {
  students: { id: string; name: string; grade_level: string }[]
  competencies: string[]
  cells: HeatmapCell[]
}

export interface StudentGroup {
  group_name: string
  student_count: number
  competency: string
  recommended_action: string
}

export interface MetricsResponse {
  gap_reduction_rate: number
  mastery_speed_days: number
  retention_rate: number
  resilience_score: number
}

const mockHeatmap: HeatmapResponse = {
  students: [
    { id: 's1', name: 'أحمد', grade_level: 'السنة 4' },
    { id: 's2', name: 'فاطمة', grade_level: 'السنة 5' },
    { id: 's3', name: 'يوسف', grade_level: 'السنة 4' },
    { id: 's4', name: 'مريم', grade_level: 'السنة 5' },
  ],
  competencies: ['الكسور', 'الضرب', 'الهندسة', 'القراءة', 'الإملاء'],
  cells: [
    { student_id: 's1', student_name: 'أحمد', competency_id: 'الكسور', mastery_level: 'PROFICIENT', score: 85 },
    { student_id: 's1', student_name: 'أحمد', competency_id: 'الضرب', mastery_level: 'MASTERED', score: 95 },
    { student_id: 's1', student_name: 'أحمد', competency_id: 'الهندسة', mastery_level: 'FAMILIAR', score: 62 },
    { student_id: 's2', student_name: 'فاطمة', competency_id: 'الكسور', mastery_level: 'MASTERED', score: 98 },
    { student_id: 's2', student_name: 'فاطمة', competency_id: 'الضرب', mastery_level: 'MASTERED', score: 92 },
  ],
}

const mockGroups: StudentGroup[] = [
  { group_name: 'المجموعة أ — إتقان', student_count: 12, competency: 'الضرب', recommended_action: 'أنشطة إثراء' },
  { group_name: 'المجموعة ب — إتقان جزئي', student_count: 18, competency: 'الكسور', recommended_action: 'تقوية مستهدفة' },
  { group_name: 'المجموعة ج — يحتاج دعماً', student_count: 8, competency: 'الإملاء', recommended_action: 'دعم مكثف' },
]

const mockMetrics: MetricsResponse = {
  gap_reduction_rate: 42,
  mastery_speed_days: 14,
  retention_rate: 73,
  resilience_score: 3.2,
}

export const analyticsService = {
  async getHeatmap(): Promise<HeatmapResponse> { return mockHeatmap },
  async getStudentGroups(): Promise<StudentGroup[]> { return mockGroups },
  async getMetrics(): Promise<MetricsResponse> { return mockMetrics },
}
