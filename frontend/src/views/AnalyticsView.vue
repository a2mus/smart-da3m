<script setup lang="ts">
import StudentFocusChart from '@/components/parent/StudentFocusChart.vue'
import { useRouter } from 'vue-router'
import { ref } from 'vue'

const router = useRouter()
const showDrawer = ref(false)

const openDrawer = () => {
    showDrawer.value = true
}

const closeDrawer = () => {
    showDrawer.value = false
}

</script>

<template>
  <div
    class="text-on-surface bg-background min-h-screen relative"
    dir="rtl"
  >
    <!-- TopNavBar -->
    <header class="w-full xl:w-[calc(100%-18rem)] fixed start-0 top-0 z-40 bg-[#faf9f6]/80 dark:bg-slate-950/80 backdrop-blur-2xl flex flex-row-reverse justify-between items-center h-16 px-4 md:px-8">
      <div class="flex items-center gap-4 md:gap-6">
        <div class="relative">
          <span class="material-symbols-outlined text-slate-400 hover:text-[#8c4e35] transition-colors cursor-pointer">notifications</span>
          <span class="absolute top-0 end-0 w-2 h-2 bg-error rounded-full" />
        </div>
        <span
          class="material-symbols-outlined text-slate-400 hover:text-[#8c4e35] transition-colors cursor-pointer"
          @click="router.push('/parent-dashboard')"
        >arrow_forward</span>
      </div>
      <div
        class="flex items-center gap-4 md:gap-8 cursor-pointer"
        @click="router.push('/')"
      >
        <h2 class="text-xl font-black text-[#00535b] dark:text-[#006D77] font-['Cairo']">
          نظام إحسان الذكي
        </h2>
        <nav class="hidden md:flex gap-6">
          <a class="text-[#00535b] dark:text-on-primary font-bold font-['Cairo'] text-sm border-b-2 border-primary pb-1">تحليلات معمقة</a>
        </nav>
      </div>
    </header>

    <!-- Drawer Overlay -->
    <div
      v-if="showDrawer"
      class="fixed inset-0 bg-scrim/50 z-50 xl:hidden backdrop-blur-sm transition-opacity"
      @click="closeDrawer"
    />

    <!-- SideNavBar (Desktop Drawer) -->
    <aside 
      class="h-screen w-72 fixed end-0 top-0 border-s border-outline-variant/20 bg-[#faf9f6]/95 dark:bg-slate-900/95 backdrop-blur-3xl flex flex-col py-8 px-4 z-50 transition-transform duration-300 xl:translate-x-0"
      :class="showDrawer ? 'translate-x-0' : 'translate-x-full'"
    >
      <div class="mb-10 px-4">
        <h1 class="text-2xl font-bold text-[#00535b] dark:text-[#006D77]">
          إحسان للتحليل
        </h1>
        <p class="text-slate-500 text-sm mt-1">
          لوحة تحكم الأولياء
        </p>
      </div>
      <nav class="space-y-2 flex-1">
        <a
          class="flex items-center gap-3 px-4 py-3 text-slate-500 dark:text-slate-400 font-medium hover:bg-[#f4f3f1]/50 transition-colors duration-200 rounded-xl group cursor-pointer"
          @click="router.push('/parent-dashboard')"
        >
          <span class="material-symbols-outlined group-hover:scale-110 transition-transform">dashboard</span>
          <span>الرئيسية</span>
        </a>
        <a class="flex items-center gap-3 px-4 py-3 text-[#00535b] dark:text-[#006D77] font-bold border-e-4 border-[#00535b] bg-[#f4f3f1] dark:bg-slate-800 rounded-s-none rounded-xl cursor-default">
          <span
            class="material-symbols-outlined"
            style="font-variation-settings: 'FILL' 1;"
          >insights</span>
          <span>تحليلات معمقة</span>
        </a>
      </nav>
      <div class="mt-auto flex justify-end px-4">
        <button
          v-if="showDrawer"
          class="text-slate-500 font-bold xl:hidden flex items-center gap-1"
          @click="closeDrawer"
        >
          إغلاق القائمة <span class="material-symbols-outlined">close</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="xl:me-72 pt-24 pb-12 px-4 md:px-8 min-h-screen">
      <!-- Mobile Menu Toggle -->
      <div class="xl:hidden mb-6 flex justify-end">
        <button
          class="bg-surface-container p-2 rounded-xl text-primary font-bold flex items-center gap-2 shadow-sm border border-outline-variant/10"
          @click="openDrawer"
        >
          <span class="material-symbols-outlined">menu</span>
          القائمة
        </button>
      </div>

      <!-- Header Section -->
      <section class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div class="max-w-2xl">
          <span class="bg-secondary-container text-on-secondary-container px-3 py-1 rounded-full text-xs font-bold font-['Inter'] mb-3 inline-block uppercase tracking-wider">Analysis Hub</span>
          <h2 class="text-4xl font-black text-primary leading-tight mb-2">
            تحليل أداء الطالب: أحمد
          </h2>
          <p class="text-on-surface-variant leading-relaxed">
            بناءً على التفاعلات الأخيرة في وحدة الكسور، يستمر أحمد في إظهار تقدم، مع بعض التشتت الطفيف الملحوظ.
          </p>
        </div>
      </section>

      <!-- KPI Bento Grid -->
      <div class="grid grid-cols-12 gap-6 mb-12">
        <!-- Student Focus Chart Component -->
        <div class="col-span-12 md:col-span-4 h-full min-h-[220px]">
          <StudentFocusChart />
        </div>

        <!-- Risk Factor / Progress Card -->
        <div class="col-span-12 md:col-span-8 bg-primary text-on-primary p-8 rounded-[2rem] relative overflow-hidden h-full flex flex-col justify-center">
          <div class="relative z-10 grid grid-cols-1 sm:grid-cols-2 gap-8">
            <div class="flex flex-col justify-center">
              <h4 class="text-2xl font-bold mb-2">
                استيعاب الكسور
              </h4>
              <p class="text-primary-fixed/70 text-sm">
                مستوى التقدم الكلي في الوحدة مميز.
              </p>
              
              <div class="flex gap-8 mt-6">
                <div>
                  <p class="text-primary-fixed/60 text-xs uppercase tracking-widest font-['Inter'] mb-1">
                    Time Studied
                  </p>
                  <p class="text-2xl font-black font-['Inter']">
                    185m
                  </p>
                </div>
                <div>
                  <p class="text-primary-fixed/60 text-xs uppercase tracking-widest font-['Inter'] mb-1">
                    Avg Score
                  </p>
                  <p class="text-2xl font-black font-['Inter']">
                    92
                  </p>
                </div>
              </div>
            </div>
            
            <div class="flex items-center justify-center sm:justify-end">
              <div class="w-32 h-32 rounded-full border-[12px] border-primary-container flex items-center justify-center relative">
                <svg class="absolute inset-0 w-full h-full -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r="52"
                    fill="transparent"
                    stroke="#82d3de"
                    stroke-width="12"
                    stroke-dasharray="326"
                    stroke-dashoffset="114"
                    stroke-linecap="round"
                  />
                </svg>
                <span class="text-2xl font-black font-['Inter']">65%</span>
              </div>
            </div>
          </div>
          <div class="absolute -end-12 -top-12 w-48 h-48 bg-primary-container rounded-full blur-3xl opacity-50" />
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Glass borders and shadows handled via tailwind */
</style>
