import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { UserRole } from '@/types/auth'
import { authApi } from '@/services/api'

export interface User {
  id: string
  email: string | null
  role: UserRole
  language: 'AR' | 'FR'
  parentId?: string | null
}

export interface AuthState {
  token: string | null
  refreshToken: string | null
  user: User | null
  isLoading: boolean
  error: string | null
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'))
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRole = computed(() => user.value?.role || null)
  const isStudent = computed(() => user.value?.role === 'STUDENT')
  const isParent = computed(() => user.value?.role === 'PARENT')
  const isExpert = computed(() => user.value?.role === 'EXPERT')
  const currentUser = computed(() => user.value)

  // RBAC Checkers
  const canAccess = (allowedRoles: UserRole[]) => {
    if (!user.value) return false
    return allowedRoles.includes(user.value.role)
  }

  const isOwnerOr = (resourceOwnerId: string, allowedRoles: UserRole[] = []) => {
    if (!user.value) return false
    if (user.value.id === resourceOwnerId) return true
    return allowedRoles.includes(user.value.role)
  }

  // Actions
  async function loginWithEmail(email: string, password: string) {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.loginWithEmail(email, password)
      const { access_token, refresh_token } = response.data

      token.value = access_token
      refreshToken.value = refresh_token

      localStorage.setItem('token', access_token)
      localStorage.setItem('refreshToken', refresh_token)

      // Fetch user info
      await fetchCurrentUser()

      return true
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } }
      error.value = axiosError.response?.data?.detail || 'Login failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function loginWithPin(pinCode: string) {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.loginWithPin(pinCode)
      const { access_token, refresh_token } = response.data

      token.value = access_token
      refreshToken.value = refresh_token

      localStorage.setItem('token', access_token)
      localStorage.setItem('refreshToken', refresh_token)

      // Fetch user info
      await fetchCurrentUser()

      return true
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } }
      error.value = axiosError.response?.data?.detail || 'Invalid PIN code'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function refreshAccessToken(): Promise<boolean> {
    if (!refreshToken.value) return false

    try {
      const response = await authApi.refreshToken(refreshToken.value)
      const { access_token, refresh_token } = response.data

      token.value = access_token
      refreshToken.value = refresh_token

      localStorage.setItem('token', access_token)
      localStorage.setItem('refreshToken', refresh_token)

      return true
    } catch {
      // Refresh failed, clear auth
      clearAuth()
      return false
    }
  }

  async function fetchCurrentUser() {
    try {
      const response = await authApi.getMe()
      user.value = response.data

      // Update language preference
      if (user.value?.language) {
        const { locale } = useI18n()
        locale.value = user.value.language.toLowerCase()
        localStorage.setItem('language', user.value.language.toLowerCase())

        // Update document direction
        const dir = user.value.language === 'AR' ? 'rtl' : 'ltr'
        document.documentElement.setAttribute('dir', dir)
        document.documentElement.setAttribute('lang', user.value.language.toLowerCase())
      }
    } catch {
      user.value = null
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch {
      // Ignore errors on logout
    } finally {
      clearAuth()
    }
  }

  function clearAuth() {
    token.value = null
    refreshToken.value = null
    user.value = null
    error.value = null

    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }

  function getDefaultRouteForRole(): string {
    switch (user.value?.role) {
      case 'STUDENT':
        return 'StudentDashboard'
      case 'PARENT':
        return 'ParentDashboard'
      case 'EXPERT':
        return 'ExpertDashboard'
      default:
        return 'Home'
    }
  }

  // Initialize from storage on app start
  async function initAuth() {
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      token.value = storedToken
      await fetchCurrentUser()
    }
  }

  return {
    // State
    token,
    refreshToken,
    user,
    isLoading,
    error,
    // Getters
    isAuthenticated,
    userRole,
    isStudent,
    isParent,
    isExpert,
    currentUser,
    // RBAC
    canAccess,
    isOwnerOr,
    // Actions
    loginWithEmail,
    loginWithPin,
    refreshAccessToken,
    fetchCurrentUser,
    logout,
    clearAuth,
    getDefaultRouteForRole,
    initAuth,
  }
})
