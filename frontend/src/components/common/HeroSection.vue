<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const startJourney = () => {
  router.push('/student/journey')
}

const learnMore = () => {
  router.push('/parent-dashboard')
}
</script>

<template>
  <section class="relative px-6 py-12 md:py-24 max-w-7xl mx-auto">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
      <div class="z-10 text-end">
        <h1 class="text-5xl md:text-7xl font-black text-primary leading-tight mb-6">
          مستقبل تعليم طفلك يبدأ هنا
        </h1>
        <p class="text-xl text-on-surface-variant max-w-xl mb-10 leading-relaxed">
          منصة إحسان تعتمد على تقنيات الذكاء الاصطناعي لتوفير رحلة تعليمية مخصصة لكل تلميذ جزائري، تتماشى مع وتيرته الخاصة وتطلعاته.
        </p>
        <div class="flex flex-col sm:flex-row-reverse gap-4">
          <button 
            class="bg-secondary text-on-secondary px-10 py-5 rounded-3xl text-xl font-bold shadow-lg hover:opacity-90 transition-all"
            @click="startJourney"
          >
            ابدأ الرحلة مجاناً
          </button>
          <button 
            class="bg-surface-container-low text-primary px-10 py-5 rounded-3xl text-xl font-bold hover:bg-surface-container-high transition-all"
            @click="learnMore"
          >
            اكتشف المزيد
          </button>
        </div>
      </div>
      <div class="relative">
        <div class="absolute -top-10 -end-10 w-64 h-64 bg-tertiary-fixed-dim/20 rounded-full blur-3xl" />
        <div class="absolute -bottom-10 -start-10 w-64 h-64 bg-secondary-fixed-dim/20 rounded-full blur-3xl" />
        <div class="relative aspect-square rounded-3xl overflow-hidden shadow-2xl rotate-2">
          <img
            alt="Student studying"
            class="w-full h-full object-cover"
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuBEN1zX9zChPg6yDgs-biPXWsEPm6lWU4SGBUBHDE9hOCHdAbhFYP_legk3NXlAOzOHVIfS11T-6M7yeDMtY6OS1u_z-aJxsw2oMdSDvDpkbJSOJkxE8u-YPgMZj6sBhK5ke33tlM-npYt1GgU5Y-pA1gH-5VSWxa01g4WcaDwqjkTYhgjdsd0yp4Mvk2p8lGvNwCVSd3b1e88MzcCURZ0VjXCv4ERwCDuvhSj7kYOnPRDyzVP5AT30sFlFMmfrq8O8KIGSz1AdYCQ"
          >
        </div>
        <!-- Decorative Floating Element -->
        <div class="absolute -bottom-6 -end-6 bg-surface-bright p-6 rounded-2xl shadow-xl flex items-center gap-4 animate-bounce">
          <div class="w-12 h-12 bg-tertiary-container rounded-full flex items-center justify-center text-on-primary">
            <span
              class="material-symbols-outlined"
              data-icon="auto_awesome"
            >auto_awesome</span>
          </div>
          <div class="text-end">
            <p class="font-bold text-primary">
              ذكاء تكيفي
            </p>
            <p class="text-xs text-on-surface-variant">
              مخصص 100% لطفلك
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
