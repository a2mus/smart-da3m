# Design System Strategy: The Adaptive Sanctuary

## 1. Overview & Creative North Star
**Creative North Star: "The Digital Majlis"**
This design system moves away from the sterile, rigid grids of traditional EdTech to create an environment that feels like a physical sanctuary for learning. Inspired by the Algerian landscape and architectural wisdom, the "Digital Majlis" emphasizes gathering, focus, and organic growth. 

We break the "template" look through **Intentional Asymmetry**. Instead of perfectly centered blocks, we lean into RTL-first layouts where elements breathe and overlap. We use the **Cairo/Tajawal** script not just as text, but as a structural element, paired with generous white space to reduce cognitive load for the learner. The result is a nurturing, premium experience that feels custom-built for the Algerian mind.

---

## 2. Colors & Atmospheric Depth
Our palette is rooted in the earth: Deep Turquoise water, Ochre sands, and soft cream surfaces. We avoid pure blacks and whites to maintain a "tactile paper" quality that is easy on the eyes during long study sessions.

### Color Logic
*   **Primary (`#00535b`)**: Used for authoritative actions and core brand presence.
*   **Secondary/Accent (`#8c4e35`)**: Reserved for "Aha!" moments—achievements, progress markers, and highlights.
*   **Background (`#faf9f6`)**: Our soft sand canvas.

### The "No-Line" Rule
**Borders are strictly prohibited for sectioning.** To define boundaries, designers must use tonal shifts. A `surface-container-low` section sitting on a `surface` background creates a natural edge. This "Invisible UI" approach ensures the content remains the hero, not the containers.

### Surface Hierarchy & Nesting
Treat the interface as a series of stacked, fine-paper sheets. 
1.  **Base:** `surface` (#FAF9F6)
2.  **Sectioning:** `surface-container-low` (#F4F3F1)
3.  **Interactive Elements:** `surface-container-lowest` (#FFFFFF) for the most prominent lift.

### The "Glass & Gradient" Rule
To add soul, use subtle linear gradients (Primary to Primary-Container) for large CTAs. For floating navigation or sidebars, apply **Glassmorphism**: use `surface` at 80% opacity with a `24px` backdrop blur. This makes the layout feel integrated and airy.

---

## 3. Typography: The Editorial Voice
The typography hierarchy is designed to feel like a high-end educational journal. 

*   **Arabic Headings (Tajawal/Cairo):** These are our "Voice." They should be used at large scales (`display-lg`) with tighter letter spacing to create a sense of authority and warmth.
*   **Numbers & Systems (Inter):** Numbers are the heartbeat of adaptive learning. We use Inter for all numerical data and English labels to ensure maximum legibility and a modern, technical precision that balances the organic Arabic script.
*   **Scale Contrast:** We utilize a high-contrast scale. A `display-md` headline may sit directly above a `body-sm` caption to create "Dynamic Tension," guiding the eye through an editorial flow rather than a standard list.

---

## 4. Elevation & Depth: Tonal Layering
We reject the standard "Box Shadow." Depth is achieved through light and material physics.

*   **The Layering Principle:** Instead of shadows, nest a `surface-container-highest` card inside a `surface-container-low` area. The 2% difference in tone is enough for the human eye to perceive depth without adding visual "noise."
*   **Ambient Shadows:** If an element must float (e.g., a Modal), use a tinted shadow: `rgba(0, 109, 119, 0.06)` with a `40px` blur. Shadows should feel like ambient light hitting a surface, never like a dark grey smudge.
*   **The "Ghost Border" Fallback:** For input fields or essential accessibility dividers, use the `outline-variant` token at **15% opacity**. It should be felt, not seen.

---

## 5. Components: Tactile & Nurturing

### Buttons
*   **Primary:** A soft gradient from `primary` to `primary_container`. No sharp corners; use `rounded-md` (0.75rem) to maintain a friendly, tactile feel.
*   **Secondary:** No background. Use a `surface-tint` text color with a `surface-container-high` background on hover.

### Progress & Adaptive Logic
*   **Learning Paths:** Avoid straight lines. Use asymmetric, organic paths where "Learning Nodes" (Chips) are placed with varying vertical offsets.
*   **Chips:** Selection chips use `tertiary_fixed` with `on_tertiary_fixed`. They should look like soft, rounded stones.

### Inputs & Cards
*   **Cards:** Absolutely no divider lines. Separate content using `spacing-xl` (Vertical White Space). 
*   **Input Fields:** Use `surface-container-lowest` as the fill. On focus, the background shifts to `primary-fixed-dim` (10% opacity) rather than showing a thick border.

### Adaptive Features (Custom)
*   **The "Focus Veil":** A component that uses a `surface_dim` backdrop blur to hide everything except the current learning module, creating a private "study nook."

---

## 6. Do’s and Don’ts

### Do:
*   **RTL-First Thinking:** Design for the right-to-left flow naturally. Icons that indicate direction (arrows) must be mirrored.
*   **Embrace Asymmetry:** Let a photo or a graph bleed off the edge of a container. It feels premium and custom.
*   **Layer Surfaces:** Use at least three tiers of `surface-container` on a single page to create "topography."

### Don’t:
*   **Don't use 1px Solid Borders:** It breaks the "Nurturing" brand and feels like an Excel sheet.
*   **Don't use Pure Black (#000):** It is too harsh against our sand backgrounds. Use `on_surface` (#1A1C1A).
*   **Don't Over-Shadow:** If everything has a shadow, nothing is important. Use tonal shifts first, shadows last.
*   **Don't Crowd the Content:** In "Ihsane," white space is not "empty"—it is a tool for mental clarity. If in doubt, double the padding.