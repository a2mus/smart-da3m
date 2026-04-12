<script setup lang="ts">
// Login view - Multi-role authentication
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-6">
    <div class="nurturing-card p-8 max-w-md w-full">
      <h2 class="text-2xl font-bold text-center mb-6">
        {{ $t('auth.welcomeBack') }}
      </h2>

      <div class="space-y-4">
        <p class="text-warm-600 text-center">
          {{ $t('auth.loginOptions') }}
        </p>

        <!-- Parent/Expert Login -->
        <div class="border-t border-warm-200 pt-4">
          <h3 class="font-medium mb-2">{{ $t('auth.parentExpert') }}</h3>
          <button class="btn-secondary w-full">
            {{ $t('auth.loginWithEmail') }}
          </button>
        </div>

        <!-- Student Login -->
        <div class="border-t border-warm-200 pt-4">
          <h3 class="font-medium mb-2">{{ $t('auth.student') }}</h3>
          <button class="btn-primary w-full">
            {{ $t('auth.loginWithPin') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
