<script setup lang="ts">
import { onMounted } from 'vue'
import { useAnalyticsStore } from '@/stores/analyticsStore'
import CompetencyHeatmap from '@/components/expert/CompetencyHeatmap.vue'

const analyticsStore = useAnalyticsStore()

onMounted(() => {
  analyticsStore.fetchHeatmap()
  analyticsStore.fetchStudentGroups()
  analyticsStore.fetchMetrics()
})
</script>

<template>
  <div
    class="min-h-screen bg-[#faf9f6] text-on-surface font-['Tajawal']"
    dir="rtl"
  >
    <!-- SideNavBar (Desktop Drawer) -->
    <aside class="h-screen w-72 fixed end-0 top-0 border-s-0 bg-[#faf9f6]/80 dark:bg-slate-900/80 backdrop-blur-3xl flex flex-col py-8 px-4 z-50">
      <div class="mb-10 px-4">
        <h1 class="text-2xl font-bold text-[#00535b] dark:text-[#006D77]">
          إحسان للتحليل
        </h1>
        <p class="text-slate-500 text-sm mt-1">
          لوحة تحكم الخبراء
        </p>
      </div>
      <nav class="space-y-2 flex-1">
        <a
          class="flex items-center gap-3 px-4 py-3 text-slate-500 dark:text-slate-400 font-medium hover:bg-[#f4f3f1]/50 transition-colors duration-200 rounded-xl group"
          href="#"
        >
          <span class="material-symbols-outlined group-hover:scale-110 transition-transform">dashboard</span>
          <span>نظرة عامة</span>
        </a>
        <a
          class="flex items-center gap-3 px-4 py-3 text-[#00535b] dark:text-[#006D77] font-bold border-e-4 border-[#00535b] bg-[#f4f3f1] dark:bg-slate-800 rounded-s-none rounded-xl"
          href="#"
        >
          <span
            class="material-symbols-outlined"
            style="font-variation-settings: 'FILL' 1;"
          >analytics</span>
          <span>خرائط الكفاءات</span>
        </a>
      </nav>
      <div class="mt-auto flex items-center gap-3 px-4 py-4 bg-surface-container-low rounded-2xl">
        <div>
          <p class="font-bold text-sm text-on-surface">
            الخبير البيداغوجي
          </p>
          <p class="text-xs text-slate-500">
            لوحة القياس والتحليل
          </p>
        </div>
      </div>
    </aside>

    <!-- TopNavBar -->
    <header class="w-[calc(100%-18rem)] fixed start-0 top-0 z-40 bg-[#faf9f6]/80 dark:bg-slate-950/80 backdrop-blur-2xl flex flex-row-reverse justify-between items-center h-16 px-8">
      <div class="flex items-center gap-6">
        <span class="font-['Cairo'] text-sm font-bold text-[#00535b]">الخبير البيداغوجي</span>
      </div>
      <div class="flex items-center gap-8">
        <h2 class="text-xl font-black text-[#00535b] dark:text-[#006D77] font-['Cairo']">
          تحليلات الكفاءات والتحصيل
        </h2>
      </div>
    </header>

    <!-- Main Content -->
    <main class="me-72 pt-24 pb-12 px-8 min-h-screen">
      <!-- Header Section -->
      <section class="mb-10 flex flex-col md:flex-row justify-between items-end gap-6">
        <div class="max-w-2xl">
          <span class="bg-secondary-container text-on-secondary-container px-3 py-1 rounded-full text-xs font-bold font-['Inter'] mb-3 inline-block uppercase tracking-wider">Analytics Hub</span>
          <h2 class="text-4xl font-black text-primary leading-tight mb-2">
            خريطة التحكم في الكفاءات
          </h2>
          <p class="text-on-surface-variant leading-relaxed">
            متابعة مستويات التحكم لكل تلميذ وكفاءة بناءً على بيانات التقييم التكيفي والتحليلات البيداغوجية.
          </p>
        </div>
        <div class="flex items-center gap-3">
          <button
            class="flex items-center gap-2 px-4 py-2.5 bg-surface-container-high hover:bg-surface-container-highest text-primary font-bold text-sm rounded-xl border border-outline-variant/30 transition-all duration-200 shadow-sm disabled:opacity-50"
            :disabled="analyticsStore.exporting"
            @click="analyticsStore.exportReport('heatmap', 'csv')"
          >
            <span class="material-symbols-outlined text-lg">download</span>
            <span>تصدير CSV</span>
          </button>
          <button
            class="flex items-center gap-2 px-4 py-2.5 bg-primary hover:bg-[#003f45] text-on-primary font-bold text-sm rounded-xl transition-all duration-200 shadow-sm disabled:opacity-50"
            :disabled="analyticsStore.exporting"
            @click="analyticsStore.exportReport('heatmap', 'pdf')"
          >
            <span class="material-symbols-outlined text-lg">picture_as_pdf</span>
            <span>تصدير PDF</span>
          </button>
        </div>
      </section>

      <!-- Competency Heatmap Section -->
      <section class="mb-12 bg-surface-bright p-6 rounded-[2rem] border border-outline-variant/10 shadow-sm">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold text-primary">
            الخريطة الحرارية للكفاءات
          </h3>
        </div>
        <CompetencyHeatmap
          :data="analyticsStore.heatmapData"
          :loading="analyticsStore.loading"
        />
      </section>
    </main>
  </div>
</template>
