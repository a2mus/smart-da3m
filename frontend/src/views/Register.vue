<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const selectedRole = ref<'PARENT' | 'EXPERT' | null>(null)
const name = ref('')
const email = ref('')
const password = ref('')
const language = ref<'AR' | 'FR'>('AR')
const error = ref<string | null>(null)
const success = ref(false)
const isLoading = ref(false)

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
    error.value = 'يرجى إدخال البريد الإلكتروني وكلمة المرور'
    return
  }

  if (password.value.length < 8) {
    error.value = 'يجب أن تتكون كلمة المرور من 8 أحرف على الأقل'
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
      router.push('/parent/dashboard')
    } else {
      error.value = authStore.error || 'فشلت عملية التسجيل. يرجى المحاولة مرة أخرى.'
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'فشلت عملية التسجيل. يرجى المحاولة مرة أخرى.'
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
          {{ selectedRole ? 'إنشاء حساب جديد' : 'انضم إلينا' }}
        </h2>
        <p class="text-on-surface-variant mt-1">
          {{ selectedRole ? '' : 'اختر نوع الحساب للمتابعة' }}
        </p>
      </div>

      <!-- Role Picker (shown when no role selected) -->
      <div
        v-if="!selectedRole"
        class="bg-surface-container rounded-[2rem] p-8 shadow-lg space-y-4"
      >
        <button
          class="w-full text-end p-6 bg-surface-container-lowest hover:bg-primary/5 border-2 border-outline-variant hover:border-primary rounded-2xl transition-all flex flex-row-reverse justify-between items-center group"
          @click="selectRole('PARENT')"
        >
          <span class="material-symbols-outlined text-4xl text-primary group-hover:scale-110 transition-transform">family_restroom</span>
          <div class="flex-1 me-4">
            <h4 class="text-xl font-bold text-on-surface">
              تسجيل كولي أمر
            </h4>
            <p class="text-sm text-on-surface-variant">
              لمتابعة مستوى طفلك وتلقي تقارير ذكية
            </p>
          </div>
        </button>

        <button
          class="w-full text-end p-6 bg-surface-container-lowest hover:bg-primary/5 border-2 border-outline-variant hover:border-primary rounded-2xl transition-all flex flex-row-reverse justify-between items-center group"
          @click="selectRole('EXPERT')"
        >
          <span class="material-symbols-outlined text-4xl text-primary group-hover:scale-110 transition-transform">school</span>
          <div class="flex-1 me-4">
            <h4 class="text-xl font-bold text-on-surface">
              تسجيل كخبير بيداغوجي
            </h4>
            <p class="text-sm text-on-surface-variant">
              للمساهمة في المناهج وتحليل البيانات
            </p>
          </div>
        </button>

        <p class="text-center text-sm text-on-surface-variant mt-6">
          لديك حساب بالفعل؟
          <router-link
            to="/login"
            class="text-primary font-bold hover:underline"
          >
            تسجيل الدخول
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
          <span class="text-sm">تغيير الاختيار</span>
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
              تم إنشاء الحساب بنجاح!
            </h3>
            <p class="text-on-surface-variant">
              مرحباً بك في منصة إحسان. يمكنك الآن تسجيل الدخول للبدء في تخصيص مسار طفلك.
            </p>
          </div>
          <router-link
            to="/login"
            class="block w-full bg-primary text-on-primary py-3.5 rounded-xl font-bold text-lg text-center
                   hover:bg-primary/90 active:scale-[0.98] transition-all"
          >
            تسجيل الدخول الآن
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
              حساب الخبراء محمي
            </h3>
            <p class="text-on-surface-variant leading-relaxed">
              يتم إنشاء حسابات الخبراء البيداغوجيين من قِبل إدارة المنصة للحفاظ على جودة المحتوى التعليمي.
              إذا تم تسجيلك مسبقاً، يرجى التوجه لصفحة تسجيل الدخول.
            </p>
          </div>
          <router-link
            to="/login"
            class="block w-full bg-primary text-on-primary py-3.5 rounded-xl font-bold text-lg text-center
                   hover:bg-primary/90 active:scale-[0.98] transition-all"
          >
            الانتقال لتسجيل الدخول
          </router-link>
        </div>

        <!-- Parent Registration form -->
        <form
          v-else
          class="space-y-4"
          @submit.prevent="handleRegister"
        >
          <h3 class="text-xl font-bold text-on-surface mb-6 text-center">
            حساب ولي أمر جديد
          </h3>

          <div>
            <label class="block text-sm font-medium text-on-surface-variant mb-1">الاسم الكامل (اختياري)</label>
            <input
              v-model="name"
              type="text"
              class="w-full px-4 py-3 rounded-xl border-2 border-outline-variant bg-surface-container-lowest
                     text-on-surface placeholder:text-on-surface-variant/40
                     focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all
                     font-['Inter','Tajawal'] text-start"
              placeholder="مثال: أحمد محمد"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-on-surface-variant mb-1">البريد الإلكتروني</label>
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
            <label class="block text-sm font-medium text-on-surface-variant mb-1">كلمة المرور (8 أحرف كحد أدنى)</label>
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
            <label class="block text-sm font-medium text-on-surface-variant mb-2">لغة الواجهة المفضلة</label>
            <div class="grid grid-cols-2 gap-3">
              <button
                type="button"
                :class="[
                  'py-3 rounded-xl border-2 font-bold transition-all',
                  language === 'AR'
                    ? 'border-primary bg-primary/5 text-primary'
                    : 'border-outline-variant text-on-surface-variant hover:bg-surface-container-highest'
                ]"
                @click="language = 'AR'"
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
                @click="language = 'FR'"
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
              جاري إنشاء الحساب...
            </span>
            <span v-else>إنشاء الحساب</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
