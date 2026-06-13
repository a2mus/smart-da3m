<script setup lang="ts">
import type { UserRole } from '@/types/auth'

const emit = defineEmits<{
  select: [role: UserRole]
}>()

const roles: { role: UserRole; labelAr: string; labelFr: string; descAr: string; icon: string; gradient: string }[] = [
  {
    role: 'PARENT',
    labelAr: 'ولي أمر',
    labelFr: 'Parent',
    descAr: 'تابع تقدم أطفالك، الإشعارات، والتوصيات الذكية',
    icon: 'family_restroom',
    gradient: 'from-[#8c4e35] to-amber-800',
  },
  {
    role: 'EXPERT',
    labelAr: 'خبير بيداغوجي',
    labelFr: 'Expert Pédagogique',
    descAr: 'أدر المحتوى التعليمي، حلل النتائج، وأدر المجموعات',
    icon: 'psychology',
    gradient: 'from-[#2e5a3b] to-emerald-800',
  },
  {
    role: 'STUDENT',
    labelAr: 'تلميذ',
    labelFr: 'Élève',
    descAr: 'استعرض رحلة التعلم، التشخيصات، ومسارات التقوية',
    icon: 'school',
    gradient: 'from-[#00535b] to-teal-700',
  },
]
</script>

<template>
  <div class="w-full">
    <h2 class="text-2xl font-bold text-on-surface text-center mb-2">
      اختر دورك
    </h2>
    <p class="text-on-surface-variant text-center mb-8">
      Sélectionnez votre rôle
    </p>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <button
        v-for="r in roles"
        :key="r.role"
        class="group relative bg-surface-container rounded-[1.5rem_0.75rem_1.5rem_0.75rem] p-6 text-center cursor-pointer
               border-2 border-surface-container-highest hover:border-primary/30
               shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-0.5 active:scale-[0.98]"
        @click="emit('select', r.role)"
      >
        <div
          :class="`w-14 h-14 mx-auto mb-4 rounded-full bg-gradient-to-br ${r.gradient} flex items-center justify-center shadow-md`"
        >
          <span
            class="material-symbols-outlined text-2xl text-on-primary"
            :data-icon="r.icon"
          >
            {{ r.icon }}
          </span>
        </div>
        <h3 class="text-lg font-bold text-on-surface mb-1">
          {{ r.labelAr }}
        </h3>
        <p class="text-xs text-on-surface-variant/70 font-medium mb-2">
          {{ r.labelFr }}
        </p>
        <p class="text-xs text-on-surface-variant leading-relaxed">
          {{ r.descAr }}
        </p>
      </button>
    </div>
  </div>
</template>
