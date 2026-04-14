# Ihsane Frontend — Developer Reference

> Vue 3 · TypeScript · Tailwind CSS 3 · Vite

---

## Semantic Color Scale

All colors in the Ihsane platform are expressed through **semantic design tokens** defined in `tailwind.config.js`.  
**Never** use hardcoded hex values (e.g., `#ffffff`, `#000000`) or bare Tailwind palette utilities (e.g., `bg-gray-100`, `text-red-500`).

### Token Map

| Token | Design Intent | Tailwind Class | Approximate Hex |
|---|---|---|---|
| `primary` | Brand accent – Teal | `text-primary` / `bg-primary` | `#00535b` |
| `on-primary` | Text on primary bg | `text-on-primary` | `#ffffff` (system) |
| `primary-container` | Soft primary surfaces | `bg-primary-container` | `#82d3de` |
| `primary-fixed` | Fixed primary tints | `bg-primary-fixed` | `#aceef7` |
| `primary-fixed-dim` | Muted primary tints | `bg-primary-fixed-dim` | `#82d3de` |
| `secondary` | Accent – Terracotta | `text-secondary` / `bg-secondary` | `#8c4e35` |
| `on-secondary` | Text on secondary bg | `text-on-secondary` | `#ffffff` (system) |
| `secondary-container` | Soft secondary surfaces | `bg-secondary-container` | `#f8d5c2` |
| `secondary-fixed` | Fixed secondary tints | `bg-secondary-fixed` | `#faddcf` |
| `tertiary` | Accent – Warm green | `text-tertiary` / `bg-tertiary` | `#3d6b4f` |
| `tertiary-container` | Soft tertiary surfaces | `bg-tertiary-container` | `#b8e5ca` |
| `tertiary-fixed` | Fixed tertiary tints | `bg-tertiary-fixed` | `#caeeda` |
| `tertiary-fixed-dim` | Muted tertiary tints | `bg-tertiary-fixed-dim` | `#aed4be` |
| `surface` | Page background | `bg-surface` | `#faf9f6` |
| `surface-bright` | Card / component bg | `bg-surface-bright` | `#faf9f6` |
| `surface-container-lowest` | Lowest elevation | `bg-surface-container-lowest` | `#f8f7f4` |
| `surface-container-low` | Low elevation | `bg-surface-container-low` | `#f4f3f1` |
| `surface-container` | Mid elevation | `bg-surface-container` | `#eeedea` |
| `surface-container-high` | High elevation | `bg-surface-container-high` | `#e8e7e4` |
| `surface-container-highest` | Highest elevation | `bg-surface-container-highest` | `#e3e2de` |
| `background` | App background | `bg-background` | `#faf9f6` |
| `on-surface` | Body text | `text-on-surface` | `#1c1b19` |
| `on-surface-variant` | Muted body text | `text-on-surface-variant` | `#48473e` |
| `outline` | Border strokes | `border-outline` | `#7a786e` |
| `outline-variant` | Subtle borders | `border-outline-variant` | `#cbc9be` |
| `error` | Error states | `text-error` / `bg-error` | `#c0392b` |
| `error-container` | Soft error surfaces | `bg-error-container` | `#ffd6d0` |
| `ink-body` | Alias for `on-surface` | `text-ink-body` | ~ `#1c1b19` |
| `ink-muted` | Alias for `on-surface-variant` | `text-ink-muted` | ~ `#48473e` |

### Usage Guidelines

```html
<!-- ✅ Correct: semantic tokens -->
<p class="text-on-surface-variant">مساعدة</p>
<div class="bg-surface-container-low border border-outline-variant">...</div>

<!-- ❌ Wrong: hardcoded hex or raw palette -->
<p class="text-gray-500">مساعدة</p>
<div style="background-color: #f4f3f1;">...</div>
```

---

## RTL / Logical CSS

The platform supports **both Arabic (RTL) and French (LTR)**. All layout properties must use [logical CSS](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_logical_properties_and_values):

| Physical ❌ | Logical ✅ |
|---|---|
| `pl-4`, `pr-4` | `ps-4`, `pe-4` |
| `ml-4`, `mr-4` | `ms-4`, `me-4` |
| `border-l`, `border-r` | `border-s`, `border-e` |
| `text-left`, `text-right` | `text-start`, `text-end` |
| `float-left`, `float-right` | `float-inline-start`, `float-inline-end` |
| `rounded-l-*`, `rounded-r-*` | `rounded-s-*`, `rounded-e-*` |

### Safe-area exemptions

Physical padding **only** for device safe-area insets (not layout) must be annotated:

```css
/* stylelint-disable-next-line plugin/use-logical-properties-and-values -- safe-area-inset */
padding-left: env(safe-area-inset-left);
```

---

## Linting

| Script | What it does |
|---|---|
| `npm run lint:design` | Runs Stylelint + ESLint to catch color and logical CSS violations |
| `npm run lint:design:fix` | Same as above, with auto-fix |
| `npm run audit:a11y` | Runs axe-core via Playwright against all routes (requires `npm run dev`) |
| `npm run audit:full` | Runs both `lint:design` and `audit:a11y` |

### Pre-commit enforcement

Husky runs `lint-staged` on every commit, targeting `*.vue`, `*.css`, and `*.ts` files through the config in `.lintstagedrc.json`.

---

## WCAG AA Compliance

The platform targets **WCAG 2.1 AA** (4.5:1 contrast for normal text, 3:1 for large text / UI components).

- All semantic token pairings have been validated for contrast.
- Run `npm run audit:a11y` to check all routes before pushing.
- Ensure every page has **exactly one `<h1>`** landmark (use `class="sr-only"` if it must be visually hidden).
- Navigation elements must use `<nav>`, page content must be inside `<main>`.
