import api from './api'

export interface HeatmapFilters {
  student_ids?: string[]
  competency_ids?: string[]
  class_id?: string
  grade_level?: string
  subject?: string
}

export interface HeatmapCell {
  student_id: string
  competency_id: string
  mastery_level: string
  p_learned: number
  color: string
  score: number
}

export interface StudentRow {
  id: string
  name: string
  grade_level: string
}

export interface HeatmapResponse {
  students: StudentRow[]
  competencies: string[]
  cells: HeatmapCell[]
  total_students: number
  total_competencies: number
}

export interface StudentGroup {
  group_id: string
  name: string
  student_count: number
  student_ids: string[]
  criteria: Record<string, any>
  recommended_action: string
}

export interface AutoGroupResponse {
  groups: StudentGroup[]
  total_groups: number
  group_by: string
}

export interface MetricsResponse {
  gap_reduction_rate: number
  mastery_speed: number
  retention_rate: number
  effort_vs_results: number
  resilience_score: number
  total_students: number
  total_assessments: number
}

export interface ExportRequest {
  format: 'csv' | 'pdf'
  report_type: 'heatmap' | 'remediation_card' | 'full_report'
  filters?: HeatmapFilters
  student_ids?: string[]
}

export interface ExportResponse {
  success: boolean
  file_path: string
  format: string
  report_type: string
  generated_at: string
}

class AnalyticsService {
  async getHeatmap(filters: HeatmapFilters = {}): Promise<HeatmapResponse> {
    const response = await api.post<HeatmapResponse>('/analytics/heatmap', filters)
    return response.data
  }

  async autoGroup(
    filters: HeatmapFilters = {},
    groupBy: 'competency' | 'error_type' = 'competency'
  ): Promise<AutoGroupResponse> {
    const response = await api.post<AutoGroupResponse>(
      `/analytics/auto-group?group_by=${groupBy}`,
      filters
    )
    return response.data
  }

  async getMetrics(
    classId?: string,
    startDate?: string,
    endDate?: string
  ): Promise<MetricsResponse> {
    const params = new URLSearchParams()
    if (classId) params.append('class_id', classId)
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)

    const response = await api.get<MetricsResponse>(
      `/analytics/metrics?${params.toString()}`
    )
    return response.data
  }

  async exportReport(request: ExportRequest): Promise<ExportResponse> {
    const response = await api.post<ExportResponse>('/analytics/export', request)
    return response.data
  }
}

export const analyticsService = new AnalyticsService()
export default analyticsService