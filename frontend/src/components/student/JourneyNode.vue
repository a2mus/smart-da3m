<script setup lang="ts">
import { computed } from 'vue';
import type { TaskState } from '@/models/stitchMockups';

const props = defineProps<{
  id: string;
  title: string;
  type: string;
  state: TaskState;
  score?: number;
}>();

const isCompleted = computed(() => props.state === 'completed');
const isActive = computed(() => props.state === 'in_progress');
const isLocked = computed(() => props.state === 'locked');

const iconName = computed(() => {
  if (isLocked.value) return 'lock';
  if (isCompleted.value) return 'done';
  if (props.type === 'video') return 'play_circle';
  if (props.type === 'quiz') return 'quiz';
  if (props.type === 'boss_battle') return 'sports_esports';
  return 'explore';
});
</script>

<template>
  <div
    class="flex items-center gap-6 z-10"
    :class="{ 'opacity-40': isLocked }"
  >
    <!-- Active Node Layout (Icon first on right side) -->
    <template v-if="isActive">
      <div 
        class="w-28 h-28 bg-primary rounded-[3rem] flex items-center justify-center shadow-2xl shadow-primary/40 ring-8 ring-primary-fixed-dim/30 animate-pulse min-w-[112px] cursor-pointer hover:scale-105 transition-transform"
      >
        <span
          class="material-symbols-outlined text-on-primary text-5xl"
          style="font-variation-settings: 'FILL' 1;"
        >{{ iconName }}</span>
      </div>
      <div class="flex flex-col">
        <span class="text-3xl font-black text-primary">{{ title }}</span>
        <span class="text-lg font-bold text-primary-container">المهمة الحالية</span>
      </div>
    </template>
    
    <!-- Completed Node Layout -->
    <template v-else-if="isCompleted">
      <div class="flex flex-col text-start">
        <span class="text-sm text-stone-500 font-label text-start w-full block">مكتمل <span v-if="score">{{ score }}%</span></span>
        <span class="text-lg font-bold text-secondary text-end">{{ title }}</span>
      </div>
      <div class="w-20 h-20 bg-secondary rounded-[2.5rem] flex items-center justify-center shadow-lg shadow-secondary/20 cursor-pointer min-w-[80px] hover:scale-105 transition-transform">
        <span
          class="material-symbols-outlined text-on-primary text-4xl"
          style="font-variation-settings: 'FILL' 1;"
        >{{ iconName }}</span>
      </div>
    </template>

    <!-- Locked Node Layout -->
    <template v-else>
      <div class="w-20 h-20 bg-stone-300 rounded-[2.5rem] flex items-center justify-center min-w-[80px]">
        <span class="material-symbols-outlined text-stone-500 text-4xl">{{ iconName }}</span>
      </div>
      <div class="flex flex-col">
        <span class="text-xl font-bold text-stone-600">{{ title }}</span>
        <span class="text-sm text-stone-500 font-label">قريباً</span>
      </div>
    </template>
  </div>
</template>
