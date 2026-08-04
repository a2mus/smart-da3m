<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { UserRole } from '@/types/auth'

const { t } = useI18n()

const emit = defineEmits<{
  select: [role: UserRole]
}>()

const roles: { role: UserRole; titleKey: string; subKey: string; descKey: string; icon: string; gradient: string }[] = [
  {
    role: 'PARENT',
    titleKey: 'roles.parent',
    subKey: 'roles.parentSub',
    descKey: 'roles.parentDesc',
    icon: 'family_restroom',
    gradient: 'from-[#8c4e35] to-amber-800',
  },
  {
    role: 'EXPERT',
    titleKey: 'roles.expert',
    subKey: 'roles.expertSub',
    descKey: 'roles.expertDesc',
    icon: 'psychology',
    gradient: 'from-[#2e5a3b] to-emerald-800',
  },
  {
    role: 'STUDENT',
    titleKey: 'roles.student',
    subKey: 'roles.studentSub',
    descKey: 'roles.studentDesc',
    icon: 'school',
    gradient: 'from-[#00535b] to-teal-700',
  },
]
</script>

<template>
  <div class="w-full">
    <h2 class="text-2xl font-bold text-on-surface text-center mb-6">
      {{ t('roles.selectRole', 'اختر دورك') }}
    </h2>
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
          {{ t(r.titleKey) }}
        </h3>
        <p class="text-xs text-on-surface-variant/70 font-medium mb-2">
          {{ t(r.subKey) }}
        </p>
        <p class="text-xs text-on-surface-variant leading-relaxed">
          {{ t(r.descKey) }}
        </p>
      </button>
    </div>
  </div>
</template>
