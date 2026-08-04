import { http } from './api'

export interface MasteryCell {
  student_id: string
  student_name: string
  competency_id: string
  mastery_level: string
  p_learned: number
}

export interface HeatmapResponse {
  students: { id: string; name: string }[]
  competencies: string[]
  grid: Record<string, Record<string, MasteryCell>>
}

export interface StudentGroup {
  id: string
  name: string
  description?: string
  student_ids: string[]
  student_count?: number
  common_failed_competencies?: string[]
}

export interface MetricsResponse {
  total_students: number
  gap_reduction_rate?: number
  mastery_speed?: number
  mastery_speed_days?: number
  retention_rate?: number
  effort_vs_results?: number
  resilience_score?: number
  total_assessments?: number
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
  items?: RemediationCardItem[]
  failed_competencies?: string[]
  error_classifications?: string[]
  recommended_atoms?: RemediationAtomItem[]
  generated_at?: string
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
    return {
      ...response.data,
      total_assessments: response.data?.total_assessments ?? 0,
    }
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
