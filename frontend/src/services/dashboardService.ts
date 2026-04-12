import { api } from './api'

export interface SubjectProgress {
  name: string
  competency_id: string
  score: number
  mastery_level: string
  last_assessed: string | null
}

export interface RecentActivity {
  type: 'DIAGNOSTIC' | 'REMEDIATION' | 'PASSPORT' | 'ACHIEVEMENT'
  title: string
  timestamp: string
  status?: string
  progress?: number
}

export interface Recommendation {
  title: string
  description: string
  duration: string
  priority: 'high' | 'medium' | 'low'
}

export interface ChildDashboardData {
  id: string
  name: string
  subjects: SubjectProgress[]
  recent_activities: RecentActivity[]
  summary: string
  recommendations: Recommendation[]
  overall_progress: number
  last_active: string | null
}

export interface ParentDashboard {
  parent_id: string
  children_count: number
  children: ChildDashboardData[]
  generated_at: string
}

export interface ChildSummary {
  child_id: string
  name: string
  avatar_url?: string
  overall_progress: number
  last_active: string | null
  needs_attention: boolean
}

class DashboardService {
  async getDashboardOverview(childId?: string): Promise<ParentDashboard> {
    const params = childId ? { child_id: childId } : {}
    const response = await api.get('/dashboard/overview', { params })
    return response.data
  }

  async getChildDetails(childId: string): Promise<ChildDashboardData> {
    const response = await api.get(`/dashboard/children/${childId}`)
    return response.data
  }

  async getChildrenList(): Promise<ChildSummary[]> {
    const response = await api.get('/dashboard/children')
    return response.data
  }
}

export const dashboardService = new DashboardService()
