# Research: Design Quality Enforcement

**Branch**: `003-design-quality-enforcement` | **Date**: 2026-04-14

## R1: Static Linting for Banned Colors in Vue + Tailwind

**Decision**: Use Stylelint with custom regex rules for `<style>` blocks AND a custom ESLint rule for Tailwind classes in `<template>` blocks.

**Rationale**: The codebase has two enforcement surfaces:
1. CSS `<style>` blocks — Stylelint's `declaration-property-value-disallowed-list` and `color-no-hex` family rules can catch raw `#FFF`/`#000`/`rgb(0,0,0)` values.
2. Tailwind utility classes in `<template>` — ESLint with `eslint-plugin-tailwindcss` can flag banned class names (`bg-white`, `text-black`, `pl-*`, `ml-*`).

**Alternatives considered**:
- PostCSS plugin only → Misses template-level Tailwind classes
- ESLint only → Poor at parsing CSS syntax in `<style>` blocks
- Custom grep script → No IDE integration, no auto-fix suggestions

## R2: Logical CSS Property Enforcement

**Decision**: Use Stylelint `plugin-logical-css` for CSS blocks, combined with `eslint-plugin-tailwindcss` classname regex for Tailwind physical utilities.

**Rationale**: `stylelint-plugin-logical-css` is a purpose-built plugin that flags physical properties (`margin-left`, `padding-right`, etc.) and suggests logical replacements. For Tailwind utilities (`pl-*`, `mr-*`), the ESLint custom rule handles enforcement at the template level.

**Alternatives considered**:
- Custom PostCSS transform → Auto-replacement is risky; better to flag and let developers choose
- `postcss-logical` polyfill → Transforms at build time, but doesn't educate developers or prevent future violations

## R3: WCAG AA Audit Tooling

**Decision**: Use `@axe-core/cli` (or Playwright + axe-core) for programmatic WCAG AA audits against rendered pages, plus a manual checklist for semantic HTML structure review.

**Rationale**: axe-core is the industry standard for WCAG compliance testing. It catches contrast violations, missing labels, heading hierarchy issues, and landmark structure. Running it via Playwright against dev server pages provides accurate rendered-DOM testing.

**Alternatives considered**:
- Lighthouse CI → Good for general audits but less customizable for specific WCAG AA rules
- pa11y → Strong but less actively maintained than axe-core
- Manual-only review → Not reproducible; misses regressions

## R4: Pre-commit Hook Infrastructure

**Decision**: Use `husky` + `lint-staged` for pre-commit hooks.

**Rationale**: The project already uses npm (package.json/pnpm-lock.yaml). Husky is the standard pre-commit tool for Node.js projects. `lint-staged` ensures only staged files are linted (fast feedback). This aligns with Constitution Article 5.1 (CI/CD pipeline) without adding Python pre-commit as a dependency.

**Alternatives considered**:
- `pre-commit` (Python) → Adds Python dependency to frontend-only workflow
- `lefthook` → Less ecosystem adoption in Vue/Tailwind projects
- Git hooks directly → No staged-file filtering, harder to maintain

## R5: Existing Violation Baseline Assessment

**Decision**: Remediate existing violations in a single sweep before enabling enforcement.

**Findings from codebase scan**:
- **~120 color violations** across 15 files (bg-white, text-white, #ffffff in shadows, bg-white/*, rgba(0,0,0,*))
- **~45 physical CSS violations** across 12 files (left-0, right-0, ml-auto, mr-auto, -left-*, -right-*)
- **3 Tailwind config violations**: `surface-container-lowest: "#ffffff"`, `on-error: "#ffffff"`, `on-primary: "#ffffff"` use banned `#ffffff`
- **1 shadow violation**: `shadow-soft` uses `rgba(0,0,0,0.05)` — banned pure-black shadow
- **2 main.css violations**: `padding-left`/`padding-right` for safe-area insets

**Approach**: Fix Tailwind config first (token definitions), then sweep components file-by-file, then enable lint rules. Safe-area insets in main.css receive a `/* physical-override: safe-area insets are device-physical */` exemption comment.

## R6: Semantic Token Completeness

**Decision**: The existing Tailwind config already provides a comprehensive token set. We need to add two missing categories:
1. `ink-primary`/`ink-secondary`/`ink-muted` aliases (currently `ink-800`/`ink-600`/`ink-400`)
2. Replacement values for `surface-container-lowest` (currently `#ffffff`), `on-error` and `on-primary` (currently `#ffffff`)

**Rationale**: The `ink` scale exists but lacks semantic aliases. The three `#ffffff` tokens need replacement with the closest approved warm-white values (e.g., `#faf9f6` for surface-container-lowest, `#faf9f6` for on-primary/on-error since they're used on dark backgrounds where cream-white is visually equivalent).
