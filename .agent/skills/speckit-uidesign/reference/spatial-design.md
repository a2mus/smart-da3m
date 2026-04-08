# Spatial Design Reference

## 4pt Base Grid (Not 8pt)
8pt is too coarse — you'll need 12px. Use 4pt: **4, 8, 12, 16, 24, 32, 48, 64, 96px**.

## Semantic Token Naming
Name by relationship (`--space-sm`, `--space-lg`), not value (`--spacing-8`).
Use `gap` instead of margins — eliminates collapse and cleanup hacks.

## Self-Adjusting Grid
```css
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
```
For complex layouts, use named grid areas and redefine at breakpoints.

## The Squint Test
Blur your eyes. Can you identify:
1. The most important element?
2. The second most important?
3. Clear groupings?

If same weight everywhere = hierarchy problem.

## Hierarchy Through Multiple Dimensions

| Tool | Strong | Weak |
|------|--------|------|
| Size | 3:1+ ratio | <2:1 |
| Weight | Bold vs Regular | Medium vs Regular |
| Color | High contrast | Similar tones |
| Position | Top/left = primary | Bottom/right |
| Space | Surrounded by whitespace | Crowded |

Best: combine 2-3 dimensions at once.

## Cards Are Not Required
Spacing + alignment create grouping naturally. Use cards ONLY when:
- Content is truly distinct and actionable
- Items need visual comparison in a grid
- Content needs clear interaction boundaries

**Never nest cards inside cards.**

## Container Queries

```css
.card-container { container-type: inline-size; }

@container (min-width: 400px) {
  .card { grid-template-columns: 120px 1fr; }
}
```

Card in narrow sidebar stays compact. Same card in main area expands.

## Optical Adjustments
- Text at `margin-left: 0` looks indented — use negative margin (-0.05em)
- Play icons shift right, arrows shift toward their direction
- Touch targets via pseudo-elements:

```css
.icon-button { width: 24px; height: 24px; position: relative; }
.icon-button::before { content: ''; position: absolute; inset: -10px; }
```

## Depth & Elevation
Semantic z-index scale: dropdown → sticky → modal-backdrop → modal → toast → tooltip.
Shadows: subtle. If clearly visible, probably too strong.
