# Color & Contrast Reference

## Use OKLCH, Not HSL

OKLCH is perceptually uniform — equal steps in lightness *look* equal.

```css
--color-primary: oklch(60% 0.15 250);      /* Blue */
--color-primary-light: oklch(85% 0.08 250); /* Lighter = reduce chroma */
--color-primary-dark: oklch(35% 0.12 250);
```

**Key**: Reduce chroma toward white/black. High chroma at extreme lightness = garish.

## Tinted Neutrals (Never Pure Gray)

```css
/* Dead — no personality */
--gray-100: oklch(95% 0 0);

/* Warm-tinted (add brand warmth) */
--gray-100: oklch(95% 0.01 60);

/* Cool-tinted (tech, professional) */
--gray-100: oklch(95% 0.01 250);
```

Chroma 0.01 is tiny but perceptible. Creates subconscious cohesion.

## Palette Structure

| Role | Purpose | Shades |
|------|---------|--------|
| Primary | Brand, CTAs | 1 color, 3-5 shades |
| Neutral | Text, backgrounds | 9-11 shade scale |
| Semantic | Success/error/warning/info | 4 colors, 2-3 shades each |
| Surface | Cards, modals | 2-3 elevation levels |

Skip secondary/tertiary unless truly needed. One accent color works.

## The 60-30-10 Rule (Visual Weight)
- **60%**: Neutral backgrounds, white space
- **30%**: Secondary — text, borders, inactive
- **10%**: Accent — CTAs, highlights, focus

## WCAG Requirements

| Content | AA Min | AAA Target |
|---------|--------|------------|
| Body text | 4.5:1 | 7:1 |
| Large text (18px+) | 3:1 | 4.5:1 |
| UI components | 3:1 | 4.5:1 |
| Placeholder text | **4.5:1** (commonly fails!) | |

## Dangerous Combinations
- Light gray on white (#1 fail)
- **Gray on any colored background** — use shade of background instead
- Red on green (8% of men affected)
- Blue on red (vibrates)
- Yellow on white (always fails)

## Never Pure Black or Pure White
Real shadows have color cast. Even chroma 0.005-0.01 feels natural.

## Dark Mode ≠ Inverted Light Mode

| Light Mode | Dark Mode |
|------------|-----------|
| Shadows for depth | Lighter surfaces for depth |
| Dark text on light | Light text on dark (reduce weight) |
| Vibrant accents | Desaturate slightly |
| White backgrounds | Dark gray oklch(12-18%) |

```css
:root[data-theme="dark"] {
  --surface-1: oklch(15% 0.01 250);
  --surface-2: oklch(20% 0.01 250);
  --surface-3: oklch(25% 0.01 250);
  --body-weight: 350; /* Not 400 */
}
```

## Token Architecture
Two layers: primitive (`--blue-500`) → semantic (`--color-primary: var(--blue-500)`).
Dark mode redefines semantic layer only.
