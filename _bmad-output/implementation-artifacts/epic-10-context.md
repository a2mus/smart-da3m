# Epic 10 Context: Bilingual Completeness & i18n Polish

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

The platform must support Arabic (RTL, primary language) and French (LTR, secondary language) across the entire application interface with no hardcoded strings or layout breakage. This epic extracts remaining hardcoded text strings into localization key files, populates missing translation keys, bans physical direction utility classes in favor of logical equivalents, and enforces automated lint rules for layout direction compliance.

## Stories

- Story 10.1: Extract All Hardcoded Strings into i18n Keys
- Story 10.2: RTL/LTR Compliance Verification & Lint Enforcement

## Requirements & Constraints

- Instant AR/FR Language Switch: Switching between Arabic and French must occur immediately without reloading the page or losing active view state (FR-28).
- Full String Externalization: All user-facing text strings in Vue components, views, modals, and store notifications must use `$t()` or `t()` functions. No raw Arabic or French text may remain in template markup.
- Localization Key Coverage: Populate missing translation keys for passport tasks, remediation flows, validation queues, grade descriptions, alert actions, and error messages across `ar.json` and `fr.json`.
- Logical CSS Compliance: Physical direction utility classes (`pl-*`, `pr-*`, `left-*`, `right-*`, `text-left`, `text-right`, `ml-*`, `mr-*`) are strictly prohibited. Layouts must use logical equivalents (`ps-*`, `pe-*`, `start-*`, `end-*`, `text-start`, `text-end`, `ms-*`, `me-*`) to flip orientation cleanly between RTL and LTR.
- Dynamic Locale Formatting: Date, time, and numeric formatting must call `toLocaleDateString()` and related methods with the current active locale rather than a hardcoded locale string.

## Technical Decisions

- i18n Framework: Uses `vue-i18n` (^10.0.5) with locale files located in `src/locales/` (`ar.json` and `fr.json`).
- Backend Error Localization: Backend endpoints emit structured machine codes (`detail.code`). The frontend maps these machine codes to localized human messages through `vue-i18n`.
- Automated Linting: ESLint and Tailwind lint configuration rules enforce logical CSS utility usage across all `.vue` and `.ts` files, blocking physical direction utility classes during build and pre-commit checks.
- Document Direction Control: Root HTML/body attributes (`dir="rtl"` and `dir="ltr"`) update dynamically when the active locale changes in the i18n store, triggering Tailwind `rtl:` and `ltr:` variant rules.
- Typography Switching: Font families switch automatically according to active direction, using Tajawal/Cairo fonts for Arabic and Plus Jakarta Sans for French.

## UX & Interaction Patterns

- Language Switcher: Header navigation control allows instant switching between Arabic and French.
- Responsive Layout Alignment: Form controls, table cells, modal dialogs, alert badges, and action buttons align automatically to the start edge of the active layout direction.
- Directional Component Handling: Interactive elements with intrinsic directionality (back buttons, breadcrumb chevrons, pagination arrows, media player controls) reverse orientation when switching between RTL and LTR views.

## Cross-Story Dependencies

- External Dependencies: Independent epic. Can run in parallel with or after any other epic.
- Internal Dependencies: Story 10.2 builds upon the comprehensive string extraction and key mapping completed in Story 10.1.
