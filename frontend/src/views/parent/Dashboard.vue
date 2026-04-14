<script setup lang="ts">
</script>

<template>
  <div
    class="bg-background text-on-surface mb-24 min-h-screen font-['Tajawal']"
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
              data-alt="vibrant character illustration of a young smiling boy with short dark hair in a playful educational style"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuDN1A1ACgKMLdwtl3eZxJuuks3EhV7uvW0a7TudvfNjviZtI-RptKKdG6MPE-XwQoXYDmRQSFIQV_UpJpIEUrwWPR-kEkL50Q-QM9YICJZcZai2aC_5XfDnA2XABXUNm3CVi6XYMyR85TMFNsvKY59NeQBSUay90oOtLdMotlpjEd6S8iEWN2Hghtvekr_XUcTXhEKnbRfQH9TBwrL6jlligISAxtooVFd-awMn3dNwPpywDeAu8xVdxd42KFYoq4mpwRKGFEm5nbg"
            >
          </div>
        </div>
        <div class="flex items-center gap-4">
          <div class="text-2xl font-black text-[#00535b] dark:text-[#006D77] font-['Plus_Jakarta_Sans','Tajawal']">
            إحسان
          </div>
          <button class="material-symbols-outlined text-primary text-2xl transition-all duration-300 active:scale-95">
            swap_horiz
          </button>
        </div>
      </div>
    </header>

    <main class="pt-24 px-6 space-y-8 max-w-4xl mx-auto">
      <!-- Smart Message Card (Insight) -->
      <section class="relative">
        <div class="bg-surface-container-lowest p-6 asymmetric-border border-e-4 border-secondary shadow-[0_10px_30px_rgba(140,78,53,0.08)]">
          <div class="flex items-start gap-4">
            <div class="bg-secondary-fixed p-3 rounded-2xl shrink-0">
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
                أحمد يتفوق في <span class="font-bold text-primary">التعبير الشفهي</span> ولكنه يحتاج للمساعدة في <span class="font-bold text-secondary">التاء المربوطة</span>.
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
          <span class="text-sm text-stone-500 font-label">الفصل الدراسي الأول</span>
        </div>
        <div class="grid grid-cols-1 gap-6">
          <!-- Subject: Arabic -->
          <div class="bg-surface-container-low p-5 rounded-3xl space-y-3">
            <div class="flex justify-between items-center">
              <span class="font-bold">اللغة العربية</span>
              <span class="font-label text-primary font-bold">92%</span>
            </div>
            <div class="w-full bg-surface-container-highest rounded-full overflow-hidden h-4">
              <div
                class="h-full bg-primary rounded-full transition-all duration-1000"
                style="width: 92%"
              />
            </div>
            <p class="text-xs text-stone-500 italic">
              تميز ملحوظ في القواعد
            </p>
          </div>
          <!-- Subject: Math -->
          <div class="bg-surface-container-low p-5 rounded-3xl space-y-3">
            <div class="flex justify-between items-center">
              <span class="font-bold">الرياضيات</span>
              <span class="font-label text-secondary font-bold">78%</span>
            </div>
            <div class="w-full bg-surface-container-highest rounded-full overflow-hidden h-4">
              <div
                class="h-full bg-secondary rounded-full transition-all duration-1000"
                style="width: 78%"
              />
            </div>
            <p class="text-xs text-stone-500 italic">
              يحتاج للتركيز على الحساب الذهني
            </p>
          </div>
          <!-- Subject: Science -->
          <div class="bg-surface-container-low p-5 rounded-3xl space-y-3">
            <div class="flex justify-between items-center">
              <span class="font-bold">العلوم</span>
              <span class="font-label text-tertiary font-bold">85%</span>
            </div>
            <div class="w-full bg-surface-container-highest rounded-full overflow-hidden h-4">
              <div
                class="h-full bg-tertiary rounded-full transition-all duration-1000"
                style="width: 85%"
              />
            </div>
            <p class="text-xs text-stone-500 italic">
              اهتمام كبير بالتجارب العملية
            </p>
          </div>
        </div>
      </section>

      <!-- Recommendation Card -->
      <section>
        <div class="bg-primary p-6 rounded-[2.5rem] text-on-primary relative overflow-hidden group">
          <!-- Decorative Circle -->
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
              5 دقائق من الحساب الذهني اليوم
            </p>
            <button class="bg-secondary text-on-primary px-6 py-3 rounded-2xl font-bold self-start mt-2 shadow-lg shadow-secondary/20 active:scale-95 transition-transform hover:bg-[#a65d3f]">
              ابدأ التحدي
            </button>
          </div>
        </div>
      </section>

      <!-- Recent Activities (Bento-ish) -->
      <section class="space-y-4 pb-8">
        <h3 class="text-xl font-bold text-primary">
          آخر النشاطات
        </h3>
        <div class="grid grid-cols-2 gap-3">
          <div class="bg-tertiary-fixed-dim p-4 rounded-3xl h-32 flex flex-col justify-between hover:scale-[1.02] transition-transform cursor-pointer">
            <span class="material-symbols-outlined text-tertiary-container">history_edu</span>
            <span class="text-sm font-bold text-on-tertiary-fixed-variant">واجب الإملاء</span>
          </div>
          <div class="bg-secondary-fixed p-4 rounded-3xl flex flex-col justify-between row-span-2 h-auto hover:scale-[1.02] transition-transform cursor-pointer">
            <span class="material-symbols-outlined text-on-secondary-fixed-variant">emoji_events</span>
            <div>
              <span class="text-2xl font-black font-label text-on-secondary-fixed">12</span>
              <p class="text-xs font-bold text-on-secondary-fixed-variant">
                نقطة تميز جديدة
              </p>
            </div>
          </div>
          <div class="bg-surface-container p-4 rounded-3xl h-32 flex flex-col justify-between hover:scale-[1.02] transition-transform cursor-pointer">
            <span class="material-symbols-outlined text-outline">menu_book</span>
            <span class="text-sm font-bold">قصة ما قبل النوم</span>
          </div>
        </div>
      </section>
    </main>

    <!-- BottomNavBar -->
    <nav class="fixed bottom-0 start-0 w-full flex flex-row-reverse justify-around items-center px-4 pb-6 pt-3 bg-[#faf9f6]/80 dark:bg-stone-900/80 backdrop-blur-xl z-50 rounded-t-3xl shadow-[0_-4px_40px_rgba(0,109,119,0.06)] max-w-md mx-auto md:max-w-none md:justify-center md:gap-16">
      <!-- Home (Active) -->
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
      <!-- Progress -->
      <a
        class="flex flex-col items-center justify-center text-stone-400 dark:text-stone-500 px-5 py-2 hover:bg-[#f4f3f1] dark:hover:bg-stone-800 transition-colors rounded-2xl"
        href="#"
      >
        <span class="material-symbols-outlined">insights</span>
        <span class="font-['Plus_Jakarta_Sans','Tajawal'] text-[12px] font-medium font-body">التقدم</span>
      </a>
      <!-- Recommendations -->
      <a
        class="flex flex-col items-center justify-center text-stone-400 dark:text-stone-500 px-5 py-2 hover:bg-[#f4f3f1] dark:hover:bg-stone-800 transition-colors rounded-2xl"
        href="#"
      >
        <span class="material-symbols-outlined">auto_awesome</span>
        <span class="font-['Plus_Jakarta_Sans','Tajawal'] text-[12px] font-medium font-body">التوصيات</span>
      </a>
      <!-- Account -->
      <a
        class="flex flex-col items-center justify-center text-stone-400 dark:text-stone-500 px-5 py-2 hover:bg-[#f4f3f1] dark:hover:bg-stone-800 transition-colors rounded-2xl"
        href="#"
      >
        <span class="material-symbols-outlined">person</span>
        <span class="font-['Plus_Jakarta_Sans','Tajawal'] text-[12px] font-medium font-body">الحساب</span>
      </a>
    </nav>
  </div>
</template>

<style scoped>
.tajawal-black { font-weight: 900; }
.asymmetric-border { border-radius: 2rem 1rem 3rem 1rem; }
</style>
