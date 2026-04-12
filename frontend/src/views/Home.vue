<script setup lang="ts">
// Home view - Landing page for Ihsane platform
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center p-6">
    <div class="nurturing-card p-8 max-w-md w-full text-center">
      <h1 class="text-4xl font-bold text-primary-600 mb-4">
        {{ $t('app.name') }}
      </h1>
      <p class="text-warm-600 mb-8">
        {{ $t('app.tagline') }}
      </p>

      <div class="space-y-4">
        <router-link
          to="/login"
          class="btn-primary w-full inline-block"
        >
          {{ $t('auth.login') }}
        </router-link>
      </div>
    </div>
  </div>
</template>
