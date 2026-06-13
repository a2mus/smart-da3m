<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div
    dir="rtl"
    class="min-h-screen flex items-center justify-center bg-[#faf9f6] dark:bg-slate-950 px-4 py-12"
  >
    <div class="w-full max-w-lg bg-surface-container rounded-[2rem] p-8 shadow-lg text-center">
      <div
        class="flex items-center justify-center gap-3 mb-8 cursor-pointer"
        @click="router.push('/')"
      >
        <span
          class="material-symbols-outlined text-4xl text-[#00535b] dark:text-teal-400"
          data-icon="menu_book"
        >
          menu_book
        </span>
        <h1 class="text-3xl font-black text-[#00535b] dark:text-teal-500">
          إحسان
        </h1>
      </div>

      <h2 class="text-2xl font-bold text-on-surface mb-2">
        إنشاء حساب جديد
      </h2>
      <p class="text-on-surface-variant mb-8">
        اختر نوع الحساب للمتابعة
      </p>

      <div class="grid grid-cols-1 gap-4">
        <router-link
          to="/register"
          class="block bg-primary text-on-primary py-4 px-6 rounded-2xl font-bold text-lg
                 hover:bg-primary/90 active:scale-[0.98] transition-all"
        >
          تسجيل كولي أمر
        </router-link>
        <router-link
          to="/register"
          class="block border-2 border-primary text-primary py-4 px-6 rounded-2xl font-bold text-lg
                 hover:bg-primary/5 active:scale-[0.98] transition-all"
        >
          تسجيل كخبير بيداغوجي
        </router-link>
      </div>

      <p class="text-sm text-on-surface-variant mt-8">
        لديك حساب بالفعل؟
        <router-link
          to="/login"
          class="text-primary font-bold hover:underline"
        >
          تسجيل الدخول
        </router-link>
      </p>
    </div>
  </div>
</template>
