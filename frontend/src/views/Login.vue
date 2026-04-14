<script setup lang="ts">
// Login view - Multi-role authentication
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-6 relative bg-surface overflow-hidden">
    <!-- Abstract Nurturing Background -->
    <div class="absolute top-0 start-0 w-full h-96 bg-gradient-to-b from-teal-50 to-transparent -z-10" />
    <div class="absolute -bottom-32 -start-32 w-96 h-96 bg-ochre-50 rounded-full blur-3xl opacity-60 -z-10" />

    <div class="w-full max-w-4xl grid md:grid-cols-2 gap-8 items-center bg-surface-bright rounded-3xl shadow-[0_20px_60px_rgba(0,0,0,0.05)] p-4 md:p-8">
      <!-- Logo & Branding Info -->
      <div class="text-center md:text-start p-6 flex flex-col justify-center h-full border-b md:border-b-0 md:border-e border-ink-100">
        <router-link
          to="/"
          class="inline-flex items-center gap-3 mb-8 mx-auto md:mx-0"
        >
          <img
            src="@/assets/logo.png"
            alt="Ihsane Logo"
            class="w-10 h-10 object-contain"
          >
          <span class="font-arabic text-2xl font-bold text-teal-800">{{ $t('app.name') }}</span>
        </router-link>
        
        <h2 class="text-3xl font-bold text-ink-900 mb-2 font-arabic text-balance">
          {{ $t('auth.welcomeBack') }}
        </h2>
        <p class="text-ink-600 mb-8 max-w-xs mx-auto md:mx-0 text-balance">
          {{ $t('auth.loginOptions') }}
        </p>

        <!-- Parent/Expert Login Option -->
        <div class="mt-auto">
          <div class="bg-surface rounded-2xl p-5 border border-ink-100 card-hover cursor-pointer group">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-full bg-teal-100 flex items-center justify-center text-teal-600 group-hover:bg-teal-600 group-hover:text-on-primary transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
                </svg>
              </div>
              <div class="text-start">
                <h3 class="font-bold text-ink-900">
                  {{ $t('auth.parentExpert') }}
                </h3>
                <p class="text-sm text-ink-500">
                  {{ $t('auth.loginWithEmail') }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Student Interactive Login -->
      <div class="p-6">
        <div class="card-nurturing border-2 border-teal-50 bg-teal-50/30 text-center">
          <div class="w-20 h-20 mx-auto bg-surface-bright rounded-full shadow-soft flex items-center justify-center mb-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-10 w-10 text-ochre-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          
          <h3 class="text-2xl font-bold text-ink-900 mb-2 font-arabic">
            {{ $t('auth.student') }}
          </h3>
          <p class="text-ink-600 mb-6 font-medium">
            {{ $t('auth.enterPin') }}
          </p>

          <!-- Playful Pin Input Placeholder -->
          <div
            class="flex justify-center gap-3 mb-8"
            dir="ltr"
          >
            <input
              type="password"
              maxlength="1"
              class="w-14 h-16 text-center text-2xl font-bold rounded-xl border-2 border-teal-200 bg-surface-bright focus:border-teal-500 focus:ring-4 focus:ring-teal-100 outline-none transition-all text-teal-800"
              placeholder="•"
            >
            <input
              type="password"
              maxlength="1"
              class="w-14 h-16 text-center text-2xl font-bold rounded-xl border-2 border-teal-200 bg-surface-bright focus:border-teal-500 focus:ring-4 focus:ring-teal-100 outline-none transition-all text-teal-800"
              placeholder="•"
            >
            <input
              type="password"
              maxlength="1"
              class="w-14 h-16 text-center text-2xl font-bold rounded-xl border-2 border-teal-200 bg-surface-bright focus:border-teal-500 focus:ring-4 focus:ring-teal-100 outline-none transition-all text-teal-800"
              placeholder="•"
            >
            <input
              type="password"
              maxlength="1"
              class="w-14 h-16 text-center text-2xl font-bold rounded-xl border-2 border-teal-200 bg-surface-bright focus:border-teal-500 focus:ring-4 focus:ring-teal-100 outline-none transition-all text-teal-800"
              placeholder="•"
            >
          </div>

          <button class="btn-primary w-full text-lg py-4 rounded-2xl shadow-teal">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 rtl:ms-2 ltr:me-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            {{ $t('auth.login') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
