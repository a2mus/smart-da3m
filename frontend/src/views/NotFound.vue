<script setup lang="ts">
// 404 Not Found page
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-6">
    <div class="nurturing-card p-8 text-center max-w-md">
      <h1 class="text-6xl font-bold text-primary-500 mb-4">404</h1>
      <h2 class="text-2xl font-bold mb-4">{{ $t('errors.notFound') }}</h2>
      <p class="text-warm-600 mb-6">{{ $t('errors.pageNotFound') }}</p>
      <router-link to="/" class="btn-primary inline-block">
        {{ $t('nav.goHome') }}
      </router-link>
    </div>
  </div>
</template>
