<script setup lang="ts">
import HeroSection from '@/components/common/HeroSection.vue'
import FeatureGrid from '@/components/common/FeatureGrid.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const startNow = () => {
  router.push('/login')
}
</script>

<template>
  <div
    class="text-on-surface"
    dir="rtl"
  >
    <!-- TopAppBar -->
    <header class="fixed top-0 w-full z-50 bg-[#faf9f6]/80 dark:bg-slate-900/80 backdrop-blur-xl shadow-sm shadow-teal-900/5">
      <nav class="flex flex-row-reverse justify-between items-center px-8 py-4 max-w-7xl mx-auto font-['Plus_Jakarta_Sans','Tajawal'] text-end">
        <div
          class="flex items-center gap-2 cursor-pointer"
          @click="router.push('/')"
        >
          <span
            class="material-symbols-outlined text-[#00535b] dark:text-teal-400 text-3xl"
            data-icon="menu_book"
          >menu_book</span>
          <span class="text-2xl font-bold text-[#00535b] dark:text-teal-500">إحسان</span>
        </div>
        <div class="hidden md:flex flex-row-reverse gap-8 items-center">
          <a
            class="text-[#00535b] dark:text-teal-400 font-bold border-b-2 border-[#00535b] dark:border-teal-400"
            href="#"
          >الرئيسية</a>
          <a
            class="text-slate-600 dark:text-slate-400 hover:text-[#8c4e35] transition-colors duration-300"
            href="#"
          >المميزات</a>
          <a
            class="text-slate-600 dark:text-slate-400 hover:text-[#8c4e35] transition-colors duration-300"
            href="#"
          >كيف نعمل</a>
          <a
            class="text-slate-600 dark:text-slate-400 hover:text-[#8c4e35] transition-colors duration-300"
            href="#"
          >من نحن</a>
        </div>
        <button 
          class="bg-primary text-on-primary px-6 py-2.5 rounded-xl font-bold scale-95 active:opacity-80 transition-transform hover:bg-primary-container"
          @click="startNow"
        >
          ابدأ الآن
        </button>
      </nav>
    </header>

    <main class="pt-24 overflow-hidden">
      <!-- Hero Section -->
      <HeroSection />

      <!-- Features Bento Grid -->
      <FeatureGrid />

      <!-- How it Works -->
      <section class="py-24 px-6 max-w-7xl mx-auto">
        <div class="text-center mb-20">
          <h2 class="text-4xl font-bold text-primary">
            كيف تبدأ الرحلة؟
          </h2>
        </div>
        <div class="relative">
          <!-- Connecting Line (Desktop Only) -->
          <div class="hidden md:block absolute top-1/2 start-0 w-full h-0.5 bg-dashed border-t-2 border-dashed border-primary/20 -translate-y-1/2" />
          <div class="grid grid-cols-1 md:grid-cols-3 gap-12 relative">
            <!-- Step 1 -->
            <div class="bg-background flex flex-col items-center text-center">
              <div class="w-20 h-20 bg-primary text-on-primary rounded-full flex items-center justify-center text-3xl font-black mb-8 z-10 border-8 border-background shadow-lg">
                1
              </div>
              <h4 class="text-2xl font-bold text-primary mb-3">
                التقييم الأولي
              </h4>
              <p class="text-on-surface-variant">
                اختبار ذكي لتحديد مستوى المكتسبات القبلية وفجوات التعلم.
              </p>
            </div>
            <!-- Step 2 -->
            <div class="bg-background flex flex-col items-center text-center">
              <div class="w-20 h-20 bg-secondary text-on-primary rounded-full flex items-center justify-center text-3xl font-black mb-8 z-10 border-8 border-background shadow-lg">
                2
              </div>
              <h4 class="text-2xl font-bold text-primary mb-3">
                تخصيص المسار
              </h4>
              <p class="text-on-surface-variant">
                خوارزميتنا تبني برنامجاً دراسياً خاصاً بطفلك يركز على ما يحتاجه فعلاً.
              </p>
            </div>
            <!-- Step 3 -->
            <div class="bg-background flex flex-col items-center text-center">
              <div class="w-20 h-20 bg-tertiary text-on-primary rounded-full flex items-center justify-center text-3xl font-black mb-8 z-10 border-8 border-background shadow-lg">
                3
              </div>
              <h4 class="text-2xl font-bold text-primary mb-3">
                الإتقان والتميز
              </h4>
              <p class="text-on-surface-variant">
                دروس تفاعلية وتمارين مستمرة حتى يصل طفلك لدرجة الإتقان الكامل.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Testimonial -->
      <section class="bg-primary py-24 px-6 overflow-hidden relative">
        <div class="absolute top-0 end-0 p-20 opacity-10">
          <span
            class="material-symbols-outlined text-[200px]"
            data-icon="format_quote"
          >format_quote</span>
        </div>
        <div class="max-w-4xl mx-auto text-center relative z-10">
          <div class="mb-8">
            <img
              alt="Parent Testimonial"
              class="w-24 h-24 rounded-full mx-auto border-4 border-#faf9f6 shadow-xl object-cover"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuBgVvboab6kgO3YGJgYTcOeFk6xUVvgvMluLn3dNXCfBkaZimZ2konWzxiFJ1CFzP4RLYgYvoLdDyPKqIUEfP3tis7rSxv7NPriarHnbPvs8tsMVknOrIu-hZ1rJ4a9vRdwewoRYqISHA7RgW75M_YMugZLvM0C0wk4NerUvPPNo_baY0vI01UNR_MhQga1IEPVS1EQ1xlTZhDA2ZQhwdiBZ_M5PqGlMZ3raKHIa1M5V_Oo_MI1St9PG6o1I4Ub2RdQ5VcIOiTVOXU"
            >
          </div>
          <p class="text-3xl md:text-4xl font-medium text-on-primary italic leading-relaxed mb-10">
            "بفضل إحسان، لاحظت تحسناً مذهلاً في نتائج ابني في مادة الرياضيات خلال شهر واحد فقط. المنصة تشعره وكأنه يلعب بينما هو في الحقيقة يتعلم بذكاء."
          </p>
          <div>
            <h5 class="text-on-primary text-xl font-bold">
              السيدة مريم بن علي
            </h5>
            <p class="text-primary-fixed-dim">
              أم لتلميذ في السنة الرابعة ابتدائي - الجزائر العاصمة
            </p>
          </div>
        </div>
      </section>

      <!-- Final CTA -->
      <section class="py-24 px-6">
        <div class="max-w-5xl mx-auto bg-surface-container rounded-[3rem] p-12 md:p-20 text-center relative overflow-hidden">
          <div class="absolute -top-24 -start-24 w-64 h-64 bg-secondary/5 rounded-full" />
          <div class="relative z-10">
            <h2 class="text-4xl md:text-5xl font-black text-primary mb-6">
              هل أنت مستعد لتغيير مسار طفلك الدراسي؟
            </h2>
            <p class="text-xl text-on-surface-variant mb-12 max-w-2xl mx-auto">
              انضم إلى آلاف العائلات الجزائرية التي وضعت ثقتها في إحسان. التسجيل سريع ومجاني للبدء.
            </p>
            <button 
              class="bg-secondary text-on-secondary px-12 py-6 rounded-3xl text-2xl font-bold shadow-2xl hover:scale-105 active:scale-95 transition-all"
              @click="startNow"
            >
              سجل الآن مجاناً
            </button>
            <p class="mt-6 text-on-surface-variant text-sm">
              لا حاجة لبطاقة دفع • تجربة كاملة لمدة 7 أيام
            </p>
          </div>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer class="w-full border-t border-[#00535b]/10 bg-[#f4f3f1] dark:bg-slate-950">
      <div class="flex flex-col md:flex-row-reverse justify-between items-center px-12 py-10 gap-6 max-w-7xl mx-auto font-['Plus_Jakarta_Sans','Tajawal'] text-end text-sm">
        <div class="flex items-center gap-2">
          <span class="text-xl font-black text-[#00535b]">إحسان</span>
          <span
            class="material-symbols-outlined text-[#00535b]"
            data-icon="menu_book"
          >menu_book</span>
        </div>
        <div class="flex flex-wrap flex-row-reverse justify-center gap-8">
          <a
            class="text-slate-600 dark:text-slate-400 hover:underline hover:text-[#00535b] transition-all"
            href="#"
          >المميزات</a>
          <a
            class="text-slate-600 dark:text-slate-400 hover:underline hover:text-[#00535b] transition-all"
            href="#"
          >عن المنصة</a>
          <a
            class="text-slate-600 dark:text-slate-400 hover:underline hover:text-[#00535b] transition-all"
            href="#"
          >تواصل معنا</a>
          <a
            class="text-slate-600 dark:text-slate-400 hover:underline hover:text-[#00535b] transition-all"
            href="#"
          >سياسة الخصوصية</a>
        </div>
        <div class="text-slate-600 dark:text-slate-400">
          © ٢٠٢٤ إحسان. جميع الحقوق محفوظة.
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.bg-dashed {
  background-image: none;
}
</style>
