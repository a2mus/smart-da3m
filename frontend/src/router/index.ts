import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
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
  // ── Public Routes ──
  {
    path: '/',
    name: 'LandingPage',
    component: () => import('@/views/LandingPage.vue'),
    meta: { public: true, guestOnly: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true, guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { public: true, guestOnly: true }
  },
  // ── Student Routes ──
  {
    path: '/student',
    name: 'StudentDashboard',
    component: () => import('@/views/student/Dashboard.vue'),
    meta: { requiresAuth: true, allowedRoles: ['STUDENT'] }
  },
  {
    path: '/student/diagnostic/:moduleId',
    name: 'DiagnosticSession',
    component: () => import('@/views/student/DiagnosticSession.vue'),
    meta: { requiresAuth: true, allowedRoles: ['STUDENT'] }
  },
  {
    path: '/student/remediation/:competencyId',
    name: 'RemediationSession',
    component: () => import('@/views/student/RemediationExecutionView.vue'),
    meta: { requiresAuth: true, allowedRoles: ['STUDENT'] }
  },
  // ── Parent Routes ──
  {
    path: '/parent',
    name: 'ParentDashboard',
    component: () => import('@/views/parent/Dashboard.vue'),
    meta: { requiresAuth: true, allowedRoles: ['PARENT'] }
  },
  {
    path: '/parent/analytics',
    name: 'ParentAnalytics',
    component: () => import('@/views/parent/Analytics.vue'),
    meta: { requiresAuth: true, allowedRoles: ['PARENT'] }
  },
  {
    path: '/parent/alerts',
    name: 'ParentAlerts',
    component: () => import('@/views/parent/Alerts.vue'),
    meta: { requiresAuth: true, allowedRoles: ['PARENT'] }
  },
  // ── Expert Routes ──
  {
    path: '/expert',
    name: 'ExpertDashboard',
    component: () => import('@/views/expert/Dashboard.vue'),
    meta: { requiresAuth: true, allowedRoles: ['EXPERT'] }
  },
  {
    path: '/expert/validation',
    name: 'ValidationQueue',
    component: () => import('@/views/expert/ValidationQueueView.vue'),
    meta: { requiresAuth: true, allowedRoles: ['EXPERT'] }
  },
  {
    path: '/expert/modules',
    name: 'ModuleList',
    component: () => import('@/views/expert/ModuleList.vue'),
    meta: { requiresAuth: true, allowedRoles: ['EXPERT'] }
  },
  {
    path: '/expert/modules/:id/edit',
    name: 'ModuleEditor',
    component: () => import('@/views/expert/ModuleEditor.vue'),
    meta: { requiresAuth: true, allowedRoles: ['EXPERT'] }
  },
  {
    path: '/expert/modules/:id/questions',
    name: 'ModuleQuestions',
    component: () => import('@/views/expert/ModuleList.vue'),
    meta: { requiresAuth: true, allowedRoles: ['EXPERT'] }
  },
  {
    path: '/expert/analytics',
    name: 'ExpertAnalytics',
    component: () => import('@/views/expert/Analytics.vue'),
    meta: { requiresAuth: true, allowedRoles: ['EXPERT'] }
  },
  // ── 404 ──
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
    return { top: 0 }
  }
})

let authInitialized = false

router.beforeEach(async (
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  const authStore = useAuthStore()

  if (!authInitialized) {
    await authStore.initAuth()
    authInitialized = true
  }

  const isAuthenticated = authStore.isAuthenticated
  const userRole = authStore.userRole
  // ── Guest-only routes: redirect authenticated users to their dashboard ──
  if (to.meta.guestOnly && isAuthenticated) {
    const redirectRoute = authStore.getDefaultRouteForRole()
    return next({ name: redirectRoute })
  }

  // ── Public routes: allow all ──
  if (to.meta.public) {
    return next()
  }

  // ── Protected routes ──
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }

  // ── Role-based access ──
  if (to.meta.allowedRoles && userRole) {
    if (!to.meta.allowedRoles.includes(userRole)) {
      const redirectRoute = authStore.getDefaultRouteForRole()
      return next({ name: redirectRoute })
    }
  }

  next()
})

router.afterEach((to) => {
  const appName = 'Ihsane'
  document.title = to.meta.title ? `${to.meta.title} | ${appName}` : appName
})

export default router
