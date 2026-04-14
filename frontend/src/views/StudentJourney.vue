<script setup lang="ts">
import { mockUiState } from '@/services/mockUiState';
import JourneyNode from '@/components/student/JourneyNode.vue';
import JourneyPathSvg from '@/components/student/JourneyPathSvg.vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const journey = mockUiState.journey;

// Calculate alignment based on index to create a zigzag map layout
const getAlignmentClass = (index: number) => {
  const mod = index % 3;
  if (mod === 0) return 'self-end translate-x-4';
  if (mod === 1) return 'self-start -translate-x-4';
  return 'self-center';
};
</script>

<template>
  <div class="bg-surface text-on-surface overflow-x-hidden min-h-screen w-full p-0 m-0" dir="rtl">
    <!-- TopAppBar -->
    <header class="bg-[#faf9f6]/90 dark:bg-stone-900/90 backdrop-blur-xl w-full top-0 rounded-b-[2rem] shadow-sm shadow-[#006D77]/5 flex flex-row-reverse justify-between items-center px-4 md:px-8 py-4 z-50 sticky mb-8">
      <div class="flex items-center gap-4 md:gap-6">
        <div class="flex gap-2 text-primary cursor-pointer" @click="router.push('/')">
           <span class="material-symbols-outlined text-3xl">logout</span>
        </div>
        <div class="h-12 w-12 rounded-full overflow-hidden bg-primary-container border-2 border-primary hidden md:block">
          <img alt="Student avatar" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCsjVnq-Q6BKkb3R1X259SSoHmpp2lDNpDN9pKzK31_aUzHyUdSRY1tzMeyf-njVSew5-BPtxS7Bdn5s_-oX6o9nw5GSB35mxTUSDNX2ugzn1O8JtFFtD09_FQPHnJkbSCtsXoIlbo80Ot6UttInY-j-XaxD__lw_ZEJbYrza2jj2l85cnY6WqY1eZ3Vv0si1c25k4cGTQBtydsVIf8KJk-U4c3UV6t44iBRgxcetKNsheKi0WMgXRYtqmZiMblM3rVzWBCSKrdugs"/>
        </div>
      </div>
      <div class="flex items-center gap-12">
        <nav class="hidden lg:flex gap-8 items-center cursor-pointer">
          <a class="font-['Tajawal'] text-lg font-bold tracking-tight text-stone-400 hover:scale-105 transition-transform duration-300">الرئيسية</a>
          <a class="font-['Tajawal'] text-lg font-bold tracking-tight text-[#006D77] border-b-4 border-[#8c4e35] pb-1 hover:scale-105 transition-transform duration-300">مساراتي</a>
          <a class="font-['Tajawal'] text-lg font-bold tracking-tight text-stone-400 hover:scale-105 transition-transform duration-300">المكتبة</a>
        </nav>
        <div class="text-2xl font-black text-[#006D77] dark:text-teal-400 italic cursor-pointer" @click="router.push('/')">Ihsane Learning</div>
      </div>
    </header>

    <main class="grid grid-cols-1 lg:grid-cols-12 gap-8 px-4 md:px-12 pb-32 max-w-[1400px] mx-auto min-h-[calc(100vh-200px)]">
      <!-- Right Section: Journey Path (Learning Nodes) -->
      <section class="lg:col-span-5 flex flex-col gap-6 relative order-2 lg:order-1">
        <h2 class="text-3xl md:text-4xl font-black text-secondary mb-4">خريطة التعلم</h2>
        <div class="bg-surface-container-low rounded-[3rem] p-6 py-12 md:p-12 h-full relative overflow-hidden flex-1">
          <!-- Central Connecting Path -->
          <JourneyPathSvg />
          
          <div class="flex flex-col gap-12 md:gap-20 relative z-10 justify-between h-full py-4">
            <!-- Render actual nodes array from mock data -->
            <JourneyNode 
              v-for="(task, index) in journey.tasks"
              :key="task.id"
              :id="task.id"
              :title="task.title"
              :type="task.type"
              :state="task.state"
              :score="task.score"
              class="w-full flex"
              :class="getAlignmentClass(index)"
            />
          </div>
        </div>
      </section>

      <!-- Left Section: Welcome & Current Mission -->
      <section class="lg:col-span-7 flex flex-col gap-8 order-1 lg:order-2">
        <!-- Welcome Hero -->
        <div class="bg-gradient-to-br from-primary to-primary-container rounded-[3rem] p-8 md:p-10 flex flex-col md:flex-row items-center justify-between shadow-[0_20px_50px_rgba(0,83,91,0.15)] relative overflow-hidden gap-6">
          <div class="relative z-10 text-center md:text-right">
            <h1 class="text-4xl md:text-6xl font-black text-white mb-2">مرحباً يا بطل!</h1>
            <p class="text-primary-fixed text-xl md:text-2xl font-bold">أنت تقوم بعمل رائع اليوم</p>
            <div class="mt-6 md:mt-8 inline-flex items-center gap-4 bg-white/20 backdrop-blur-md rounded-full px-6 py-3 border border-white/10 mx-auto md:mx-0">
              <span class="material-symbols-outlined text-tertiary-fixed" style="font-variation-settings: 'FILL' 1;">workspace_premium</span>
              <span class="text-white font-bold text-xl">المستوى 2</span>
              <div class="w-24 md:w-32 h-3 bg-white/30 rounded-full overflow-hidden">
                <div class="w-3/4 h-full bg-tertiary-fixed shadow-[0_0_15px_#acefe7]"></div>
              </div>
            </div>
          </div>
          <div class="relative w-40 h-40 md:w-48 md:h-48 mx-auto md:mx-0">
            <img alt="Student success" class="w-full h-full object-cover rounded-[2.5rem] rotate-3 border-4 border-white/20" src="https://lh3.googleusercontent.com/aida-public/AB6AXuARvafOtgxBCGRLsJNz3X40jOHJZsgEHxeubB5p97sF9IBnP4tsw5M5DAyun2Ew0LEM3a5sUKhGCL3qWovS0DkXw6H7L6gQ6rafqYETDLuCSfQqepj9C3l4t0nB-LW_RVJ5gdB7jLmZ8mA4QE9SQ2w5M_m0Qp5M0Ey1ecxCbVuKkJj-oqrhcvjZYcdk0EzEt0-v_uCksWX-tCeiZiZ2mpH3INOyC9-RVSwt9EQBNYtL9q_x5FrwhrqQHndwv_EYt1f8KAYs6pz1wqg"/>
          </div>
        </div>

        <!-- Current Mission Card -->
        <div class="bg-surface-container-lowest rounded-[4rem] p-8 md:p-12 flex flex-col md:flex-row items-center gap-6 md:gap-10 shadow-lg flex-1 group" style="box-shadow: 20px 20px 60px #e6e5e2, -20px -20px 60px #ffffff;">
          <div class="w-32 h-32 md:w-48 md:h-48 bg-primary-fixed-dim/20 rounded-[3rem] flex items-center justify-center shrink-0">
            <span class="material-symbols-outlined text-primary text-[6rem] md:text-[8rem]" style="font-variation-settings: 'FILL' 1;">calculate</span>
          </div>
          <div class="flex-1 text-center md:text-right w-full">
            <div class="flex flex-col gap-2">
               <span class="text-secondary font-black text-xl md:text-2xl">{{ journey.moduleName }}</span>
               <h3 class="text-5xl md:text-7xl font-black text-primary leading-tight">الكسور</h3>
               <p class="text-on-surface-variant text-lg md:text-xl mt-2">المهمة الحالية جاهزة. اضغط للبدء!</p>
            </div>
          </div>
          <button class="w-24 h-24 md:w-32 md:h-32 bg-primary rounded-[2.5rem] md:rounded-[3rem] flex items-center justify-center shadow-2xl shadow-primary/40 group-hover:-translate-x-2 transition-transform duration-500 shrink-0 mx-auto md:mx-0 mt-4 md:mt-0 cursor-pointer">
            <span class="material-symbols-outlined text-white text-5xl md:text-6xl translate-x-1" style="font-variation-settings: 'FILL' 1;">play_arrow</span>
          </button>
        </div>

        <!-- Zakat al-Ilm Card -->
        <div class="bg-secondary-container/30 rounded-[2.5rem] p-6 flex items-center justify-between border-2 border-secondary/10">
          <div class="flex items-center gap-4 md:gap-6">
            <div class="w-12 h-12 md:w-16 md:h-16 bg-secondary text-white rounded-2xl flex items-center justify-center shrink-0">
              <span class="material-symbols-outlined text-2xl md:text-3xl" style="font-variation-settings: 'FILL' 1;">lightbulb</span>
            </div>
            <div>
              <h4 class="text-xl md:text-2xl font-black text-secondary">نصيحة من صديق</h4>
              <p class="text-on-secondary-container font-bold italic text-sm md:text-base">"هل تعلم أن الكسور هي مجرد أجزاء من الكل؟"</p>
            </div>
          </div>
          <button class="bg-white/80 backdrop-blur p-3 md:p-4 rounded-2xl text-secondary hover:bg-secondary hover:text-white transition-all shadow-sm hidden md:block">
            <span class="material-symbols-outlined text-3xl">volume_up</span>
          </button>
        </div>
      </section>
    </main>

    <!-- BottomNavBar (Mobile/Tablet) -->
    <nav class="fixed bottom-0 left-0 w-full z-50 flex lg:hidden flex-row-reverse justify-around items-end px-4 md:px-10 bg-white/90 dark:bg-stone-800/90 backdrop-blur-2xl rounded-t-[3rem] pb-6 pt-4 shadow-[0_-15px_40px_-10px_rgba(0,0,0,0.08)]">
      <button class="flex flex-col items-center justify-center text-stone-500 dark:text-stone-400 px-4 md:px-6 py-2 hover:text-[#006D77] transition-colors" @click="router.push('/')">
        <span class="material-symbols-outlined text-3xl" style="font-variation-settings: 'FILL' 1;">home</span>
        <span class="font-['Tajawal'] font-black text-xs md:text-sm mt-1">الرئيسية</span>
      </button>
      <button class="flex flex-col items-center justify-center bg-[#006D77] text-white rounded-[2rem] px-6 md:px-8 py-3 transform -translate-y-4 shadow-lg shadow-[#006D77]/30 transition-all active:scale-95">
        <span class="material-symbols-outlined text-3xl">map</span>
        <span class="font-['Tajawal'] font-black text-xs md:text-sm mt-1">مساري</span>
      </button>
      <button class="flex flex-col items-center justify-center text-stone-500 dark:text-stone-400 px-4 md:px-6 py-2 hover:text-[#006D77] transition-colors">
        <span class="material-symbols-outlined text-3xl">workspace_premium</span>
        <span class="font-['Tajawal'] font-black text-xs md:text-sm mt-1">جوائزي</span>
      </button>
      <button class="flex flex-col items-center justify-center text-stone-500 dark:text-stone-400 px-4 md:px-6 py-2 hover:text-[#006D77] transition-colors">
        <span class="material-symbols-outlined text-3xl">local_library</span>
        <span class="font-['Tajawal'] font-black text-xs md:text-sm mt-1">المكتبة</span>
      </button>
    </nav>
  </div>
</template>
