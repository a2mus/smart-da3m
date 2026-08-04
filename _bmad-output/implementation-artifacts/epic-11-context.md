# Epic 11 Context: UX Gap Remediation & Production Bug Fixes

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Address all UX friction points, persona gaps, and production bugs identified during the 2026-08-03 UX/UI evaluation (`docs/ux_ui_analysis_and_gaps.md`). Elevate the user experience from MVP to a friction-free learning environment across student, parent, and expert roles.

## Stories

- Story 11.1: Fix Register.vue Route Redirection Bug
- Story 11.2: Fix auth.ts useI18n Scope Exception
- Story 11.3: Defensive API Payload Normalization in dashboardService
- Story 11.4: Global Language Toggle in App Header
- Story 11.5: Diagnostic Resume Banner on Student Dashboard
- Story 11.6: Parent PIN Management Modal
- Story 11.7: First-Time Parent Onboarding & Empty State Checklist
- Story 11.8: Live Preview Toggle in Expert Question Builder

## Requirements & Constraints

- Fix high-impact routing bugs, i18n initialization exceptions, and payload structure discrepancies.
- Improve parent onboarding and visibility into child credentials/PINs and diagnostic progress.
- Provide smooth Arabic (RTL) / French (LTR) toggle support across all pages.
- Ensure all components comply with Vue 3 composition API, Pinia stores, and Tailwind CSS patterns.

## Technical Decisions

- Use Vue I18n global singleton (`i18n.global.t`) inside Pinia store helpers when outside setup context.
- Use logical CSS properties (`ps-*`, `pe-*`, `start-*`, `end-*`) for RTL/LTR support.
- Normalize API list responses defensively: `(response.data.items || response.data)`.
- Use Pinia stores for user state, active child state, and session state.

## UX & Interaction Patterns

- Parent Dashboard: First-time parent experience with zero diagnostic history displays step-by-step onboarding checklist instead of empty analytics/charts.
- Onboarding Checklist steps:
  1. Give child 4-digit PIN
  2. Have child take 10-minute diagnostic test
  3. View insights & recommendations once completed
- When first diagnostic session completes, checklist automatically transitions to real analytics charts.
