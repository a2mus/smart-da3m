<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { UserRole } from '@/types/auth'
import RolePicker from '@/components/common/RolePicker.vue'
import PinInput from '@/components/common/PinInput.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const selectedRole = ref<UserRole | null>(null)
const email = ref('')
const password = ref('')
const parentEmail = ref('')
const pinCode = ref('')
const error = ref<string | null>(null)
const isLoading = ref(false)

const redirectPath = computed(() => (route.query.redirect as string) || null)

function selectRole(role: UserRole) {
  selectedRole.value = role
  error.value = null
}

function backToRoles() {
  selectedRole.value = null
  error.value = null
}

async function handleEmailLogin() {
  if (!email.value || !password.value) {
    error.value = 'يرجى إدخال البريد الإلكتروني وكلمة المرور'
    return
  }
  isLoading.value = true
  error.value = null
  try {
    const success = await authStore.loginWithEmail(email.value, password.value)
    if (success) {
      const target = redirectPath.value || { name: authStore.getDefaultRouteForRole() }
      router.push(target)
    } else {
      error.value = authStore.error || 'فشل تسجيل الدخول'
    }
  } finally {
    isLoading.value = false
  }
}

async function handlePinLogin() {
  if (!parentEmail.value || pinCode.value.length < 4) {
    error.value = 'يرجى إدخال البريد الإلكتروني للولي والرمز السري'
    return
  }
  isLoading.value = true
  error.value = null
  try {
    const success = await authStore.loginWithPin(parentEmail.value, pinCode.value)
    if (success) {
      const target = redirectPath.value || { name: 'StudentDashboard' }
      router.push(target)
    } else {
      error.value = authStore.error || 'الرمز السري غير صحيح'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div
    dir="rtl"
    class="min-h-screen flex items-center justify-center bg-[#faf9f6] dark:bg-slate-950 px-4 py-12"
  >
    <div class="w-full max-w-lg">
      <!-- Header -->
      <div class="text-center mb-10">
        <div
          class="flex items-center justify-center gap-3 mb-4 cursor-pointer"
          @click="router.push('/')"
        >
          <span
            class="material-symbols-outlined text-4xl text-[#00535b] dark:text-teal-400"
            data-icon="menu_book"
          >
            menu_book
          </span>
          <h1 class="text-3xl font-black text-[#00535b] dark:text-teal-500">
            إحسان
          </h1>
        </div>
        <h2 class="text-2xl font-bold text-on-surface">
          {{ selectedRole ? 'تسجيل الدخول' : 'مرحباً بعودتك' }}
        </h2>
        <p class="text-on-surface-variant mt-1">
          {{ selectedRole ? '' : 'اختر دورك للمتابعة' }}
        </p>
      </div>

      <!-- Role Picker (shown when no role selected) -->
      <div
        v-if="!selectedRole"
        class="bg-surface-container rounded-[2rem] p-8 shadow-lg"
      >
        <RolePicker @select="selectRole" />
      </div>

      <!-- Role-specific form -->
      <div
        v-else
        class="bg-surface-container rounded-[2rem] p-8 shadow-lg"
      >
        <!-- Back button -->
        <button
          class="flex items-center gap-1 text-on-surface-variant hover:text-primary mb-6 transition-colors"
          @click="backToRoles"
        >
          <span class="material-symbols-outlined text-lg">arrow_back</span>
          <span class="text-sm">تغيير الدور</span>
        </button>

        <h3 class="text-xl font-bold text-on-surface mb-6 text-center">
          {{ selectedRole === 'STUDENT' ? 'تسجيل دخول التلميذ' : selectedRole === 'PARENT' ? 'تسجيل دخول ولي الأمر' : 'تسجيل دخول الخبير' }}
        </h3>

        <!-- Parent / Expert: Email + Password -->
        <form
          v-if="selectedRole !== 'STUDENT'"
          class="space-y-4"
          @submit.prevent="handleEmailLogin"
        >
          <div>
            <label class="block text-sm font-medium text-on-surface-variant mb-1">البريد الإلكتروني</label>
            <input
              v-model="email"
              type="email"
              dir="ltr"
              class="w-full px-4 py-3 rounded-xl border-2 border-outline-variant bg-surface-container-lowest
                     text-on-surface placeholder:text-on-surface-variant/40
                     focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all
                     font-['Inter','Tajawal'] text-start"
              placeholder="email@example.com"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-on-surface-variant mb-1">كلمة المرور</label>
            <input
              v-model="password"
              type="password"
              dir="ltr"
              class="w-full px-4 py-3 rounded-xl border-2 border-outline-variant bg-surface-container-lowest
                     text-on-surface placeholder:text-on-surface-variant/40
                     focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all
                     font-['Inter','Tajawal'] text-start"
              placeholder="••••••••"
            >
          </div>

          <!-- Error message -->
          <div
            v-if="error"
            class="bg-error/10 text-error rounded-xl px-4 py-3 text-sm font-medium text-center"
          >
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="w-full bg-primary text-on-primary py-3.5 rounded-xl font-bold text-lg
                   hover:bg-primary/90 active:scale-[0.98] transition-all
                   disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span
              v-if="isLoading"
              class="inline-flex items-center gap-2"
            >
              <span class="animate-spin material-symbols-outlined text-lg">progress_activity</span>
              جاري الدخول...
            </span>
            <span v-else>تسجيل الدخول</span>
          </button>

          <!-- Social login -->
          <div class="relative my-6">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-outline-variant" />
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-4 bg-surface-container text-on-surface-variant">أو</span>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <button
              type="button"
              class="flex items-center justify-center gap-2 px-4 py-3 rounded-xl border-2 border-outline-variant
                     text-on-surface font-medium hover:bg-surface-container-highest transition-all"
            >
              <span class="font-bold text-[#4285F4]">G</span> Google
            </button>
            <button
              type="button"
              class="flex items-center justify-center gap-2 px-4 py-3 rounded-xl border-2 border-outline-variant
                     text-on-surface font-medium hover:bg-surface-container-highest transition-all"
            >
              <span class="font-bold text-[#1877F2]">f</span> Facebook
            </button>
          </div>
        </form>

        <!-- Student: Parent Email + PIN -->
        <form
          v-else
          class="space-y-6"
          @submit.prevent="handlePinLogin"
        >
          <div>
            <label class="block text-sm font-medium text-on-surface-variant mb-1">البريد الإلكتروني لولي الأمر</label>
            <input
              v-model="parentEmail"
              type="email"
              dir="ltr"
              class="w-full px-4 py-3 rounded-xl border-2 border-outline-variant bg-surface-container-lowest
                     text-on-surface placeholder:text-on-surface-variant/40
                     focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all
                     font-['Inter','Tajawal'] text-start"
              placeholder="parent@example.com"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-on-surface-variant mb-3 text-center">الرمز السري (٤-٦ أرقام)</label>
            <PinInput
              v-model="pinCode"
              :length="6"
            />
          </div>

          <!-- Error message -->
          <div
            v-if="error"
            class="bg-error/10 text-error rounded-xl px-4 py-3 text-sm font-medium text-center"
          >
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="isLoading || pinCode.length < 4"
            class="w-full bg-primary text-on-primary py-3.5 rounded-xl font-bold text-lg
                   hover:bg-primary/90 active:scale-[0.98] transition-all
                   disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span
              v-if="isLoading"
              class="inline-flex items-center gap-2"
            >
              <span class="animate-spin material-symbols-outlined text-lg">progress_activity</span>
              جاري الدخول...
            </span>
            <span v-else>دخول</span>
          </button>
        </form>

        <!-- Register link (Parent/Expert only) -->
        <p
          v-if="selectedRole !== 'STUDENT'"
          class="text-center text-sm text-on-surface-variant mt-6"
        >
          ليس لديك حساب؟
          <router-link
            to="/register"
            class="text-primary font-bold hover:underline"
          >
            سجل الآن
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>
