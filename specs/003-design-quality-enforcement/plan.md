# Implementation Plan: Design Quality Enforcement

**Branch**: `003-design-quality-enforcement` | **Date**: 2026-04-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-design-quality-enforcement/spec.md`

## Summary

Enforce the Constitution's design system constraints (Article 3) through automated tooling and retroactive codebase remediation. Three enforcement layers: (1) **Stylelint** rules banning pure whites/blacks and physical CSS properties in `<style>` blocks, (2) **ESLint** rules banning Tailwind physical/banned utility classes in `<template>` blocks, (3) **axe-core** WCAG AA audits for contrast, semantic HTML, and touch targets. Pre-commit hooks (husky + lint-staged) provide instant developer feedback; CI pipeline blocks merges on Critical violations. All ~52 existing frontend files are remediated retroactively.

## Technical Context

**Language/Version**: TypeScript 5.6, Vue 3.5+, CSS (Tailwind 3.4)  
**Primary Dependencies**: Stylelint, stylelint-plugin-logical-css, eslint-plugin-tailwindcss, husky, lint-staged, @axe-core/cli  
**Storage**: N/A (tooling-only feature)  
**Testing**: Vitest (unit), Playwright + axe-core (a11y audit)  
**Target Platform**: Web (Chrome, Firefox, Safari, Edge)  
**Project Type**: Web application (Vue 3 SPA)  
**Performance Goals**: Pre-commit checks complete in < 5 seconds; full audit in < 5 minutes per screen  
**Constraints**: Must not break existing build; retroactive fixes must be visually validated  
**Scale/Scope**: ~52 frontend files, ~120 color violations, ~45 physical CSS violations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Article | Requirement | Status |
|---------|-------------|--------|
| 3.1 Design System | Pure whites/blacks banned; semantic tokens enforced | ✅ This feature enforces it |
| 3.2 Component Standards | Headless UI + Tailwind; naming convention | ✅ No conflict |
| 3.3 Accessibility | WCAG AA; 60px/44px touch targets; RTL-first | ✅ This feature enforces it |
| 3.4 Responsive | Mobile-first, tablet, desktop breakpoints | ✅ No conflict |
| 2.1 Testing | 80% coverage; Vitest + PyTest | ✅ Lint rules are tested via Vitest |
| 2.2 Code Style | ESLint + Prettier | ✅ Extended with design rules |
| 5.1 CI/CD | GitHub Actions lint + test + build | ✅ Extended with design checks |
| 1.4 Dependency Policy | < 100KB gzipped per new dep | ⚠️ Must verify Stylelint + axe-core bundle impact (dev-only, no production impact) |

**Gate Result**: ✅ PASS — All new dependencies are devDependencies (no production bundle impact).

## Project Structure

### Documentation (this feature)

```text
specs/003-design-quality-enforcement/
├── plan.md              # This file
├── research.md          # Phase 0: tool research & decisions
├── data-model.md        # Phase 1: token registry & violation map
├── quickstart.md        # Phase 1: developer onboarding guide
└── tasks.md             # Phase 2: task breakdown (via /speckit.tasks)
```

### Source Code (repository root)

```text
frontend/
├── .stylelintrc.json          # [NEW] Stylelint config with color + logical rules
├── .lintstagedrc.json         # [NEW] lint-staged config
├── .husky/
│   └── pre-commit             # [NEW] Pre-commit hook
├── package.json               # [MODIFY] Add devDependencies + scripts
├── tailwind.config.js         # [MODIFY] Fix #ffffff tokens + shadow-soft
├── src/
│   ├── assets/main.css        # [MODIFY] Safe-area exemption comments
│   ├── views/                 # [MODIFY] Remediate ~15 files
│   │   ├── student/Dashboard.vue
│   │   ├── StudentJourney.vue
│   │   ├── Home.vue
│   │   ├── LandingPage.vue
│   │   ├── Login.vue
│   │   ├── ParentDashboard.vue
│   │   ├── parent/Dashboard.vue
│   │   ├── expert/Analytics.vue
│   │   ├── AnalyticsView.vue
│   │   └── ...
│   ├── components/            # [MODIFY] Remediate ~5 files
│   │   ├── common/HeroSection.vue
│   │   ├── expert/CompetencyHeatmap.vue
│   │   ├── ui/IhsaneButton.vue
│   │   └── ...
│   └── scripts/               # [NEW] Audit scripts
│       └── audit-a11y.ts      # axe-core audit runner

.github/workflows/
└── deploy.yml                 # [MODIFY] Add design lint + a11y check steps
```

**Structure Decision**: This is a tooling + remediation feature layered onto the existing web application structure. No new modules or architectural changes — only configuration files, lint rules, and component fixes.

## Implementation Phases

### Phase 1: Foundation — Token Registry & Lint Configuration

**Goal**: Fix Tailwind config violations, install lint tooling, configure rules.

#### 1.1 Fix Tailwind Config Token Violations
- Replace `surface-container-lowest: "#ffffff"` → `"#faf9f6"`
- Replace `on-primary: "#ffffff"` → `"#faf9f6"`
- Replace `on-error: "#ffffff"` → `"#faf9f6"`
- Replace `on-secondary: "#ffffff"` → `"#faf9f6"`
- Replace `on-tertiary: "#ffffff"` → `"#faf9f6"`
- Replace `shadow-soft: 'rgba(0, 0, 0, 0.05)'` → `'rgba(26, 28, 26, 0.05)'`
- Add semantic aliases: `ink-primary: '#292524'`, `ink-secondary: '#57534e'`, `ink-muted: '#a8a29e'`

#### 1.2 Install Dev Dependencies
```bash
npm install --save-dev stylelint stylelint-config-standard stylelint-plugin-logical-css husky lint-staged
```

#### 1.3 Create Stylelint Configuration (`.stylelintrc.json`)
- Ban `#fff`, `#FFF`, `#ffffff`, `#FFFFFF`, `#000`, `#000000`, `white`, `black` via `declaration-property-value-disallowed-list`
- Ban `rgb(0,0,0)`, `rgb(255,255,255)`, `rgba(0,0,0,*)`, `rgba(255,255,255,*)` via regex patterns
- Enable `plugin/use-logical` from stylelint-plugin-logical-css (flag physical horizontal properties)
- Configure vertical property exemptions (`top`, `bottom`, `padding-top`, `padding-bottom`, `margin-top`, `margin-bottom`, `border-top`, `border-bottom`)
- Configure `/* physical-override: */` comment exemption pattern

#### 1.4 Extend ESLint Configuration
- Add rules to flag banned Tailwind classes: `bg-white`, `bg-black`, `text-white`, `text-black`
- Add rules to flag physical Tailwind utilities: `pl-*`, `pr-*`, `ml-*`, `mr-*`, `left-*`, `right-*`
- Suggest logical replacements in error messages

#### 1.5 Configure Pre-commit Hooks
- Initialize husky: `npx husky init`
- Create `.husky/pre-commit` running `npx lint-staged`
- Create `.lintstagedrc.json` targeting `*.vue`, `*.css`, `*.ts` files

#### 1.6 Add npm Scripts
```json
{
  "lint:design": "stylelint 'src/**/*.{vue,css}' && eslint --rule ihsane-design-rules src/",
  "lint:design:fix": "stylelint 'src/**/*.{vue,css}' --fix",
  "audit:a11y": "node scripts/audit-a11y.ts",
  "audit:full": "npm run lint:design && npm run audit:a11y"
}
```

**Verification**: Run `npm run lint:design` — should report existing violations (baseline count matches research findings).

---

### Phase 2: Retroactive Remediation — Color Violations

**Goal**: Fix all ~120 color violations across 15 files.

#### 2.1 Remediation Strategy

| Pattern | Replacement | Context |
|---------|-------------|---------|
| `text-white` on dark bg | `text-on-primary` / `text-on-secondary` / `text-surface-bright` | Icons/text on primary/secondary backgrounds |
| `bg-white` solid | `bg-surface` or `bg-surface-bright` | Card backgrounds |
| `bg-white/XX` alpha | `bg-surface-bright/XX` | Glassmorphism overlays |
| `border-white/XX` | `border-surface-bright/XX` | Subtle borders |
| `#ffffff` in inline style | CSS variable `var(--surface-bright)` | box-shadow definitions |
| `rgba(0,0,0,XX)` in shadow | `rgba(26,28,26,XX)` | Shadow definitions |

#### 2.2 File-by-File Remediation Order (highest violation count first)
1. `views/student/Dashboard.vue` (~22 violations)
2. `views/Home.vue` (~15 violations)
3. `views/StudentJourney.vue` (~12 violations)
4. `views/expert/Analytics.vue` (~12 violations)
5. `views/Login.vue` (~10 violations)
6. `views/LandingPage.vue` (~8 violations)
7. `views/AnalyticsView.vue` (~8 violations)
8. `views/ParentDashboard.vue` (~6 violations)
9. `views/parent/Dashboard.vue` (~6 violations)
10. `components/common/HeroSection.vue` (~4 violations)
11. `components/expert/CompetencyHeatmap.vue` (~2 violations)
12. Remaining components as discovered

**Verification**: After each file, run `npm run lint:design -- --filter <file>` to confirm zero violations.

---

### Phase 3: Retroactive Remediation — Logical CSS Properties

**Goal**: Fix all ~45 physical CSS / Tailwind violations.

#### 3.1 Tailwind Class Migration

| Physical | Logical | Notes |
|----------|---------|-------|
| `left-0` | `start-0` | Position |
| `right-0` | `end-0` | Position |
| `ml-auto` | `ms-auto` | Margin |
| `mr-auto` | `me-auto` | Margin |
| `ml-1` | `ms-1` | Margin |
| `mr-2` | `me-2` | Margin |
| `pl-*` | `ps-*` | Padding |
| `pr-*` | `pe-*` | Padding |
| `-left-X` | `-start-X` | Negative position |
| `-right-X` | `-end-X` | Negative position |
| `mr-72` | `me-72` | Fixed sidebar offset |
| `left-8` | `start-8` | FAB position |
| `left-12` | `start-12` | Button position |

#### 3.2 CSS Property Migration (main.css)
- `padding-left: env(safe-area-inset-left)` → Add `/* physical-override: safe-area insets are device-physical */` exemption comment
- `padding-right: env(safe-area-inset-right)` → Add exemption comment

#### 3.3 File-by-File Remediation Order
1. `views/expert/Analytics.vue` (~10 violations)
2. `views/AnalyticsView.vue` (~8 violations)
3. `views/student/Dashboard.vue` (~6 violations)
4. `views/StudentJourney.vue` (~4 violations)
5. `views/ParentDashboard.vue` (~4 violations)
6. `views/parent/Dashboard.vue` (~4 violations)
7. `views/Home.vue` (~4 violations)
8. `views/LandingPage.vue` (~3 violations)
9. `views/Login.vue` (~1 violation)
10. `components/ui/IhsaneButton.vue` (~1 violation)
11. `components/expert/CompetencyHeatmap.vue` (~2 violations)
12. `assets/main.css` (~2 violations — exempted)

**Verification**: Run `npm run lint:design` — zero violations. Toggle `dir="rtl"` in-browser on all screens and visually confirm correct mirroring.

---

### Phase 4: WCAG AA Audit Infrastructure

**Goal**: Create the axe-core audit pipeline and semantic HTML validation.

#### 4.1 Install axe-core
```bash
npm install --save-dev @axe-core/playwright
```

#### 4.2 Create Audit Script (`src/scripts/audit-a11y.ts`)
- Launches Vite dev server
- Opens each screen route via Playwright
- Runs axe-core with WCAG AA ruleset
- Checks contrast ratios (4.5:1 normal, 3:1 large text)
- Validates heading hierarchy (single h1, no skipped levels)
- Validates landmark elements
- Validates form labels
- Checks touch target sizing
- Outputs JSON report per screen

#### 4.3 Run Baseline Audit
- Execute against all 3 primary screens (Parent, Student, Expert)
- Document findings
- Remediate Critical findings (contrast failures, missing labels)
- Document Warning findings with justifications

#### 4.4 Semantic HTML Remediation
- Ensure single `<h1>` per view
- Add missing `<main>`, `<header>`, `<nav>`, `<footer>` landmarks
- Add `aria-label` to all interactive elements lacking visible text
- Add `<label>` associations to all form inputs
- Add meaningful `alt` text to images
- Verify focus indicators on all interactive elements

**Verification**: Run `npm run audit:a11y` — zero Critical findings.

---

### Phase 5: CI Pipeline Integration

**Goal**: Add design lint + a11y checks to GitHub Actions.

#### 5.1 Update `.github/workflows/deploy.yml`
- Add `lint:design` step after existing lint step
- Add `audit:a11y` step (start dev server → run axe audit → stop)
- Configure failure to block merge on Critical findings

#### 5.2 Documentation
- Update quickstart.md with final verified commands
- Create developer reference for semantic token scale
- Document exemption comment pattern

**Verification**: Push a test commit with a `bg-white` class → CI must fail. Fix and push → CI must pass.

---

### Phase 6: Visual Validation & Polish

**Goal**: Verify no visual regressions from remediation.

#### 6.1 RTL/LTR Visual Check
- Toggle direction on every screen
- Verify no overlapping text, misaligned buttons, or collapsed layouts
- Screenshot comparison (Arabic vs French)

#### 6.2 Color Consistency Check
- Verify `text-on-primary` contrast on primary backgrounds
- Verify `text-surface-bright` readability on dark backgrounds
- Verify shadow tinting is visually correct

#### 6.3 Build Verification
- `npm run build` — zero errors
- `npm run test` — all existing tests pass
- `npm run lint:design` — zero violations
- `npm run audit:a11y` — zero Critical findings

**Verification**: All success criteria SC-001 through SC-008 pass.

## Complexity Tracking

No constitution violations requiring justification. All changes are additive devDependencies and configuration — no production bundle impact, no architectural changes.
