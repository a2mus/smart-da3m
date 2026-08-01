import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// Case conversion helpers
function toCamelCase(str: string): string {
  return str.replace(/_([a-z0-9])/g, (_, letter) => letter.toUpperCase())
}

function toSnakeCase(str: string): string {
  return str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`)
}

function isObject(val: unknown): val is Record<string, unknown> {
  return (
    val !== null &&
    typeof val === 'object' &&
    !(val instanceof Date) &&
    !(val instanceof RegExp) &&
    !(val instanceof Blob) &&
    !(val instanceof File) &&
    !(val instanceof FormData)
  )
}

export function keysToCamelCase<T>(obj: unknown): T {
  if (Array.isArray(obj)) {
    return obj.map((v) => keysToCamelCase(v)) as unknown as T
  }
  if (isObject(obj)) {
    const n: Record<string, unknown> = {}
    Object.keys(obj).forEach((k) => {
      n[toCamelCase(k)] = keysToCamelCase(obj[k])
    })
    return n as T
  }
  return obj as T
}

export function keysToSnakeCase<T>(obj: unknown): T {
  if (Array.isArray(obj)) {
    return obj.map((v) => keysToSnakeCase(v)) as unknown as T
  }
  if (isObject(obj)) {
    const n: Record<string, unknown> = {}
    Object.keys(obj).forEach((k) => {
      n[toSnakeCase(k)] = keysToSnakeCase(obj[k])
    })
    return n as T
  }
  return obj as T
}

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
})

// Request interceptor - Add JWT token to headers and convert camelCase payload to snake_case
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const token = authStore.token
    const activeOrgId = authStore.activeOrganizationId

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    if (activeOrgId) {
      config.headers['X-Organization-Id'] = activeOrgId
    }

    if (config.data && isObject(config.data)) {
      config.data = keysToSnakeCase(config.data)
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Convert snake_case response to camelCase and handle auth errors
api.interceptors.response.use(
  (response) => {
    if (response.data && isObject(response.data)) {
      response.data = keysToCamelCase(response.data)
    }
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }

    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const authStore = useAuthStore()

      // Try to refresh the token
      try {
        const refreshed = await authStore.refreshAccessToken()

        if (refreshed) {
          // Retry the original request with new token
          originalRequest.headers = {
            ...originalRequest.headers,
            Authorization: `Bearer ${authStore.token}`,
          }
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, logout and redirect
        authStore.clearAuth()
        router.push({ name: 'Login', query: { session_expired: 'true' } })
        return Promise.reject(refreshError)
      }
    }

    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      // User doesn't have permission for this resource
      console.error('Permission denied:', error.response.data)
    }

    // Handle network errors
    if (!error.response) {
      console.error('Network error - no response from server')
    }

    return Promise.reject(error)
  }
)

// Auth API endpoints
export const authApi = {
  // Email/password login (for parents/experts)
  loginWithEmail: (email: string, password: string) =>
    api.post('/auth/login/email', { email, password }),

  // PIN login (for students)
  loginWithPin: (parentEmail: string, pinCode: string) =>
    api.post('/auth/login/pin', { parentEmail, pinCode }),

  // Refresh access token
  refreshToken: (refreshToken: string) =>
    api.post('/auth/refresh', { refreshToken }),

  // Logout
  logout: () => api.post('/auth/logout'),

  // Get current user info
  getMe: () => api.get('/auth/me'),

  // Register parent
  registerParent: (email: string, password: string, language: 'AR' | 'FR' = 'AR', name?: string) =>
    api.post('/auth/register/parent', { email, password, language, name }),

  // Register student (child)
  registerStudent: (parentId: string, pinCode: string) =>
    api.post('/auth/register/student', { parentId, pinCode }),
}

// Diagnostic API
export const diagnosticApi = {
  startSession: (moduleId: string) =>
    api.post('/diagnostic/start', { moduleId }),

  submitAnswer: (sessionId: string, questionId: string, answer: string | number, responseTimeMs: number) =>
    api.post('/diagnostic/answer', {
      sessionId,
      questionId,
      answer,
      responseTimeMs,
    }),

  getResults: (sessionId: string) =>
    api.get(`/diagnostic/${sessionId}/results`),
}

// Generic API methods
export const http = {
  get: <T>(url: string, config?: AxiosRequestConfig) => api.get<T>(url, config),
  post: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    api.post<T>(url, data, config),
  put: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    api.put<T>(url, data, config),
  patch: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    api.patch<T>(url, data, config),
  delete: <T>(url: string, config?: AxiosRequestConfig) =>
    api.delete<T>(url, config),
}

export { api }
export default api
