import { api } from './api'

export interface Alert {
  id: string
  studentId?: string
  student_id?: string
  triggerType?: 'REPEATED_FAILURE' | 'FRUSTRATION' | 'PASSPORT_FAILED' | 'INACTIVITY' | 'ABANDONMENT' | string
  trigger_type?: 'REPEATED_FAILURE' | 'FRUSTRATION' | 'PASSPORT_FAILED' | 'INACTIVITY' | 'ABANDONMENT' | string
  severity: 'INFO' | 'WARNING' | 'CRITICAL'
  status?: 'UNREAD' | 'READ' | 'RESOLVED' | 'DISMISSED' | string
  simplifiedMessage?: string
  simplified_message?: string
  expertMessage?: string
  expert_message?: string
  recommendedAction?: string
  recommended_action?: string
  contextData?: Record<string, any>
  context_data?: Record<string, any>
  createdAt?: string
  created_at?: string
  readAt?: string
  read_at?: string
  isRead?: boolean
  is_read?: boolean
  message?: string
}

export interface AlertList {
  items: Alert[]
  total: number
  unreadCount?: number
  unread_count?: number
}

export interface ParentAlertSummary {
  id: string
  severity: 'INFO' | 'WARNING' | 'CRITICAL'
  message: string
  createdAt?: string
  created_at?: string
  isRead?: boolean
  is_read?: boolean
}

class AlertService {
  async getAlerts(unreadOnly = false): Promise<AlertList> {
    try {
      const response = await api.get('/alerts', {
        params: { unread_only: unreadOnly },
      })
      return this.normalizeAlertList(response.data)
    } catch {
      // Fallback to legacy dashboard endpoint if /alerts is not reachable
      const response = await api.get('/dashboard/alerts', {
        params: { unread_only: unreadOnly },
      })
      return this.normalizeAlertList(response.data)
    }
  }

  async getAlertsSince(sinceTimestamp: string): Promise<Alert[]> {
    try {
      const response = await api.get('/alerts', {
        params: { since: sinceTimestamp },
      })
      const list = this.normalizeAlertList(response.data)
      return list.items
    } catch {
      const response = await api.get('/dashboard/alerts', {
        params: { since: sinceTimestamp },
      })
      const list = this.normalizeAlertList(response.data)
      return list.items
    }
  }

  async markAlertsRead(alertIds: string[]): Promise<{ markedCount: number }> {
    try {
      const response = await api.post('/alerts/mark-read', {
        alert_ids: alertIds,
        alertIds: alertIds,
      })
      return {
        markedCount: response.data?.markedCount || response.data?.marked_count || alertIds.length,
      }
    } catch {
      const response = await api.post('/dashboard/alerts/mark-read', {
        alert_ids: alertIds,
        alertIds: alertIds,
      })
      return {
        markedCount: response.data?.markedCount || response.data?.marked_count || alertIds.length,
      }
    }
  }

  async getChildAlerts(childId: string): Promise<ParentAlertSummary[]> {
    const response = await api.get(`/dashboard/children/${childId}/alerts`)
    const data = response.data
    if (Array.isArray(data)) {
      return data.map(item => ({
        id: item.id,
        severity: item.severity,
        message: item.message || item.simplifiedMessage || item.simplified_message || '',
        createdAt: item.createdAt || item.created_at || new Date().toISOString(),
        created_at: item.createdAt || item.created_at || new Date().toISOString(),
        isRead: item.isRead ?? item.is_read ?? false,
        is_read: item.isRead ?? item.is_read ?? false,
      }))
    }
    return []
  }

  normalizeAlert(a: any): Alert {
    const simplified = a.simplifiedMessage || a.simplified_message || a.message || ''
    const expert = a.expertMessage || a.expert_message || a.message || ''
    const created = a.createdAt || a.created_at || new Date().toISOString()
    const isReadBool = a.isRead ?? a.is_read ?? (a.status === 'READ')

    return {
      id: a.id,
      studentId: a.studentId || a.student_id || '',
      student_id: a.studentId || a.student_id || '',
      triggerType: a.triggerType || a.trigger_type || 'REPEATED_FAILURE',
      trigger_type: a.triggerType || a.trigger_type || 'REPEATED_FAILURE',
      severity: a.severity || 'INFO',
      status: a.status || (isReadBool ? 'READ' : 'UNREAD'),
      simplifiedMessage: simplified,
      simplified_message: simplified,
      expertMessage: expert,
      expert_message: expert,
      recommendedAction: a.recommendedAction || a.recommended_action,
      recommended_action: a.recommendedAction || a.recommended_action,
      contextData: a.contextData || a.context_data || {},
      context_data: a.contextData || a.context_data || {},
      createdAt: created,
      created_at: created,
      readAt: a.readAt || a.read_at,
      read_at: a.readAt || a.read_at,
      isRead: isReadBool,
      is_read: isReadBool,
      message: simplified || expert,
    }
  }

  private normalizeAlertList(data: any): AlertList {
    if (!data) {
      return { items: [], total: 0, unreadCount: 0, unread_count: 0 }
    }
    const items = Array.isArray(data.items) ? data.items.map((i: any) => this.normalizeAlert(i)) : (Array.isArray(data) ? data.map((i: any) => this.normalizeAlert(i)) : [])
    const total = data.total ?? items.length
    const unreadCount = data.unreadCount ?? data.unread_count ?? items.filter((i: Alert) => !i.isRead).length

    return {
      items,
      total,
      unreadCount,
      unread_count: unreadCount,
    }
  }

  getSeverityColor(severity: string): string {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-error-container text-error border-outline'
      case 'WARNING':
        return 'bg-secondary-container text-secondary border-outline'
      case 'INFO':
        return 'bg-primary-container text-primary border-outline'
      default:
        return 'bg-surface-container text-on-surface-variant border-outline-variant'
    }
  }

  getSeverityIcon(severity: string): string {
    switch (severity) {
      case 'CRITICAL':
        return '🔴'
      case 'WARNING':
        return '🟡'
      case 'INFO':
        return '🔵'
      default:
        return '⚪'
    }
  }
}

export const alertService = new AlertService()
