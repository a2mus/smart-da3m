import { api } from './api'

export interface Alert {
  id: string
  student_id: string
  trigger_type: 'REPEATED_FAILURE' | 'FRUSTRATION' | 'PASSPORT_FAILED' | 'INACTIVITY' | 'ABANDONMENT'
  severity: 'INFO' | 'WARNING' | 'CRITICAL'
  status: 'UNREAD' | 'READ' | 'RESOLVED' | 'DISMISSED'
  simplified_message: string
  expert_message: string
  recommended_action?: string
  context_data: Record<string, any>
  created_at: string
  read_at?: string
}

export interface AlertList {
  items: Alert[]
  total: number
  unread_count: number
}

export interface ParentAlertSummary {
  id: string
  severity: 'INFO' | 'WARNING' | 'CRITICAL'
  message: string
  created_at: string
  is_read: boolean
}

class AlertService {
  async getAlerts(unreadOnly = false): Promise<AlertList> {
    const response = await api.get('/dashboard/alerts', {
      params: { unread_only: unreadOnly },
    })
    return response.data
  }

  async markAlertsRead(alertIds: string[]): Promise<{ marked_count: number }> {
    const response = await api.post('/dashboard/alerts/mark-read', {
      alert_ids: alertIds,
    })
    return response.data
  }

  async getChildAlerts(childId: string): Promise<ParentAlertSummary[]> {
    const response = await api.get(`/dashboard/children/${childId}/alerts`)
    return response.data
  }

  getSeverityColor(severity: string): string {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-red-500'
      case 'WARNING':
        return 'bg-yellow-500'
      case 'INFO':
        return 'bg-blue-500'
      default:
        return 'bg-gray-400'
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
