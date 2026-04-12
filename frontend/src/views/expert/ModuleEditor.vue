<script setup lang="ts">
// Module Editor - Expert creates/edits content
import { useRoute } from 'vue-router'

const route = useRoute()
const moduleId = route.params.id
</script>

<template>
  <div class="min-h-screen p-6">
    <div class="nurturing-card p-6">
      <h1 class="text-2xl font-bold text-primary-600 mb-4">
        {{ $t('expert.editModule') }}
      </h1>
      <p class="text-warm-600">
        {{ $t('expert.editingModule') }}: {{ moduleId }}
      </p>
    </div>
  </div>
</template>
