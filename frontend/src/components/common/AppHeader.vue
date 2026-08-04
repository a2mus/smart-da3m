<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import LanguageToggle from '@/components/common/LanguageToggle.vue'
import OrgSwitcher from '@/components/common/OrgSwitcher.vue'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()

const roleBadgeKey = computed(() => {
  switch (authStore.userRole) {
    case 'EXPERT':
      return 'roles.expert'
    case 'PARENT':
      return 'roles.parent'
    case 'STUDENT':
      return 'roles.student'
    default:
      return ''
  }
})

const handleLogout = async () => {
  await authStore.logout()
  router.push({ name: 'Login' })
}
</script>

<template>
  <header class="w-full bg-surface-container-lowest border-b border-outline-variant px-4 py-3 sticky top-0 z-40">
    <div class="max-w-7xl mx-auto flex items-center justify-between gap-4">
      <!-- App Brand Logo & Title -->
      <router-link
        to="/"
        class="flex items-center gap-2 font-bold text-xl text-primary focus:outline-none"
      >
        <span class="text-2xl">🎓</span>
        <span>{{ t('app.title', 'إحسان') }}</span>
      </router-link>

      <!-- Header Controls & User Info -->
      <div class="flex items-center gap-3">
        <!-- Tenant Org Switcher -->
        <OrgSwitcher />

        <!-- i18n Language Switcher -->
        <LanguageToggle />

        <!-- User Role Badge & Logout if Authenticated -->
        <div
          v-if="authStore.isAuthenticated"
          class="flex items-center gap-2 ms-2 ps-2 border-s border-outline-variant"
        >
          <span
            v-if="roleBadgeKey"
            class="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-primary-container text-on-primary-container"
          >
            {{ t(roleBadgeKey, authStore.userRole || '') }}
          </span>
          <button
            type="button"
            class="px-3 py-1.5 text-xs font-medium text-error hover:bg-error-container/20 rounded-soft transition-colors focus:outline-none"
            :title="t('auth.logout', 'تسجيل الخروج')"
            @click="handleLogout"
          >
            {{ t('auth.logout', 'تسجيل الخروج') }}
          </button>
        </div>
        <div
          v-else
          class="flex items-center gap-2 ms-2 ps-2 border-s border-outline-variant"
        >
          <router-link
            to="/register"
            class="px-3.5 py-1.5 text-xs font-bold rounded-xl bg-primary text-on-primary hover:bg-primary-container transition-colors"
          >
            {{ t('auth.registerNow', 'سجل الآن') }}
          </router-link>
          <router-link
            to="/login"
            class="px-3.5 py-1.5 text-xs font-bold rounded-xl border border-primary text-primary hover:bg-primary/5 transition-colors"
          >
            {{ t('auth.login', 'تسجيل الدخول') }}
          </router-link>
        </div>
      </div>
    </div>
  </header>
</template>