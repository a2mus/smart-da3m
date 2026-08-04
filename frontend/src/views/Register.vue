<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'

const { t, locale } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const selectedRole = ref<'PARENT' | 'EXPERT' | null>(null)
const name = ref('')
const email = ref('')
const password = ref('')
const language = ref<'AR' | 'FR'>(locale.value.toUpperCase() === 'FR' ? 'FR' : 'AR')
const error = ref<string | null>(null)
const success = ref(false)
const isLoading = ref(false)

function setLanguage(lang: 'AR' | 'FR') {
  language.value = lang
  locale.value = lang.toLowerCase()
}

function selectRole(role: 'PARENT' | 'EXPERT') {
  selectedRole.value = role
  error.value = null
  success.value = false
}

function backToRoles() {
  selectedRole.value = null
  error.value = null
  success.value = false
}

async function handleRegister() {
  if (selectedRole.value !== 'PARENT') return

  if (!email.value || !password.value) {
    error.value = t('auth.emailAndPasswordRequired', 'يرجى إدخال البريد الإلكتروني وكلمة المرور')
    return
  }

  if (password.value.length < 8) {
    error.value = t('auth.passwordMinLength', 'يجب أن تتكون كلمة المرور من 8 أحرف على الأقل')
    return
  }

  isLoading.value = true
  error.value = null
  try {
    const loggedIn = await authStore.registerParent(
      email.value,
      password.value,
      language.value,
      name.value.trim() || undefined
    )
    if (loggedIn) {
      router.push('/parent')
    } else {
      error.value = authStore.error || t('auth.registrationFailed', 'فشلت عملية التسجيل. يرجى المحاولة مرة أخرى.')
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || t('auth.registrationFailed', 'فشلت عملية التسجيل. يرجى المحاولة مرة أخرى.')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-[#faf9f6] dark:bg-slate-950 px-4 py-12">
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
            {{ t('app.name') }}
          </h1>
        </div>
        <h2 class="text-2xl font-bold text-on-surface">
          {{ selectedRole ? t('auth.registerTitle') : t('auth.joinUs') }}
        </h2>
        <p class="text-on-surface-variant mt-1">
          {{ selectedRole ? '' : t('auth.selectAccountType') }}
        </p>
      </div>

      <!-- Role Picker (shown when no role selected) -->
      <div
        v-if="!selectedRole"
        class="bg-surface-container rounded-[2rem] p-8 shadow-lg space-y-4"
      >
        <button
          class="w-full text-start p-6 bg-surface-container-lowest hover:bg-primary/5 border-2 border-outline-variant hover:border-primary rounded-2xl transition-all flex items-center justify-between group"
          @click="selectRole('PARENT')"
        >
          <div class="flex items-center gap-4">
            <span class="material-symbols-outlined text-4xl text-primary group-hover:scale-110 transition-transform">family_restroom</span>
            <div>
              <h4 class="text-xl font-bold text-on-surface">
                {{ t('auth.registerParent') }}
              </h4>
              <p class="text-sm text-on-surface-variant">
                {{ t('auth.registerParentDesc') }}
              </p>
            </div>
          </div>
        </button>

        <button
          class="w-full text-start p-6 bg-surface-container-lowest hover:bg-primary/5 border-2 border-outline-variant hover:border-primary rounded-2xl transition-all flex items-center justify-between group"
          @click="selectRole('EXPERT')"
        >
          <div class="flex items-center gap-4">
            <span class="material-symbols-outlined text-4xl text-primary group-hover:scale-110 transition-transform">school</span>
            <div>
              <h4 class="text-xl font-bold text-on-surface">
                {{ t('auth.registerExpert') }}
              </h4>
              <p class="text-sm text-on-surface-variant">
                {{ t('auth.registerExpertDesc') }}
              </p>
            </div>
          </div>
        </button>

        <p class="text-center text-sm text-on-surface-variant mt-6">
          {{ t('auth.alreadyHaveAccount') }}
          <router-link
            to="/login"
            class="text-primary font-bold hover:underline"
          >
            {{ t('auth.login') }}
          </router-link>
        </p>
      </div>

      <!-- Registration forms/messages -->
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
          <span class="text-sm">{{ t('auth.changeSelection') }}</span>
        </button>

        <!-- Success view -->
        <div
          v-if="success"
          class="text-center py-6 space-y-6"
        >
          <div class="w-16 h-16 bg-success/10 text-success rounded-full flex items-center justify-center mx-auto text-4xl">
            <span class="material-symbols-outlined text-4xl">check_circle</span>
          </div>
          <div>
            <h3 class="text-2xl font-bold text-on-surface mb-2">
              {{ t('auth.accountCreatedSuccess') }}
            </h3>
            <p class="text-on-surface-variant">
              {{ t('auth.accountCreatedMsg') }}
            </p>
          </div>
          <router-link
            to="/login"
            class="block w-full bg-primary text-on-primary py-3.5 rounded-xl font-bold text-lg text-center
                   hover:bg-primary/90 active:scale-[0.98] transition-all"
          >
            {{ t('auth.loginNow') }}
          </router-link>
        </div>

        <!-- Expert message view -->
        <div
          v-else-if="selectedRole === 'EXPERT'"
          class="text-center py-6 space-y-6"
        >
          <div class="w-16 h-16 bg-primary/10 text-primary rounded-full flex items-center justify-center mx-auto text-4xl">
            <span class="material-symbols-outlined text-4xl">admin_panel_settings</span>
          </div>
          <div>
            <h3 class="text-2xl font-bold text-on-surface mb-2">
              {{ t('auth.expertAccountProtected') }}
            </h3>
            <p class="text-on-surface-variant leading-relaxed">
              {{ t('auth.expertAccountMsg') }}
            </p>
          </div>
          <router-link
            to="/login"
            class="block w-full bg-primary text-on-primary py-3.5 rounded-xl font-bold text-lg text-center
                   hover:bg-primary/90 active:scale-[0.98] transition-all"
          >
            {{ t('auth.goToLogin') }}
          </router-link>
        </div>

        <!-- Parent Registration form -->
        <form
          v-else
          class="space-y-4"
          @submit.prevent="handleRegister"
        >
          <h3 class="text-xl font-bold text-on-surface mb-6 text-center">
            {{ t('auth.newParentAccount') }}
          </h3>

          <div>
            <label class="block text-sm font-medium text-on-surface-variant mb-1">{{ t('auth.fullNameOptional') }}</label>
            <input
              v-model="name"
              type="text"
              class="w-full px-4 py-3 rounded-xl border-2 border-outline-variant bg-surface-container-lowest
                     text-on-surface placeholder:text-on-surface-variant/40
                     focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all
                     font-['Inter','Tajawal'] text-start"
              :placeholder="t('auth.fullNamePlaceholder')"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-on-surface-variant mb-1">{{ t('auth.email') }}</label>
            <input
              v-model="email"
              type="email"
              dir="ltr"
              required
              class="w-full px-4 py-3 rounded-xl border-2 border-outline-variant bg-surface-container-lowest
                     text-on-surface placeholder:text-on-surface-variant/40
                     focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all
                     font-['Inter','Tajawal'] text-start"
              placeholder="email@example.com"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-on-surface-variant mb-1">{{ t('auth.password') }}</label>
            <input
              v-model="password"
              type="password"
              dir="ltr"
              required
              class="w-full px-4 py-3 rounded-xl border-2 border-outline-variant bg-surface-container-lowest
                     text-on-surface placeholder:text-on-surface-variant/40
                     focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all
                     font-['Inter','Tajawal'] text-start"
              placeholder="••••••••"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-on-surface-variant mb-2">{{ t('auth.preferredLanguage') }}</label>
            <div class="grid grid-cols-2 gap-3">
              <button
                type="button"
                :class="[
                  'py-3 rounded-xl border-2 font-bold transition-all',
                  language === 'AR'
                    ? 'border-primary bg-primary/5 text-primary'
                    : 'border-outline-variant text-on-surface-variant hover:bg-surface-container-highest'
                ]"
                @click="setLanguage('AR')"
              >
                العربية (RTL)
              </button>
              <button
                type="button"
                :class="[
                  'py-3 rounded-xl border-2 font-bold transition-all',
                  language === 'FR'
                    ? 'border-primary bg-primary/5 text-primary'
                    : 'border-outline-variant text-on-surface-variant hover:bg-surface-container-highest'
                ]"
                @click="setLanguage('FR')"
              >
                Français (LTR)
              </button>
            </div>
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
              {{ t('auth.creatingAccount') }}
            </span>
            <span v-else>{{ t('auth.createAccount') }}</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
