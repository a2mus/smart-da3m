import { http } from '@/services/api'

export interface HeatmapCell {
  student_id: string
  student_name?: string
  competency_id: string
  mastery_level: string
  p_learned?: number
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
  mastery_speed_days?: number
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

export interface RemediationCardItem {
  competency_id: string
  competency_name?: string
  mastery_level: string
  error_classifications: string[]
  recommended_atoms: string[]
}

export interface RemediationCardData {
  student_id: string
  student_name: string
  grade_level: string
  group_name?: string
  items: RemediationCardItem[]
}

export interface RemediationCardsResponse {
  cards: RemediationCardData[]
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
  ): Promise<Blob | ExportResponse> {
    const response = await http.post<ExportResponse>('/analytics/export', {
      format,
      report_type: reportType,
      student_ids: studentIds,
    })
    return response.data
  },

  async getRemediationCards(
    studentId?: string,
    groupId?: string
  ): Promise<RemediationCardsResponse> {
    const params: Record<string, string> = {}
    if (studentId) params.student_id = studentId
    if (groupId) params.group_id = groupId
    const response = await http.get<RemediationCardsResponse>('/analytics/remediation-cards', { params })
    return response.data
  },
}
