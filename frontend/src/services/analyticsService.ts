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
  group_name: string
  student_count: number
  competency: string
  recommended_action: string
}

export interface MetricsResponse {
  gap_reduction_rate: number
  mastery_speed_days?: number
  retention_rate: number
  resilience_score: number
}

export const analyticsService = {
  async getHeatmap(moduleId?: string): Promise<HeatmapResponse> {
    const params = moduleId ? { module_id: moduleId } : {}
    const response = await http.get<HeatmapResponse>('/analytics/heatmap', { params })
    return response.data
  },

  async getStudentGroups(): Promise<StudentGroup[]> {
    const response = await http.post<{ groups: StudentGroup[] }>('/analytics/auto-group')
    return response.data.groups || []
  },

  async getMetrics(): Promise<MetricsResponse> {
    const response = await http.get<MetricsResponse>('/analytics/metrics')
    return response.data
  },
}
