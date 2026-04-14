<script setup lang="ts">
import { mockUiState } from '@/services/mockUiState';

const notifications = mockUiState.notifications;
</script>

<template>
  <section class="space-y-4 pb-8">
    <h3 class="text-xl font-bold text-primary">
      آخر التنبيهات
    </h3>
    <div class="grid grid-cols-2 gap-3">
      <!-- Dynamic list based on notifications -->
      <div 
        v-for="notif in notifications" 
        :key="notif.id"
        class="p-4 rounded-3xl flex flex-col justify-between"
        :class="{
          'bg-tertiary-fixed-dim': notif.type === 'achievement',
          'bg-error-container col-span-2 row-span-2': notif.severity === 'high',
          'bg-secondary-fixed row-span-2 h-auto': notif.type === 'alert' && notif.severity !== 'high',
          'bg-surface-container h-32': notif.type === 'system' || (notif.type === 'achievement' && notif.severity !== 'high')
        }"
      >
        <span 
          class="material-symbols-outlined"
          :class="{
            'text-tertiary-container': notif.type === 'achievement',
            'text-on-secondary-fixed': notif.type === 'alert' && notif.severity !== 'high',
            'text-error': notif.severity === 'high',
            'text-outline': notif.type === 'system'
          }"
        >
          {{ notif.type === 'achievement' ? 'emoji_events' : (notif.type === 'system' ? 'info' : 'warning') }}
        </span>
        
        <div v-if="notif.type === 'alert'">
          <span
            class="text-xl font-black font-label"
            :class="notif.severity === 'high' ? 'text-error' : 'text-on-secondary-fixed'"
          >
            تنبيه
          </span>
          <p
            class="text-xs font-bold mt-1"
            :class="notif.severity === 'high' ? 'text-on-error-container' : 'text-on-secondary-fixed-variant'"
          >
            {{ notif.message }}
          </p>
        </div>
        
        <span
          v-else
          class="text-sm font-bold"
          :class="notif.type === 'achievement' ? 'text-on-tertiary-fixed-variant' : 'text-on-surface'"
        >
          {{ notif.message }}
        </span>
      </div>
    </div>
  </section>
</template>
