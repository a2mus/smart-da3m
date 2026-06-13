# Data Model: Design Quality Enforcement

**Branch**: `003-design-quality-enforcement` | **Date**: 2026-04-14

## Entities

This feature is primarily a tooling/process enforcement feature. There are no database entities. The "data model" consists of configuration files and audit output structures.

### Semantic Color Token Registry

**Source**: `frontend/tailwind.config.js` → `theme.extend.colors`

| Token Name | Category | Current Value | Compliant? | Action |
|------------|----------|---------------|------------|--------|
| `surface` (DEFAULT) | warm | `#faf9f6` | ✅ | Keep |
| `surface-container` | warm | `#efeeeb` | ✅ | Keep |
| `surface-container-lowest` | warm | `#ffffff` | ❌ | Replace with `#faf9f6` |
| `surface-bright` | warm | `#faf9f6` | ✅ | Keep |
| `on-primary` | ink-on-dark | `#ffffff` | ❌ | Replace with `#faf9f6` |
| `on-error` | ink-on-dark | `#ffffff` | ❌ | Replace with `#faf9f6` |
| `on-secondary` | ink-on-dark | `#ffffff` | ❌ | Replace with `#faf9f6` |
| `on-tertiary` | ink-on-dark | `#ffffff` | ❌ | Replace with `#faf9f6` |
| `ink-800` | ink | `#292524` | ✅ | Add alias `ink-primary` |
| `ink-600` | ink | `#57534e` | ✅ | Add alias `ink-secondary` |
| `ink-400` | ink | `#a8a29e` | ✅ | Add alias `ink-muted` |
| `primary` | brand | `#00535b` | ✅ | Keep |
| `primary-container` | brand | `#006d77` | ✅ | Keep |
| `secondary` | accent | `#8c4e35` | ✅ | Keep |
| `secondary-container` | accent | `#ffad8f` | ✅ | Keep |
| `mint-500` | status-success | `#14b8a6` | ✅ | Keep |
| `amber-500` | status-warning | `#f59e0b` | ✅ | Keep |
| `rose-500` | status-error | `#e13666` | ✅ | Keep |
| `error` | status-error | `#ba1a1a` | ✅ | Keep |

### Shadow Token Registry

**Source**: `frontend/tailwind.config.js` → `theme.extend.boxShadow`

| Token Name | Current Value | Compliant? | Action |
|------------|---------------|------------|--------|
| `shadow-teal` | `rgba(0, 83, 91, 0.10)` | ✅ | Keep (brand-tinted) |
| `shadow-ochre` | `rgba(140, 78, 53, 0.08)` | ✅ | Keep (brand-tinted) |
| `shadow-soft` | `rgba(0, 0, 0, 0.05)` | ❌ | Replace with `rgba(26, 28, 26, 0.05)` |

### Lint Rule Configuration Schema

```
stylelint-config-ihsane/
├── color-ban-rules     → regex patterns matching #fff, #000, white, black, rgb(0,0,0), rgb(255,255,255)
├── logical-css-rules   → physical-to-logical property mappings
└── exemption-pattern   → /* physical-override: [justification] */ comment disables

eslint-plugin-ihsane/
├── banned-tw-classes   → bg-white, bg-black, text-white, text-black
├── physical-tw-classes → pl-*, pr-*, ml-*, mr-*, left-*, right-*
└── allowed-tw-classes  → ps-*, pe-*, ms-*, me-*, start-*, end-*
```

### Audit Finding Output Schema

Each audit run produces findings in this structure:

```
{
  "timestamp": "ISO 8601",
  "screen": "ParentDashboard | StudentDashboard | ExpertAnalytics | ...",
  "findings": [
    {
      "id": "unique-finding-id",
      "rule": "FR-002 | FR-010 | FR-020 | ...",
      "severity": "Critical | Warning | Info",
      "element": "CSS selector or file:line reference",
      "currentValue": "bg-white | margin-left: 1rem | contrast 3.2:1",
      "requiredValue": "bg-surface | margin-inline-start: 1rem | contrast ≥ 4.5:1",
      "remediation": "Replace bg-white with bg-surface"
    }
  ],
  "summary": {
    "critical": 0,
    "warning": 0,
    "info": 0,
    "passed": true
  }
}
```

## File Impact Map

### Files Requiring Color Remediation (~120 violations)

| File | Violation Count | Primary Issue |
|------|----------------|---------------|
| `views/student/Dashboard.vue` | ~22 | text-white, bg-white/*, #ffffff shadow |
| `views/StudentJourney.vue` | ~12 | text-white, bg-white/*, #ffffff shadow, rgba(0,0,0) |
| `views/Home.vue` | ~15 | text-white, bg-white |
| `views/LandingPage.vue` | ~8 | text-white |
| `views/Login.vue` | ~10 | bg-white |
| `views/ParentDashboard.vue` | ~6 | text-white, bg-white/* |
| `views/parent/Dashboard.vue` | ~6 | text-white, bg-white/* |
| `views/expert/Analytics.vue` | ~12 | text-white, border-white |
| `views/AnalyticsView.vue` | ~8 | text-white |
| `components/common/HeroSection.vue` | ~4 | bg-white |
| `components/expert/CompetencyHeatmap.vue` | ~2 | bg-white |
| `components/ui/IhsaneButton.vue` | ~2 | -ml-1, mr-2 (Tailwind physical) |
| `assets/main.css` | 2 | padding-left/right (safe-area exempt) |
| `tailwind.config.js` | 4 | #ffffff in token definitions |

### Files Requiring Logical CSS Remediation (~45 violations)

| File | Violation Count | Primary Issue |
|------|----------------|---------------|
| `views/expert/Analytics.vue` | ~10 | right-0, left-0, mr-72, left-8 |
| `views/AnalyticsView.vue` | ~8 | right-0, left-0, mr-72 |
| `views/student/Dashboard.vue` | ~6 | left-0, ml-auto, mr-auto, left-12 |
| `views/StudentJourney.vue` | ~4 | left-0 |
| `views/ParentDashboard.vue` | ~4 | -left-12, -right-8, left-0, right-0 |
| `views/parent/Dashboard.vue` | ~4 | -left-12, -right-8, left-0 |
| `views/Home.vue` | ~4 | -right-10, -left-10, -right-6, left-0 |
| `views/LandingPage.vue` | ~3 | left-0, -left-24, right-0 |
| `views/Login.vue` | ~1 | rtl:ml-2, ltr:mr-2 |
| `components/ui/IhsaneButton.vue` | ~1 | -ml-1, mr-2 |
| `components/expert/CompetencyHeatmap.vue` | ~2 | left-0, sticky left |
