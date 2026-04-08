# Typography Reference

## Vertical Rhythm
Line-height = base unit for ALL vertical spacing. If body is `line-height: 1.5` on `16px` (= 24px), spacing should be multiples of 24px.

## Modular Scale — 5-Size System

| Role | Ratio | Use Case |
|------|-------|----------|
| xs | 0.75rem | Captions, legal |
| sm | 0.875rem | Secondary UI, metadata |
| base | 1rem | Body text |
| lg | 1.25-1.5rem | Subheadings, lead |
| xl+ | 2-4rem | Headlines, hero |

Ratios: 1.25 (major third), 1.333 (perfect fourth), 1.5 (perfect fifth). Pick one.

## Readability
- Use `ch` for measure: `max-width: 65ch`
- Increase line-height for light-on-dark (+0.05-0.1)
- 45-75 characters optimal line length

## Distinctive Fonts (NOT: Inter, Roboto, Arial, Open Sans, Lato, Montserrat)

| Instead of | Try |
|------------|-----|
| Inter | Instrument Sans, Plus Jakarta Sans, Outfit |
| Roboto | Onest, Figtree, Urbanist |
| Open Sans | Source Sans 3, Nunito Sans, DM Sans |
| Editorial | Fraunces, Newsreader, Lora |

## Pairing
One font in multiple weights > two competing fonts. When pairing, contrast on multiple axes:
- Serif + Sans (structure)
- Geometric + Humanist (personality)
- Condensed display + Wide body (proportion)

**Never pair similar-but-not-identical fonts.**

## Web Font Loading

```css
@font-face {
  font-family: 'CustomFont';
  src: url('font.woff2') format('woff2');
  font-display: swap;
}

/* Match fallback metrics */
@font-face {
  font-family: 'CustomFont-Fallback';
  src: local('Arial');
  size-adjust: 105%;
  ascent-override: 90%;
  descent-override: 20%;
  line-gap-override: 10%;
}
```

## Fluid Type
- **Marketing/content pages**: `clamp(min, preferred, max)` headings
- **Product UI/dashboards**: Fixed `rem` scales (no major design system uses fluid in product UI)
- **Body text**: Always fixed

## OpenType Features

```css
.data-table { font-variant-numeric: tabular-nums; }
abbr { font-variant-caps: all-small-caps; }
code { font-variant-ligatures: none; }
body { font-kerning: normal; }
```

## Accessibility
- Never disable zoom (`user-scalable=no`)
- Use rem/em for font sizes (respects browser settings)
- Minimum 16px body text
- Text links need 44px+ tap targets via padding
