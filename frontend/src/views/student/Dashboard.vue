<script setup lang="ts">
</script>

<template>
  <div
    class="bg-surface text-on-surface overflow-hidden min-h-screen w-full font-['Tajawal']"
    dir="rtl"
  >
    <!-- TopAppBar -->
    <header class="bg-[#faf9f6]/80 dark:bg-stone-900/80 backdrop-blur-xl docked full-width top-0 rounded-b-[2rem] no-border shadow-sm shadow-[#006D77]/5 shadow-[0_10px_30px_-15px_rgba(0,109,119,0.1)] flex flex-row-reverse justify-between items-center w-full px-8 py-4 z-40 sticky">
      <div class="flex items-center gap-6">
        <div class="flex gap-4">
          <button class="material-symbols-outlined text-[#006D77] text-2xl hover:scale-105 transition-transform duration-300">
            notifications
          </button>
          <button class="material-symbols-outlined text-[#006D77] text-2xl hover:scale-105 transition-transform duration-300">
            stars
          </button>
        </div>
        <div class="h-12 w-12 rounded-full overflow-hidden bg-primary-container border-2 border-primary">
          <img
            alt="Cheerful student avatar"
            data-alt="close-up portrait of a smiling young boy with curly hair in a bright classroom setting, soft natural lighting, high-end commercial style"
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuCsjVnq-Q6BKkb3R1X259SSoHmpp2lDNpDN9pKzK31_aUzHyUdSRY1tzMeyf-njVSew5-BPtxS7Bdn5s_-oX6o9nw5GSB35mxTUSDNX2ugzn1O8JtFFtD09_FQPHnJkbSCtsXoIlbo80Ot6UttInY-j-XaxD__lw_ZEJbYrza2jj2l85cnY6WqY1eZ3Vv0si1c25k4cGTQBtydsVIf8KJk-U4c3UV6t44iBRgxcetKNsheKi0WMgXRYtqmZiMblM3rVzWBCSKrdugs"
          >
        </div>
      </div>
      <div class="flex items-center gap-12">
        <nav class="hidden md:flex gap-8 items-center">
          <a
            class="font-['Tajawal'] text-lg font-bold tracking-tight text-[#006D77] border-b-4 border-[#8c4e35] pb-1 hover:scale-105 transition-transform duration-300"
            href="#"
          >الرئيسية</a>
          <a
            class="font-['Tajawal'] text-lg font-bold tracking-tight text-stone-400 hover:scale-105 transition-transform duration-300"
            href="#"
          >مساراتي</a>
          <a
            class="font-['Tajawal'] text-lg font-bold tracking-tight text-stone-400 hover:scale-105 transition-transform duration-300"
            href="#"
          >المكتبة</a>
        </nav>
        <div class="text-2xl font-black text-[#006D77] dark:text-teal-400 italic">
          Ihsane Learning
        </div>
      </div>
    </header>

    <main class="grid grid-cols-1 md:grid-cols-12 gap-8 px-6 md:px-12 pt-8 pb-32 h-full overflow-y-auto overflow-x-hidden">
      <!-- Right Section: Journey Path (Learning Nodes) - Responsive Order 2 -->
      <section class="col-span-1 border-t pt-8 md:border-t-0 md:pt-0 md:col-span-5 flex flex-col gap-6 relative order-2 md:order-1">
        <h2 class="text-4xl font-black text-secondary mb-4">
          خريطة التعلم
        </h2>
        <div class="bg-surface-container-low rounded-[3rem] p-6 md:p-12 h-full relative overflow-hidden min-h-[400px]">
          <!-- Path Graphics -->
          <svg
            class="absolute inset-0 w-full h-full pointer-events-none opacity-20"
            viewBox="0 0 400 600"
            preserveAspectRatio="xMidYMid slice"
          >
            <path
              d="M300,500 C150,450 50,350 100,250 C150,150 300,100 200,50"
              fill="none"
              stroke="#8c4e35"
              stroke-dasharray="15,15"
              stroke-width="8"
            />
          </svg>
          <div class="flex flex-col gap-12 md:gap-20 relative z-10 items-center md:items-stretch">
            <!-- Node 1: Completed -->
            <div class="flex items-center gap-6 md:self-end md:translate-x-4">
              <div class="flex flex-col text-left">
                <span class="text-lg font-bold text-secondary">الجمع</span>
                <span class="text-sm text-stone-500 font-label">مكتمل</span>
              </div>
              <div class="w-16 h-16 md:w-20 md:h-20 bg-secondary rounded-[2.5rem] flex items-center justify-center shadow-lg shadow-secondary/20">
                <span
                  class="material-symbols-outlined text-on-primary text-4xl"
                  data-icon="done"
                  style="font-variation-settings: 'FILL' 1;"
                >done</span>
              </div>
            </div>
            <!-- Node 2: Current (Active) -->
            <div class="flex items-center gap-6 md:self-start md:-translate-x-4">
              <div class="w-24 h-24 md:w-28 md:h-28 bg-primary rounded-[3rem] flex items-center justify-center shadow-2xl shadow-primary/40 ring-8 ring-primary-fixed-dim/30 animate-pulse">
                <span
                  class="material-symbols-outlined text-on-primary text-5xl"
                  data-icon="explore"
                  style="font-variation-settings: 'FILL' 1;"
                >explore</span>
              </div>
              <div class="flex flex-col">
                <span class="text-3xl font-black text-primary">الكسور</span>
                <span class="text-lg font-bold text-primary-container">المهمة الحالية</span>
              </div>
            </div>
            <!-- Node 3: Future -->
            <div class="flex items-center gap-6 self-center opacity-40">
              <div class="w-16 h-16 md:w-20 md:h-20 bg-stone-300 rounded-[2.5rem] flex items-center justify-center">
                <span
                  class="material-symbols-outlined text-stone-500 text-3xl md:text-4xl"
                  data-icon="lock"
                >lock</span>
              </div>
              <div class="flex flex-col">
                <span class="text-xl font-bold text-stone-600">الضرب</span>
                <span class="text-sm text-stone-500 font-label">قريباً</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Left Section: Welcome & Current Mission - Responsive Order 1 -->
      <section class="col-span-1 md:col-span-7 flex flex-col gap-8 order-1 md:order-2">
        <!-- Welcome Hero -->
        <div class="bg-gradient-to-br from-primary to-primary-container rounded-[3rem] p-6 md:p-10 flex flex-col md:flex-row items-center justify-between shadow-[0_20px_50px_rgba(0,83,91,0.15)] relative overflow-hidden text-center md:text-right gap-6 md:gap-0">
          <div class="relative z-10 w-full">
            <h1 class="text-4xl md:text-6xl font-black text-on-primary mb-2">
              مرحباً يا بطل!
            </h1>
            <p class="text-primary-fixed text-xl md:text-2xl font-bold">
              أنت تقوم بعمل رائع اليوم
            </p>
            <div class="mt-8 inline-flex items-center gap-4 bg-surface-bright/20 backdrop-blur-md rounded-full px-6 py-3 border border-#faf9f6/10 w-full max-w-sm ms-auto me-auto md:me-0 md:ms-auto">
              <span
                class="material-symbols-outlined text-tertiary-fixed"
                data-icon="workspace_premium"
                style="font-variation-settings: 'FILL' 1;"
              >workspace_premium</span>
              <span class="text-on-primary font-bold text-xl min-w-16">المستوى 2</span>
              <div class="w-full h-3 bg-surface-bright/30 rounded-full overflow-hidden">
                <div class="w-3/4 h-full bg-tertiary-fixed shadow-[0_0_15px_#acefe7]" />
              </div>
            </div>
          </div>
          <div class="relative w-40 h-40 md:w-48 md:h-48 shrink-0">
            <img
              alt="Student success"
              class="w-full h-full object-cover rounded-[2.5rem] rotate-3 border-4 border-#faf9f6/20"
              data-alt="happy child student raising hands in celebration with school background"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuARvafOtgxBCGRLsJNz3X40jOHJZsgEHxeubB5p97sF9IBnP4tsw5M5DAyun2Ew0LEM3a5sUKhGCL3qWovS0DkXw6H7L6gQ6rafqYETDLuCSfQqepj9C3l4t0nB-LW_RVJ5gdB7jLmZ8mA4QE9SQ2w5M_m0Qp5M0Ey1ecxCbVuKkJj-oqrhcvjZYcdk0EzEt0-v_uCksWX-tCeiZiZ2mpH3INOyC9-RVSwt9EQBNYtL9q_x5FrwhrqQHndwv_EYt1f8KAYs6pz1wqg"
            >
          </div>
        </div>

        <!-- Current Mission Card -->
        <div class="bg-surface-container-lowest rounded-[3rem] md:rounded-[4rem] p-6 md:p-12 flex flex-col md:flex-row items-center md:items-start gap-6 md:gap-10 asymmetric-shadow flex-1 group">
          <div class="w-32 h-32 md:w-48 md:h-48 bg-primary-fixed-dim/20 rounded-[2.5rem] md:rounded-[3rem] flex items-center justify-center shrink-0">
            <span
              class="material-symbols-outlined text-primary text-[5rem] md:text-[8rem]"
              data-icon="calculate"
              style="font-variation-settings: 'FILL' 1;"
            >calculate</span>
          </div>
          <div class="flex-1 text-center md:text-right w-full">
            <div class="flex flex-col gap-2">
              <span class="text-secondary font-black text-xl md:text-2xl">الوحدة الرابعة</span>
              <h3 class="text-5xl md:text-7xl font-black text-primary leading-tight">
                الكسور
              </h3>
              <p class="text-on-surface-variant text-lg md:text-xl mt-2">
                تعلم كيف تقسم الأشياء بالتساوي مع أصدقائك
              </p>
            </div>
            
            <button class="w-full md:w-32 h-20 md:h-32 bg-primary rounded-[2rem] md:rounded-[3rem] flex items-center justify-center shadow-2xl shadow-primary/40 md:group-hover:scale-110 transition-transform duration-500 mt-6 md:mt-0 md:absolute start-12 bottom-12 min-w-[80px]">
              <span
                class="material-symbols-outlined text-on-primary text-4xl md:text-6xl md:translate-x-1"
                data-icon="play_arrow"
                style="font-variation-settings: 'FILL' 1;"
              >play_arrow</span>
            </button>
          </div>
        </div>

        <!-- Zakat al-Ilm Card -->
        <div class="bg-secondary-container/30 rounded-[2.5rem] p-6 flex flex-col sm:flex-row items-center sm:justify-between border-2 border-secondary/10 gap-4">
          <div class="flex items-center gap-6">
            <div class="w-16 h-16 bg-secondary text-on-primary rounded-2xl flex items-center justify-center shrink-0">
              <span
                class="material-symbols-outlined text-3xl"
                data-icon="lightbulb"
                style="font-variation-settings: 'FILL' 1;"
              >lightbulb</span>
            </div>
            <div class="text-center sm:text-right">
              <h4 class="text-xl md:text-2xl font-black text-secondary">
                نصيحة من صديق
              </h4>
              <p class="text-on-secondary-container font-bold italic">
                "هل تعلم أن الكسور هي مجرد أجزاء من الكل؟"
              </p>
            </div>
          </div>
          <button class="bg-surface-bright/80 backdrop-blur p-4 rounded-2xl text-secondary hover:bg-secondary hover:text-on-primary transition-all shadow-sm">
            <span
              class="material-symbols-outlined text-3xl"
              data-icon="volume_up"
            >volume_up</span>
          </button>
        </div>
      </section>
    </main>

    <!-- BottomNavBar -->
    <nav class="fixed bottom-0 start-0 w-full z-50 flex flex-row-reverse justify-around items-end px-4 md:px-10 bg-surface-bright/90 dark:bg-stone-800/90 backdrop-blur-2xl rounded-t-[3rem] pb-6 pt-4 shadow-[0_-15px_40px_-10px_rgba(0,0,0,0.08)]">
      <button class="flex flex-col items-center justify-center bg-[#006D77] text-on-primary rounded-[2rem] px-6 md:px-8 py-3 transform -translate-y-4 shadow-lg shadow-[#006D77]/30 transition-all active:scale-95">
        <span
          class="material-symbols-outlined text-2xl md:text-3xl"
          data-icon="home"
          style="font-variation-settings: 'FILL' 1;"
        >home</span>
        <span class="font-['Tajawal'] font-black text-xs md:text-sm mt-1">الرئيسية</span>
      </button>
      <button class="flex flex-col items-center justify-center text-stone-500 dark:text-stone-400 px-4 md:px-6 py-2 hover:text-[#006D77] transition-colors">
        <span
          class="material-symbols-outlined text-2xl md:text-3xl"
          data-icon="map"
        >map</span>
        <span class="font-['Tajawal'] font-black text-xs md:text-sm mt-1">مساري</span>
      </button>
      <button class="flex flex-col items-center justify-center text-stone-500 dark:text-stone-400 px-4 md:px-6 py-2 hover:text-[#006D77] transition-colors">
        <span
          class="material-symbols-outlined text-2xl md:text-3xl"
          data-icon="workspace_premium"
        >workspace_premium</span>
        <span class="font-['Tajawal'] font-black text-xs md:text-sm mt-1">جوائزي</span>
      </button>
      <button class="flex flex-col items-center justify-center text-stone-500 dark:text-stone-400 px-4 md:px-6 py-2 hover:text-[#006D77] transition-colors">
        <span
          class="material-symbols-outlined text-2xl md:text-3xl"
          data-icon="local_library"
        >local_library</span>
        <span class="font-['Tajawal'] font-black text-xs md:text-sm mt-1">المكتبة</span>
      </button>
    </nav>
  </div>
</template>

<style scoped>
.asymmetric-shadow { 
  box-shadow: 20px 20px 60px #e6e5e2, -20px -20px 60px #faf9f6; 
}
.dashed-path {
  background-image: repeating-linear-gradient(90deg, #8c4e35 0, #8c4e35 10px, transparent 10px, transparent 20px);
  height: 4px;
  width: 100%;
}
</style>
