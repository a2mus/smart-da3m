# Quickstart: Design Quality Enforcement

**Branch**: `003-design-quality-enforcement`

## Prerequisites

- Node.js 18+
- pnpm or npm
- Git

## Setup (one-time)

```bash
# 1. Switch to feature branch
git checkout 003-design-quality-enforcement

# 2. Install new dev dependencies
cd frontend
npm install --save-dev stylelint stylelint-config-standard stylelint-plugin-logical-css husky lint-staged @axe-core/cli

# 3. Initialize husky
npx husky init

# 4. Verify lint configuration
npm run lint:design   # Should report current violations
npm run audit:a11y    # Should run axe-core audit
```

## Key Commands

| Command | Purpose |
|---------|---------|
| `npm run lint:design` | Run Stylelint + ESLint design checks |
| `npm run lint:design:fix` | Auto-fix where possible |
| `npm run audit:a11y` | Run WCAG AA axe-core audit |
| `npm run audit:full` | Combined design lint + a11y audit |

## Workflow

1. **Before coding**: Understand the semantic token scale (see `tailwind.config.js` → `theme.extend.colors`)
2. **While coding**: Use semantic tokens (`bg-surface`, `text-ink-800`) not raw values
3. **Before commit**: Pre-commit hook runs automatically via husky
4. **On PR**: CI pipeline blocks merge on Critical findings
5. **Polish phase**: Run full audit (`npm run audit:full`)

## Common Fixes

| Violation | Fix |
|-----------|-----|
| `bg-white` | `bg-surface` or `bg-surface-bright` |
| `text-white` | `text-on-primary` (on dark bg) or `text-surface-bright` |
| `text-black` | `text-ink-800` or `text-on-surface` |
| `#ffffff` in style | `var(--surface-bright)` |
| `#000000` in style | `var(--ink-800)` or `var(--on-surface)` |
| `pl-4` | `ps-4` |
| `mr-2` | `me-2` |
| `ml-auto` | `ms-auto` |
| `left-0` | `start-0` |
| `right-0` | `end-0` |
| `margin-left` | `margin-inline-start` |
| `padding-right` | `padding-inline-end` |
| `text-align: left` | `text-align: start` |
