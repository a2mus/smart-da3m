<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import type { OrganizationClaim } from '@/types/auth'

const authStore = useAuthStore()
const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const selectOrganization = (org: OrganizationClaim) => {
  if (authStore.activeOrganizationId !== org.id) {
    authStore.setActiveOrganization(org.id)
    isOpen.value = false
    window.location.reload()
  } else {
    isOpen.value = false
  }
}

const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

const getOrgIcon = (type: string) => {
  return type === 'SCHOOL' ? '🏫' : '🏠'
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div
    v-if="authStore.hasMultipleOrganizations"
    ref="dropdownRef"
    class="relative inline-block text-start"
  >
    <button
      type="button"
      class="flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-soft bg-surface-container-low hover:bg-surface-container-high text-on-surface transition-colors border border-outline-variant touch-target focus:outline-none focus:ring-2 focus:ring-primary"
      aria-haspopup="true"
      :aria-expanded="isOpen"
      @click="toggleDropdown"
    >
      <span class="text-base">{{ getOrgIcon(authStore.activeOrganization?.type || 'HOUSEHOLD') }}</span>
      <span class="truncate max-w-[140px] md:max-w-[200px]">
        {{ authStore.activeOrganization?.name || authStore.activeOrganization?.id || 'Organization' }}
      </span>
      <svg
        class="w-4 h-4 transition-transform duration-200"
        :class="{ 'rotate-180': isOpen }"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M19 9l-7 7-7-7"
        />
      </svg>
    </button>

    <div
      v-if="isOpen"
      class="absolute z-50 mt-1 w-56 rounded-soft bg-surface-bright shadow-lg border border-outline-variant py-1 focus:outline-none end-0"
    >
      <button
        v-for="org in authStore.organizations"
        :key="org.id"
        type="button"
        class="w-full text-start flex items-center justify-between px-4 py-2.5 text-sm transition-colors hover:bg-surface-container"
        :class="{
          'bg-surface-container-high font-semibold text-primary': org.id === authStore.activeOrganizationId,
          'text-on-surface': org.id !== authStore.activeOrganizationId
        }"
        @click="selectOrganization(org)"
      >
        <div class="flex items-center gap-2 truncate">
          <span>{{ getOrgIcon(org.type) }}</span>
          <span class="truncate">{{ org.name || org.id }}</span>
        </div>
        <svg
          v-if="org.id === authStore.activeOrganizationId"
          class="w-4 h-4 text-primary shrink-0 ms-2"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M5 13l4 4L19 7"
          />
        </svg>
      </button>
    </div>
  </div>
</template>