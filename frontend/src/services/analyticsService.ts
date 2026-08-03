import { http } from '@/services/api'

export interface HeatmapCell {
  student_id: string
  student_name?: string
  competency_id: string
  mastery_level: string
  p_learned: number
  color?: string
  score: number
}

export interface HeatmapResponse {
  students: { id: string; name: string; grade_level: string }[]
  competencies: string[]
  cells: HeatmapCell[]
  total_students?: number
  total_competencies?: number
}

export interface StudentGroup {
  group_id?: string
  name?: string
  group_name?: string
  student_count: number
  student_ids?: string[]
  students?: string[]
  competency?: string
  error_type?: string
  recommended_action: string
  criteria?: Record<string, unknown>
}

export interface MetricsResponse {
  gap_reduction_rate: number
  mastery_speed_days: number
  retention_rate: number
  resilience_score: number
}

export interface ExportResponse {
  success: boolean
  file_path: string
  format: string
  report_type: string
  generated_at: string
}

export interface RemediationAtomItem {
  id?: string
  title: string
  description: string
  content_type?: string
}

export interface StudentRemediationCard {
  student_id: string
  student_name: string
  grade_level: string
  failed_competencies: string[]
  error_classifications: string[]
  recommended_atoms: RemediationAtomItem[]
  generated_at: string
}

export interface RemediationCardsResponse {
  cards: StudentRemediationCard[]
  total_cards: number
}

export const analyticsService = {
  async getHeatmap(moduleId?: string): Promise<HeatmapResponse> {
    const params = moduleId ? { module_id: moduleId } : {}
    const response = await http.get<HeatmapResponse>('/analytics/heatmap', { params })
    return response.data
  },

  async getStudentGroups(groupBy: string = 'competency'): Promise<StudentGroup[]> {
    const response = await http.post<{ groups: StudentGroup[] }>('/analytics/auto-group', {}, {
      params: { group_by: groupBy }
    })
    return response.data.groups || []
  },

  async getMetrics(): Promise<MetricsResponse> {
    const response = await http.get<MetricsResponse>('/analytics/metrics')
    return response.data
  },

  async exportReport(
    format: 'pdf' | 'csv' = 'csv',
    reportType: string = 'heatmap',
    studentIds?: string[]
  ): Promise<ExportResponse> {
    const response = await http.post<ExportResponse>('/analytics/export', {
      format,
      report_type: reportType,
      student_ids: studentIds,
    })
    return response.data
  },

  async getRemediationCards(studentId?: string): Promise<RemediationCardsResponse> {
    const params = studentId ? { student_id: studentId } : {}
    const response = await http.get<RemediationCardsResponse>('/analytics/remediation-cards', { params })
    return response.data
  },
}
