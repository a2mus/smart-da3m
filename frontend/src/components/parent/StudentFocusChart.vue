<script setup lang="ts">
import { mockUiState } from '@/services/mockUiState';

const sessions = mockUiState.analytics.sessions;

// Calculate height percentage based on focus score
const getBarHeight = (score: number) => `${score}%`;

// Return appropriate colors based on the score
const getBarColorClass = (score: number) => {
  if (score >= 90) return 'bg-primary';
  if (score >= 80) return 'bg-primary-fixed-dim';
  if (score >= 70) return 'bg-secondary-container';
  return 'bg-error';
};
</script>

<template>
  <div class="bg-surface-bright p-6 rounded-[2rem] border border-outline-variant/10 flex flex-col justify-between h-full">
    <div>
      <div class="flex justify-between items-start mb-4">
        <div class="w-12 h-12 bg-primary-fixed rounded-2xl flex items-center justify-center text-primary">
          <span class="material-symbols-outlined">insights</span>
        </div>
        <span class="text-tertiary font-bold text-sm bg-tertiary-fixed/30 px-3 py-1 rounded-full">
          معدل التركيز
        </span>
      </div>
      <p class="text-slate-500 text-sm font-bold">
        متوسط تركيز الطالب
      </p>
      <h3 class="text-4xl font-black text-primary font-['Inter'] mt-1">
        {{ mockUiState.analytics.weeklyFocusAverage }}<span class="text-xl">%</span>
      </h3>
    </div>
    
    <div class="mt-6 h-16 w-full bg-slate-50 rounded-lg overflow-hidden relative flex items-end gap-1 px-2 pt-2 pb-0">
      <div 
        v-for="session in sessions" 
        :key="session.id"
        class="w-full rounded-t-sm transition-all hover:opacity-80 cursor-pointer relative group"
        :class="getBarColorClass(session.focusScore)"
        :style="{ height: getBarHeight(session.focusScore) }"
      >
        <!-- Tooltip -->
        <div class="absolute -top-10 start-1/2 -translate-x-1/2 bg-inverse-surface text-inverse-on-surface text-xs py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none">
          {{ session.focusScore }}% - {{ session.durationMinutes }}د
        </div>
      </div>
    </div>
  </div>
</template>
