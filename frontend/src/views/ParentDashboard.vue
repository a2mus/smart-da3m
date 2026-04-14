<script setup lang="ts">
import ParentNotificationsList from '@/components/parent/ParentNotificationsList.vue'
import { useRouter } from 'vue-router'
import { mockUiState } from '@/services/mockUiState';

const router = useRouter()

const goToAnalytics = () => {
  router.push('/parent/analytics')
}
</script>

<template>
  <div
    class="bg-background text-on-surface mb-24 min-h-screen"
    dir="rtl"
  >
    <!-- TopAppBar -->
    <header class="fixed top-0 w-full z-50 bg-[#faf9f6]/80 dark:bg-stone-900/80 backdrop-blur-xl">
      <div class="flex flex-row-reverse justify-between items-center w-full px-6 py-4">
        <div class="flex items-center gap-3">
          <div class="text-end">
            <p class="text-xs text-stone-500 font-medium leading-none">
              مرحباً بوليّ أمر
            </p>
            <h2 class="text-primary font-bold text-lg">
              أحمد
            </h2>
          </div>
          <div class="w-12 h-12 rounded-2xl bg-primary-fixed overflow-hidden ring-4 ring-primary/5">
            <img
              alt="أحمد"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuDN1A1ACgKMLdwtl3eZxJuuks3EhV7uvW0a7TudvfNjviZtI-RptKKdG6MPE-XwQoXYDmRQSFIQV_UpJpIEUrwWPR-kEkL50Q-QM9YICJZcZai2aC_5XfDnA2XABXUNm3CVi6XYMyR85TMFNsvKY59NeQBSUay90oOtLdMotlpjEd6S8iEWN2Hghtvekr_XUcTXhEKnbRfQH9TBwrL6jlligISAxtooVFd-awMn3dNwPpywDeAu8xVdxd42KFYoq4mpwRKGFEm5nbg"
            >
          </div>
        </div>
        <div
          class="flex items-center gap-4 cursor-pointer"
          @click="router.push('/')"
        >
          <div class="text-2xl font-black text-[#00535b] dark:text-[#006D77] font-['Plus_Jakarta_Sans','Tajawal']">
            إحسان
          </div>
          <button class="material-symbols-outlined text-primary text-2xl transition-all duration-300 active:scale-95">
            swap_horiz
          </button>
        </div>
      </div>
    </header>

    <main class="pt-24 px-6 space-y-8 max-w-lg mx-auto">
      <!-- Smart Message Card (Insight) -->
      <section class="relative">
        <div class="bg-surface-container-lowest p-6 asymmetric-border border-e-4 border-secondary shadow-[0_10px_30px_rgba(140,78,53,0.08)]">
          <div class="flex items-start gap-4">
            <div class="bg-secondary-fixed p-3 rounded-2xl">
              <span
                class="material-symbols-outlined text-secondary"
                style="font-variation-settings: 'FILL' 1;"
              >auto_awesome</span>
            </div>
            <div>
              <h3 class="text-secondary font-bold text-lg mb-1">
                رؤية ذكية
              </h3>
              <p class="text-on-surface-variant leading-relaxed">
                أحمد يتفوق في <span class="font-bold text-primary">المعادلات</span> ولكنه يحتاج للمساعدة في <span class="font-bold text-secondary">الكسور</span>.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Stats Section: Progress Comparison -->
      <section class="space-y-4">
        <div class="flex justify-between items-end">
          <h3 class="text-xl font-bold text-primary">
            نظرة على التقدم
          </h3>
          <span class="text-sm text-stone-500 font-label">أداء هذا الأسبوع</span>
        </div>
        <div class="grid grid-cols-1 gap-6">
          <div
            class="bg-surface-container-low p-5 rounded-3xl space-y-3 cursor-pointer hover:bg-surface-container transition-colors"
            @click="goToAnalytics"
          >
            <div class="flex justify-between items-center">
              <span class="font-bold">الرياضيات: الكسور</span>
              <span class="font-label text-primary font-bold">{{ mockUiState.journey.currentProgressPct }}%</span>
            </div>
            <div class="w-full bg-surface-container-highest rounded-full overflow-hidden h-4">
              <div
                class="h-full bg-primary rounded-full transition-all duration-1000"
                :style="{ width: mockUiState.journey.currentProgressPct + '%' }"
              />
            </div>
            <p class="text-xs text-stone-500 italic">
              انقر لرؤية التحليلات المعمقة
            </p>
          </div>
        </div>
      </section>

      <!-- Recommendation Card -->
      <section>
        <div class="bg-primary p-6 rounded-[2.5rem] text-on-primary relative overflow-hidden group">
          <div class="absolute -top-12 -start-12 w-32 h-32 bg-primary-container rounded-full opacity-20" />
          <div class="absolute -bottom-8 -end-8 w-24 h-24 bg-secondary rounded-full opacity-10" />
          
          <div class="relative z-10 flex flex-col gap-4">
            <div class="flex items-center gap-3">
              <span class="material-symbols-outlined bg-surface-bright/20 p-2 rounded-xl">lightbulb</span>
              <h4 class="font-bold text-lg">
                توصية اليوم
              </h4>
            </div>
            <p class="text-primary-fixed text-xl font-bold leading-snug">
              5 دقائق من تمرين الكسور
            </p>
            <button
              class="bg-secondary text-on-primary px-6 py-3 rounded-2xl font-bold self-start mt-2 shadow-lg shadow-secondary/20 active:scale-95 transition-transform"
              @click="router.push('/student/journey')"
            >
              ابدأ رحلة التلميذ
            </button>
          </div>
        </div>
      </section>

      <!-- Recent Activities via new Component -->
      <ParentNotificationsList />
    </main>

    <!-- BottomNavBar -->
    <nav class="fixed bottom-0 start-0 w-full flex flex-row-reverse justify-around items-center px-4 pb-6 pt-3 bg-[#faf9f6]/80 dark:bg-stone-900/80 backdrop-blur-xl z-50 rounded-t-3xl shadow-[0_-4px_40px_rgba(0,109,119,0.06)] max-w-lg mx-auto end-0">
      <a
        class="flex flex-col items-center justify-center bg-[#00535b]/10 dark:bg-[#006D77]/20 text-[#00535b] dark:text-[#006D77] rounded-2xl px-5 py-2 scale-110 transition-transform duration-200"
        href="#"
      >
        <span
          class="material-symbols-outlined"
          style="font-variation-settings: 'FILL' 1;"
        >home</span>
        <span class="font-['Plus_Jakarta_Sans','Tajawal'] text-[12px] font-bold font-body">الرئيسية</span>
      </a>
      <a
        class="flex flex-col items-center justify-center text-stone-400 dark:text-stone-500 px-5 py-2 hover:bg-[#f4f3f1] dark:hover:bg-stone-800 transition-colors cursor-pointer"
        @click="goToAnalytics"
      >
        <span class="material-symbols-outlined">insights</span>
        <span class="font-['Plus_Jakarta_Sans','Tajawal'] text-[12px] font-medium font-body">التقدم</span>
      </a>
      <a
        class="flex flex-col items-center justify-center text-stone-400 dark:text-stone-500 px-5 py-2 hover:bg-[#f4f3f1] dark:hover:bg-stone-800 transition-colors"
        href="#"
      >
        <span class="material-symbols-outlined">auto_awesome</span>
        <span class="font-['Plus_Jakarta_Sans','Tajawal'] text-[12px] font-medium font-body">التوصيات</span>
      </a>
      <a
        class="flex flex-col items-center justify-center text-stone-400 dark:text-stone-500 px-5 py-2 hover:bg-[#f4f3f1] dark:hover:bg-stone-800 transition-colors"
        href="#"
      >
        <span class="material-symbols-outlined">person</span>
        <span class="font-['Plus_Jakarta_Sans','Tajawal'] text-[12px] font-medium font-body">الحساب</span>
      </a>
    </nav>
  </div>
</template>

<style scoped>
.asymmetric-border {
  border-radius: 2rem 1rem 3rem 1rem;
}
</style>
