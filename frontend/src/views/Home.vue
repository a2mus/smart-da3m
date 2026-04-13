<script setup lang="ts">
// Home view - Landing page for Ihsane platform
</script>

<template>
  <div class="min-h-screen flex flex-col relative overflow-hidden bg-surface">
    <!-- Abstract Nurturing Background Element -->
    <div class="absolute top-0 inset-x-0 h-[50vh] bg-gradient-to-b from-teal-50 to-surface -z-10 rounded-b-cloud opacity-70"></div>
    <div class="absolute -top-24 -end-24 w-96 h-96 bg-teal-100 rounded-full blur-3xl opacity-50 -z-10"></div>
    <div class="absolute top-32 -start-24 w-72 h-72 bg-ochre-100 rounded-full blur-3xl opacity-40 -z-10"></div>

    <!-- Header area -->
    <header class="w-full p-6 flex justify-between items-center z-10 max-w-7xl mx-auto">
      <div class="flex items-center gap-3">
        <img src="@/assets/logo.png" alt="Ihsane Logo" class="w-12 h-12 object-contain" />
        <span class="font-arabic text-2xl font-bold text-teal-800">{{ $t('app.name') }}</span>
      </div>
      <div class="flex items-center gap-4">
        <!-- Language Switcher placeholder -->
        <button class="text-ink-500 font-medium hover:text-teal-600 transition-colors">
          <span v-if="$i18n.locale === 'ar'">Fr</span>
          <span v-else>عربي</span>
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 flex items-center justify-center p-6 z-10 w-full max-w-7xl mx-auto">
      <div class="w-full max-w-4xl grid md:grid-cols-2 gap-12 items-center">
        
        <!-- Left/Right (RTL aware): Text Content -->
        <div class="text-center md:text-start space-y-6">
          <div class="inline-block px-4 py-1.5 rounded-full bg-teal-50 border border-teal-100 text-teal-700 font-medium text-sm mb-2">
            ✨ {{ $t('app.welcome') }}
          </div>
          
          <h1 class="text-5xl md:text-6xl font-black text-ink-900 leading-tight font-arabic text-balance">
            {{ $t('app.name') }}
          </h1>
          <p class="text-xl md:text-2xl font-medium text-teal-700 mt-2 font-arabic text-balance">
            {{ $t('app.tagline') }}
          </p>
          
          <p class="text-lg text-ink-600 max-w-lg mx-auto md:mx-0 text-balance leading-relaxed py-4">
            منصة تعليمية متطورة تدعم نمو طفلك الأكاديمي بأسلوب تربوي ذكي، آمن، وممتع. تتبع التقدم وتلقى التوصيات في بيئة تشجع على التعلم الذاتي.
          </p>

          <div class="flex flex-col sm:flex-row gap-4 justify-center md:justify-start pt-2">
            <router-link
              to="/login"
              class="btn-primary shadow-teal text-lg px-8 py-4 w-full sm:w-auto"
            >
              {{ $t('auth.login') }}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 rtl:rotate-180" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </router-link>
            
            <button class="btn-secondary w-full sm:w-auto px-8 py-4 text-lg">
              تعرف على المزيد
            </button>
          </div>
        </div>

        <!-- Right/Left (RTL aware): Visuals/Nurturing Card Focus -->
        <div class="relative hidden md:block">
          <div class="card-nurturing p-8 relative z-10 border border-white/50 bg-white/80 backdrop-blur-xl">
            <div class="flex items-start gap-4 mb-6">
              <div class="w-12 h-12 rounded-full bg-teal-100 flex items-center justify-center text-teal-600 shrink-0">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h3 class="font-bold text-ink-900 text-lg">التعلم التكيفي</h3>
                <p class="text-ink-600 mt-1 leading-relaxed">يتكيف المحتوى مع مستوى استيعاب التلميذ خطوة بخطوة، معززاً ثقته بنفسه.</p>
              </div>
            </div>
            
            <div class="flex items-start gap-4 mb-6">
              <div class="w-12 h-12 rounded-full bg-ochre-100 flex items-center justify-center text-ochre-600 shrink-0">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 class="font-bold text-ink-900 text-lg">متابعة الأبوين</h3>
                <p class="text-ink-600 mt-1 leading-relaxed">تحديثات إيجابية مستمرة وتوجيهات عملية لدعم طفلك في المنزل دون ضغوط.</p>
              </div>
            </div>
          </div>
          
          <!-- Decorative UI elements floating around -->
          <div class="absolute -bottom-6 -start-6 w-24 h-24 bg-teal-500 rounded-3xl opacity-10 rotate-12 -z-10"></div>
          <div class="absolute -top-8 -end-8 w-32 h-32 bg-ochre-400 rounded-full opacity-10 -z-10"></div>
        </div>

      </div>
    </main>
  </div>
</template>
