# Motion Design Reference

## The 100/300/500 Rule

| Duration | Use Case | Examples |
|----------|----------|----------|
| 100-150ms | Instant feedback | Button press, toggle, color change |
| 200-300ms | State changes | Menu open, tooltip, hover |
| 300-500ms | Layout changes | Accordion, modal, drawer |
| 500-800ms | Entrance animations | Page load, hero reveals |

**Exit = ~75% of enter duration.**

## Easing: Exponential Curves

| Curve | Use For | CSS |
|-------|---------|-----|
| ease-out | Entering | `cubic-bezier(0.16, 1, 0.3, 1)` |
| ease-in | Leaving | `cubic-bezier(0.7, 0, 0.84, 0)` |
| ease-in-out | Toggles | `cubic-bezier(0.65, 0, 0.35, 1)` |

```css
--ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);   /* Recommended default */
--ease-out-quint: cubic-bezier(0.22, 1, 0.36, 1);   /* More dramatic */
--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);     /* Snappy */
```

**NEVER bounce or elastic.** They're tacky. Real objects decelerate smoothly.

## Only Animate `transform` and `opacity`
Everything else causes layout recalculation.
For height: use `grid-template-rows: 0fr → 1fr`.

## Staggered Animations
```css
animation-delay: calc(var(--i, 0) * 50ms);
```
Cap total stagger: 10 items × 50ms = 500ms max.

## Reduced Motion (REQUIRED)

```css
@media (prefers-reduced-motion: reduce) {
  .card { animation: fade-in 200ms ease-out; } /* Crossfade instead */
}
```

Preserve: progress bars, spinners (slowed), focus indicators.

## Perceived Performance
- **80ms threshold**: Under 80ms feels instant
- **Preemptive start**: Begin transitions while loading
- **Optimistic UI**: Update immediately, sync later (low-stakes actions)
- **Ease-in toward completion**: Makes tasks feel shorter (peak-end effect)

## Performance
- `will-change` only when animation imminent (`:hover`, `.animating`)
- Intersection Observer for scroll-triggered animations
- Create motion tokens for consistency
