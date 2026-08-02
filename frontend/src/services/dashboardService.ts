import api from '@/services/api'

// ── Dashboard Service Types ────────────────────────────────────────

export interface ChildSummary {
  childId?: string
  child_id?: string
  name: string
  gradeLevel?: string
  grade_level?: string
  needsAttention?: boolean
  needs_attention?: boolean
  overallProgress?: number
  overall_progress?: number
}

export interface SubjectData {
  competencyId?: string
  competency_id?: string
  name: string
  score: number
  masteryLevel?: string
  mastery_level?: string
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
  id?: string
  name: string
  summary: string
  overallProgress?: number
  overall_progress?: number
  subjects: SubjectData[]
  recommendations: Recommendation[]
  recentActivities?: Activity[]
  recent_activities?: Activity[]
}

export interface ParentDashboardResponse {
  parentId?: string
  parent_id?: string
  childrenCount?: number
  children_count?: number
  children: ChildDashboardData[]
  generatedAt?: string
  generated_at?: string
}

// ── Service ────────────────────────────────────────────────────────

export const dashboardService = {
  /**
   * Fetch complete dashboard overview for the authenticated parent.
   */
  async getOverview(childId?: string): Promise<ParentDashboardResponse> {
    const params = childId ? { child_id: childId } : {}
    const response = await api.get<ParentDashboardResponse>('/dashboard/overview', { params })
    return response.data
  },

  /**
   * Fetch list of all children for the authenticated parent.
   */
  async getChildrenList(): Promise<ChildSummary[]> {
    const response = await api.get<ChildSummary[]>('/dashboard/children')
    // Normalize properties for backward compatibility across both camelCase and snake_case callers
    return response.data.map((item) => ({
      ...item,
      child_id: item.childId || item.child_id || '',
      childId: item.childId || item.child_id || '',
      needs_attention: item.needsAttention ?? item.needs_attention ?? false,
      needsAttention: item.needsAttention ?? item.needs_attention ?? false,
    }))
  },

  /**
   * Fetch detailed dashboard data for a specific child.
   */
  async getChildDetails(childId: string): Promise<ChildDashboardData> {
    const response = await api.get<ChildDashboardData>(`/dashboard/children/${childId}`)
    const data = response.data
    return {
      ...data,
      overall_progress: data.overallProgress ?? data.overall_progress ?? 0,
      overallProgress: data.overallProgress ?? data.overall_progress ?? 0,
      recent_activities: data.recentActivities || data.recent_activities || [],
      recentActivities: data.recentActivities || data.recent_activities || [],
      subjects: (data.subjects || []).map((s) => ({
        ...s,
        competency_id: s.competencyId || s.competency_id || '',
        competencyId: s.competencyId || s.competency_id || '',
        mastery_level: s.masteryLevel || s.mastery_level || 'NOT_STARTED',
        masteryLevel: s.masteryLevel || s.mastery_level || 'NOT_STARTED',
      })),
    }
  },
}
