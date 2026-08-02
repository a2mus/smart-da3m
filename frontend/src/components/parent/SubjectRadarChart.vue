<script setup lang="ts">
defineProps<{
  subjects: { name: string; score: number; competency_id?: string; competencyId?: string }[]
}>()
</script>

<template>
  <div class="w-full">
    <div
      v-if="subjects.length === 0"
      class="text-center py-8 text-ink-400"
    >
      لا توجد بيانات للمواد
    </div>
    <div
      v-else
      class="space-y-3"
    >
      <div
        v-for="s in subjects"
        :key="s.competency_id || s.competencyId || s.name"
        class="flex items-center gap-3"
      >
        <span class="w-24 text-sm font-medium text-ink-700 truncate text-end">{{ s.name }}</span>
        <div class="flex-1 h-4 bg-ink-100 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-700"
            :class="s.score >= 80 ? 'bg-mint-500' : s.score >= 60 ? 'bg-teal-500' : s.score >= 40 ? 'bg-amber-500' : 'bg-rose-400'"
            :style="{ width: s.score + '%' }"
          />
        </div>
        <span class="w-10 text-sm font-bold text-ink-600 text-start">{{ s.score }}%</span>
      </div>
    </div>
  </div>
</template>
