<script setup lang="ts">
// Expert Dashboard - Content management overview
</script>

<template>
  <div class="min-h-screen p-6">
    <div class="nurturing-card p-6">
      <h1 class="text-2xl font-bold text-primary-600 mb-4">
        {{ $t('expert.dashboard') }}
      </h1>
      <p class="text-warm-600">
        {{ $t('expert.welcomeMessage') }}
      </p>

      <div class="mt-6 grid gap-4">
        <router-link
          to="/expert/modules"
          class="btn-secondary inline-block text-center"
        >
          {{ $t('expert.manageModules') }}
        </router-link>
      </div>
    </div>
  </div>
</template>
