<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const props = withDefaults(
  defineProps<{
    childName?: string
    childPin?: string
  }>(),
  {
    childName: '',
    childPin: '1234'
  }
)

const { t } = useI18n()
</script>

<template>
  <div class="bg-surface rounded-2xl p-6 shadow-soft border border-outline-variant space-y-6">
    <!-- Header -->
    <div class="text-center sm:text-start space-y-2">
      <div class="inline-flex items-center gap-2 px-3 py-1 bg-primary-container text-primary rounded-full text-xs font-semibold">
        <span class="material-symbols-outlined text-sm">rocket_launch</span>
        <span>{{ t('parent.onboarding.title') }}</span>
      </div>
      <h2 class="text-xl font-bold text-on-surface">
        {{ props.childName ? t('parent.hello', { name: props.childName }) : t('parent.onboarding.title') }}
      </h2>
      <p class="text-sm text-on-surface-variant leading-relaxed">
        {{ t('parent.onboarding.subtitle') }}
      </p>
    </div>

    <!-- Checklist Steps -->
    <div class="space-y-4">
      <!-- Step 1: Child PIN -->
      <div class="flex items-start gap-4 p-4 rounded-xl bg-surface-container-low border border-outline-variant transition-colors hover:bg-surface-container">
        <div class="w-9 h-9 rounded-full bg-primary text-on-primary font-bold flex items-center justify-center text-sm shrink-0">
          1
        </div>
        <div class="flex-1 space-y-1">
          <h3 class="font-semibold text-on-surface text-base">
            {{ t('parent.onboarding.step1Title') }}
          </h3>
          <p class="text-xs text-on-surface-variant">
            {{ t('parent.onboarding.step1Desc') }}
          </p>
          <div class="pt-2 flex items-center gap-2">
            <span class="text-xs font-medium text-on-surface-variant">PIN:</span>
            <span class="px-3 py-1 bg-surface-bright border border-outline text-primary font-mono text-base font-bold rounded-lg tracking-wider">
              {{ props.childPin || '1234' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Step 2: Take Diagnostic -->
      <div class="flex items-start gap-4 p-4 rounded-xl bg-surface-container-low border border-outline-variant transition-colors hover:bg-surface-container">
        <div class="w-9 h-9 rounded-full bg-primary text-on-primary font-bold flex items-center justify-center text-sm shrink-0">
          2
        </div>
        <div class="flex-1 space-y-1">
          <h3 class="font-semibold text-on-surface text-base">
            {{ t('parent.onboarding.step2Title') }}
          </h3>
          <p class="text-xs text-on-surface-variant">
            {{ t('parent.onboarding.step2Desc') }}
          </p>
          <div class="pt-2">
            <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-secondary-container text-secondary text-xs font-medium rounded-md">
              <span class="material-symbols-outlined text-sm">timer</span>
              10 {{ t('time.minutes', 'min') }}
            </span>
          </div>
        </div>
      </div>

      <!-- Step 3: View Insights -->
      <div class="flex items-start gap-4 p-4 rounded-xl bg-surface-container-low border border-outline-variant transition-colors hover:bg-surface-container">
        <div class="w-9 h-9 rounded-full bg-primary text-on-primary font-bold flex items-center justify-center text-sm shrink-0">
          3
        </div>
        <div class="flex-1 space-y-1">
          <h3 class="font-semibold text-on-surface text-base">
            {{ t('parent.onboarding.step3Title') }}
          </h3>
          <p class="text-xs text-on-surface-variant">
            {{ t('parent.onboarding.step3Desc') }}
          </p>
          <div class="pt-2">
            <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-tertiary-container text-tertiary text-xs font-medium rounded-md">
              <span class="material-symbols-outlined text-sm">analytics</span>
              {{ t('parent.smartInsights') }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
