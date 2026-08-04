import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import i18n from '@/i18n'
import type { OrganizationClaim, UserRole } from '@/types/auth'
import { authApi } from '@/services/api'

export interface User {
  id: string
  email: string | null
  role: UserRole
  language: 'AR' | 'FR'
  parentId?: string | null
  organizations?: OrganizationClaim[]
}

export interface AuthState {
  token: string | null
  refreshToken: string | null
  user: User | null
  activeOrganizationId: string | null
  isLoading: boolean
  error: string | null
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'))
  const activeOrganizationId = ref<string | null>(localStorage.getItem('activeOrganizationId'))
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
  const organizations = computed(() => user.value?.organizations || [])
  const hasMultipleOrganizations = computed(() => organizations.value.length > 1)
  const activeOrganization = computed(() => {
    if (!organizations.value.length) return null
    return (
      organizations.value.find((org) => org.id === activeOrganizationId.value) ||
      organizations.value[0]
    )
  })

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

  function setActiveOrganization(id: string) {
    activeOrganizationId.value = id
    localStorage.setItem('activeOrganizationId', id)
  }

  // Actions
  async function loginWithEmail(email: string, password: string) {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.loginWithEmail(email, password)
      const { accessToken, refreshToken: newRefreshToken } = response.data as {
        accessToken: string
        refreshToken: string
      }

      token.value = accessToken
      refreshToken.value = newRefreshToken

      localStorage.setItem('token', accessToken)
      localStorage.setItem('refreshToken', newRefreshToken)

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

  async function loginWithPin(parentEmail: string, pinCode: string) {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.loginWithPin(parentEmail, pinCode)
      const { accessToken, refreshToken: newRefreshToken } = response.data as {
        accessToken: string
        refreshToken: string
      }

      token.value = accessToken
      refreshToken.value = newRefreshToken

      localStorage.setItem('token', accessToken)
      localStorage.setItem('refreshToken', newRefreshToken)

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
      const { accessToken, refreshToken: newRefreshToken } = response.data as {
        accessToken: string
        refreshToken: string
      }

      token.value = accessToken
      refreshToken.value = newRefreshToken

      localStorage.setItem('token', accessToken)
      localStorage.setItem('refreshToken', newRefreshToken)

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

      const userOrgs = user.value?.organizations || []
      if (userOrgs.length > 0) {
        const isValidActive = userOrgs.some((org) => org.id === activeOrganizationId.value)
        if (!isValidActive) {
          activeOrganizationId.value = userOrgs[0].id
          localStorage.setItem('activeOrganizationId', userOrgs[0].id)
        }
      } else {
        activeOrganizationId.value = null
        localStorage.removeItem('activeOrganizationId')
      }

      // Update language preference
      if (user.value?.language) {
        const lang = user.value.language.toLowerCase()
        if (i18n.global.locale) {
          ;(i18n.global.locale as any).value = lang
        }
        localStorage.setItem('language', lang)

        // Update document direction
        const dir = user.value.language === 'AR' ? 'rtl' : 'ltr'
        document.documentElement.setAttribute('dir', dir)
        document.documentElement.setAttribute('lang', lang)
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
    activeOrganizationId.value = null
    error.value = null

    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('activeOrganizationId')
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

  async function registerParent(email: string, password: string, language: 'AR' | 'FR' = 'AR', name?: string) {
    isLoading.value = true
    error.value = null

    try {
      await authApi.registerParent(email, password, language, name)
      return await loginWithEmail(email, password)
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } }
      error.value = axiosError.response?.data?.detail || 'Registration failed'
      return false
    } finally {
      isLoading.value = false
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
    token,
    refreshToken,
    user,
    activeOrganizationId,
    isLoading,
    error,
    isAuthenticated,
    userRole,
    isStudent,
    isParent,
    isExpert,
    currentUser,
    organizations,
    hasMultipleOrganizations,
    activeOrganization,
    canAccess,
    isOwnerOr,
    setActiveOrganization,
    registerParent,
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
