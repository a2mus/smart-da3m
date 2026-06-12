<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useMockUiStore, type MockRole } from '@/stores/mockUiStore'

const router = useRouter()
const mockStore = useMockUiStore()

// If already authenticated, redirect to dashboard
if (mockStore.isMockAuthenticated) {
  const redirect = mockStore.activeRoleRedirect
  if (redirect) router.replace({ name: redirect })
}

const roles: { role: MockRole; labelAr: string; labelFr: string; descAr: string; icon: string; gradient: string }[] = [
  {
    role: 'STUDENT',
    labelAr: 'تلميذ',
    labelFr: 'Élève',
    descAr: 'استعرض رحلة التعلم، التشخيصات، ومسارات التقوية',
    icon: 'school',
    gradient: 'from-[#00535b] to-teal-700',
  },
  {
    role: 'PARENT',
    labelAr: 'ولي أمر',
    labelFr: 'Parent',
    descAr: 'تابع تقدم أطفالك، الإشعارات، والتوصيات الذكية',
    icon: 'family_restroom',
    gradient: 'from-[#8c4e35] to-amber-800',
  },
  {
    role: 'EXPERT',
    labelAr: 'خبير بيداغوجي',
    labelFr: 'Expert Pédagogique',
    descAr: 'أدر المحتوى التعليمي، حلل النتائج، وأدر المجموعات',
    icon: 'psychology',
    gradient: 'from-[#2e5a3b] to-emerald-800',
  },
]

function handleSelectRole(role: MockRole) {
  const routeName = mockStore.selectRole(role)
  router.push({ name: routeName })
}
</script>

<template>
  <div
    dir="rtl"
    class="min-h-screen flex items-center justify-center bg-[#faf9f6] dark:bg-slate-950 px-4 py-12"
  >
    <div class="w-full max-w-4xl">
      <!-- Header -->
      <div class="text-center mb-12">
        <div class="flex items-center justify-center gap-3 mb-6">
          <span
            class="material-symbols-outlined text-5xl text-[#00535b] dark:text-teal-400"
            data-icon="menu_book"
          >
            menu_book
          </span>
          <h1 class="text-5xl font-black text-[#00535b] dark:text-teal-500">
            إحسان
          </h1>
        </div>
        <h2 class="text-2xl font-bold text-on-surface mb-3">
          اختر طريقة العرض
        </h2>
        <p class="text-on-surface-variant text-lg max-w-lg mx-auto">
          هذه نسخة تجريبية للمعاينة. اختر دوراً لاستعراض المنصة من وجهة نظر مختلفة.
        </p>
      </div>

      <!-- Role Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <button
          v-for="r in roles"
          :key="r.role"
          class="group relative bg-surface-container rounded-[2rem_1rem_2rem_1rem] p-8 text-center cursor-pointer
                 border-2 border-surface-container-highest hover:border-primary/30
                 shadow-lg shadow-teal-900/5 hover:shadow-xl hover:shadow-teal-900/10
                 transition-all duration-300 hover:-translate-y-1 active:scale-[0.98]"
          @click="handleSelectRole(r.role)"
        >
          <!-- Icon circle -->
          <div
            :class="`w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br ${r.gradient} flex items-center justify-center shadow-lg`"
          >
            <span
              class="material-symbols-outlined text-4xl text-on-primary"
              :data-icon="r.icon"
            >
              {{ r.icon }}
            </span>
          </div>
          <!-- Label -->
          <h3 class="text-xl font-bold text-on-surface mb-2">
            {{ r.labelAr }}
          </h3>
          <p class="text-sm text-on-surface-variant/70 font-medium mb-2">
            {{ r.labelFr }}
          </p>
          <!-- Description -->
          <p class="text-sm text-on-surface-variant leading-relaxed">
            {{ r.descAr }}
          </p>
          <!-- Arrow indicator -->
          <div
            class="mt-6 inline-flex items-center justify-center w-10 h-10 rounded-full
                   bg-primary/10 text-primary group-hover:bg-primary group-hover:text-on-primary
                   transition-all duration-300"
          >
            <span
              class="material-symbols-outlined text-xl"
              data-icon="arrow_forward"
            >arrow_forward</span>
          </div>
        </button>
      </div>

      <!-- Footer note -->
      <p class="text-center text-xs text-on-surface-variant/50 mt-10">
        معاينة تجريبية — لا تمثل جلسة حقيقية • Experimental Preview
      </p>
    </div>
  </div>
</template>
