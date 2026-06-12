import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMockUiStore } from '@/stores/mockUiStore'
import type { UserRole } from '@/types/auth'

declare module 'vue-router' {
  interface RouteMeta {
    public?: boolean
    guestOnly?: boolean
    requiresAuth?: boolean
    requiresMockAuth?: boolean
    allowedRoles?: UserRole[]
  }
}

const routes: RouteRecordRaw[] = [
  /*
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { public: true }
  },
  */
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true, guestOnly: true }
  },
  // Student Routes
  {
    path: '/student',
    name: 'StudentDashboard',
    component: () => import('@/views/student/Dashboard.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: ['STUDENT']
    }
  },
  {
    path: '/student/diagnostic',
    name: 'DiagnosticSession',
    component: () => import('@/views/student/DiagnosticSession.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: ['STUDENT']
    }
  },
  {
    path: '/student/remediation',
    name: 'RemediationSession',
    component: () => import('@/views/student/RemediationSession.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: ['STUDENT']
    }
  },
  // Parent Routes
  {
    path: '/parent',
    name: 'ParentDashboard',
    component: () => import('@/views/parent/Dashboard.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: ['PARENT']
    }
  },
  // Expert Routes
  {
    path: '/expert',
    name: 'ExpertDashboard',
    component: () => import('@/views/expert/Dashboard.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: ['EXPERT']
    }
  },
  {
    path: '/expert/modules',
    name: 'ModuleList',
    component: () => import('@/views/expert/ModuleList.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: ['EXPERT']
    }
  },
  {
    path: '/expert/modules/:id/edit',
    name: 'ModuleEditor',
    component: () => import('@/views/expert/ModuleEditor.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: ['EXPERT']
    }
  },
  {
    path: '/expert/analytics',
    name: 'ExpertAnalytics',
    component: () => import('@/views/expert/Analytics.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: ['EXPERT']
    }
  },
  // Stitch Mockup Routes
  {
    path: '/', // Overriding Home for LandingPage (or just use /landing if better, quickstart says "Navigate to Landing Page (/)")
    name: 'LandingPage',
    component: () => import('@/views/LandingPage.vue'),
    meta: { public: true }
  },
  {
    path: '/mock-auth',
    name: 'MockAuth',
    component: () => import('@/views/MockAuth.vue'),
    meta: { public: true }
  },
  {
    path: '/parent-dashboard',
    name: 'StitchParentDashboard',
    component: () => import('@/views/ParentDashboard.vue'),
    meta: { requiresMockAuth: true }
  },
  {
    path: '/parent/analytics',
    name: 'StitchAnalyticsView',
    component: () => import('@/views/AnalyticsView.vue'),
    meta: { requiresMockAuth: true }
  },
  {
    path: '/student/journey',
    name: 'StitchStudentJourney',
    component: () => import('@/views/StudentJourney.vue'),
    meta: { requiresMockAuth: true }
  },
  // 404
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { public: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    // Always scroll to top on navigation
    return { top: 0 }
  }
})

// Track if auth has been initialized
let authInitialized = false

// Navigation guards
router.beforeEach(async (
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  const authStore = useAuthStore()
  const mockStore = useMockUiStore()

  // Initialize auth on first navigation
  if (!authInitialized) {
    await authStore.initAuth()
    authInitialized = true
  }

  const isAuthenticated = authStore.isAuthenticated
  const isMockAuth = mockStore.isMockAuthenticated
  const userRole = authStore.userRole

  // ── Mock Auth Guard ──
  // If route requires mock auth and user is not mock-authenticated, redirect to mock-auth
  if (to.meta.requiresMockAuth && !isMockAuth) {
    return next({ name: 'MockAuth' })
  }

  // If user is mock-authenticated and tries to go to /mock-auth, redirect to their dashboard
  if (to.name === 'MockAuth' && isMockAuth) {
    const redirect = mockStore.activeRoleRedirect
    if (redirect) return next({ name: redirect })
  }

  // Handle public routes
  if (to.meta.public) {
    // If guest-only route and user is authenticated, redirect to appropriate dashboard
    if (to.meta.guestOnly && isAuthenticated) {
      const redirectRoute = authStore.getDefaultRouteForRole()
      return next({ name: redirectRoute })
    }
    return next()
  }

  // Check authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({
      name: 'Login',
      query: { redirect: to.fullPath }
    })
  }

  // Check role-based access
  if (to.meta.allowedRoles && userRole) {
    if (!to.meta.allowedRoles.includes(userRole)) {
      // User doesn't have permission, redirect to their dashboard
      const redirectRoute = authStore.getDefaultRouteForRole()
      return next({ name: redirectRoute })
    }
  }

  next()
})

// After navigation hook for analytics/tracking
router.afterEach((to) => {
  // Update page title
  const appName = 'Ihsane'
  document.title = to.meta.title ? `${to.meta.title} | ${appName}` : appName
})

export default router
