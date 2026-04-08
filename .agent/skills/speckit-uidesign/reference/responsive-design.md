# Responsive Design Reference

## Mobile-First
Start with mobile base styles. Use `min-width` to layer complexity. Desktop-first means mobile loads unnecessary styles.

## Content-Driven Breakpoints
Don't chase devices — let content tell you where to break. Three usually suffice: ~640, ~768, ~1024px. Use `clamp()` for fluid values without breakpoints.

## Detect Input Method, Not Screen Size

```css
/* Fine pointer (mouse) */
@media (pointer: fine) { .button { padding: 8px 16px; } }

/* Coarse pointer (touch) */
@media (pointer: coarse) { .button { padding: 12px 20px; } }

/* Has hover capability */
@media (hover: hover) { .card:hover { transform: translateY(-2px); } }

/* No hover (touch) */
@media (hover: none) { /* Use active instead */ }
```

**Never rely on hover for functionality.**

## Safe Areas (Notch, Rounded Corners)

```css
body {
  padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
}
```

Enable: `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">`

## Responsive Images

```html
<img src="hero-800.jpg"
  srcset="hero-400.jpg 400w, hero-800.jpg 800w, hero-1200.jpg 1200w"
  sizes="(max-width: 768px) 100vw, 50vw"
  alt="Description">
```

Use `<picture>` for art direction (different crops).

## Layout Adaptation
- **Nav**: Hamburger+drawer (mobile) → compact horizontal (tablet) → full labels (desktop)
- **Tables**: Transform to cards on mobile (`display: block` + `data-label`)
- **Progressive disclosure**: `<details>/<summary>` for collapsible content

## Testing
Don't trust DevTools alone. Test on at least one real iPhone, one real Android, and a tablet. Cheap Android reveals real-world performance.
