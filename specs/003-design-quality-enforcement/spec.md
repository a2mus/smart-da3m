# Feature Specification: Design Quality Enforcement (تطبيق جودة التصميم)

**Feature Branch**: `003-design-quality-enforcement`  
**Created**: 2026-04-14  
**Status**: Draft  
**Input**: Update the specification to require explicit enforcement of Constitution accessibility and design system limits. Require that all implemented screens must be built with RTL-optimized structures using logical CSS properties. Ensure that the design implementation strictly bans pure whites (#FFF) and pure blacks (#000), replacing them with the approved semantic scale (warm, ink, surface). Finally, add a requirement for a comprehensive WCAG AA contrast ratio and semantic HTML audit during the polish phase, extending beyond the existing 60px touch target checks.

## Clarifications

### Session 2026-04-14

- Q: Does enforcement apply retroactively to existing screens or only to new/modified code? → A: Full retroactive — all existing screens must be remediated to comply.
- Q: When do automated quality checks run in the development lifecycle? → A: Both pre-commit hooks (instant local feedback) and CI pipeline (merge gatekeeper that blocks on failure).
- Q: How are inherently physical CSS properties (top, bottom, padding-top, border-bottom) and rare intentional physical horizontal overrides handled? → A: Allowlist with justification — vertical physical properties are allowed; horizontal physical properties require a documented exemption comment.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Designer/Developer Encounters Color Violation Feedback (Priority: P1)

A developer implementing a new screen or modifying an existing view applies a raw `#FFFFFF` background or `#000000` text color. Before the change can be merged, an automated linting rule flags the violation and reports the exact file, line number, and the approved semantic token replacement (e.g., `surface-bright` instead of `#FFF`, `ink-primary` instead of `#000`). The developer corrects the color to the semantic token and the check passes.

**Why this priority**: Pure whites and pure blacks are the most visually disruptive violations of the Nurturing Soft Modernism design system. They create stark contrasts that trigger anxiety in young learners (ages 6–11) and undermine the platform's core emotional safety. Without automated enforcement, these values inevitably leak into production.

**Independent Test**: Can be fully tested by inserting a `#FFF` or `#000` value into any component file and verifying that the linting/review process catches it and provides the correct semantic token replacement.

**Acceptance Scenarios**:

1. **Given** a developer editing a Vue component, **When** they use `color: #000` or `background: #FFF` (in any casing or shorthand), **Then** an automated quality check flags the violation with the offending line and recommends the correct semantic token.
2. **Given** a component using `white` or `black` CSS keyword colors, **When** the quality check runs, **Then** these are flagged identically to hex equivalents.
3. **Given** a developer who replaces `#FFFFFF` with `var(--surface-bright)`, **When** the quality check re-runs, **Then** the violation is resolved and the check passes.
4. **Given** a component with `rgb(0,0,0)` or `rgba(255,255,255,1)`, **When** the quality check runs, **Then** these functional color notations are also caught and flagged.

---

### User Story 2 — Developer Builds an RTL-Optimized Screen (Priority: P1)

A developer creating the Parent Dashboard uses `margin-inline-start`, `padding-inline-end`, `inset-inline-start`, and `border-inline-end` instead of physical CSS properties like `margin-left`, `padding-right`, `left`, and `border-right`. The layout renders identically in both Arabic (RTL) and French (LTR) modes without any separate directional stylesheets, overrides, or `[dir="rtl"]` selectors.

**Why this priority**: The Ihsane platform targets bilingual Algerian users who switch between Arabic (RTL) and French (LTR). Using physical CSS properties creates layout breakages when switching directions — buttons misalign, text overlaps containers, and navigation collapses. Logical properties eliminate this class of bug entirely.

**Independent Test**: Can be fully tested by switching the document direction from `ltr` to `rtl` on any screen and verifying that all spacing, alignment, and flow adapts automatically without visual breakage.

**Acceptance Scenarios**:

1. **Given** any component stylesheet, **When** it specifies horizontal spacing or positioning, **Then** it uses CSS logical properties (e.g., `margin-inline-start`) instead of physical properties (e.g., `margin-left`).
2. **Given** the platform in Arabic (RTL) mode, **When** a user views any screen, **Then** all padding, margins, borders, and positioned elements flow correctly without manual RTL overrides.
3. **Given** a developer who uses `padding-left: 1rem`, **When** the quality check runs, **Then** the physical property is flagged with a recommendation to use `padding-inline-start: 1rem`.
4. **Given** a component using `text-align: left`, **When** the quality check runs, **Then** it is flagged with a recommendation to use `text-align: start`.
5. **Given** a component using Tailwind utility classes like `pl-4` or `mr-2`, **When** the quality check runs, **Then** it is flagged with recommendations to use `ps-4` (padding-start) or `me-2` (margin-end) respectively.

---

### User Story 3 — Quality Auditor Runs WCAG AA Contrast Audit (Priority: P1)

During the polish phase of any feature implementation, a quality auditor (developer, reviewer, or automated CI pipeline) runs a comprehensive accessibility audit. The audit checks every foreground/background color pair against WCAG AA minimum contrast ratios (4.5:1 for normal text, 3:1 for large text and UI components), validates semantic HTML structure (correct heading hierarchy, landmark regions, ARIA labels), and verifies touch target sizing. The audit produces a pass/fail report with specific violations, affected elements, current contrast ratios, and required minimum ratios.

**Why this priority**: WCAG AA compliance is a constitutional requirement (Article 3.3). The existing specification only enforces 60px/44px touch target minimums. Without contrast ratio and semantic HTML validation, screens may pass touch-target checks while remaining inaccessible to users with visual impairments or screen readers — a critical gap for an educational platform serving diverse learners.

**Independent Test**: Can be fully tested by running the audit against any implemented screen and verifying that the report correctly identifies both passing and failing elements with accurate contrast ratio calculations.

**Acceptance Scenarios**:

1. **Given** any implemented screen, **When** a WCAG AA audit runs, **Then** every text element's foreground/background contrast ratio is checked against the 4.5:1 minimum (normal text) or 3:1 minimum (large text ≥ 18pt or bold ≥ 14pt).
2. **Given** a screen with heading elements, **When** the semantic HTML audit runs, **Then** it validates that headings follow a logical hierarchy (no skipped levels, single `<h1>` per page).
3. **Given** a screen with interactive regions, **When** the audit runs, **Then** it validates the presence of landmark elements (`<header>`, `<main>`, `<nav>`, `<footer>`) and meaningful ARIA labels on interactive elements.
4. **Given** a screen with form inputs, **When** the audit runs, **Then** every input has an associated `<label>` element or `aria-label` attribute.
5. **Given** a screen with interactive elements, **When** the audit runs, **Then** touch targets are verified against the minimum sizing requirements (60px for student-facing, 44px for parent/expert-facing).
6. **Given** a screen that fails one or more checks, **When** the audit report is generated, **Then** it includes the specific element, the current value, the required value, and the severity (Critical for contrast failures, Warning for semantic structure issues).

---

### User Story 4 — Developer References Approved Semantic Color Scale (Priority: P2)

A developer needs to choose a background color for a new card component. Instead of guessing hex values, they reference the documented semantic color scale which maps design intent to approved tokens: `surface-bright` (#FAF9F6) for primary backgrounds, `surface-container` (#EFEEEB) for nested surfaces, `ink-primary` (deep charcoal, not #000) for body text, `ink-secondary` for muted text, and the established primary/secondary/semantic status palette. The developer uses the token name, not the raw value, ensuring consistency across the entire application.

**Why this priority**: Without a clearly documented and enforced semantic scale, developers make ad-hoc color choices that drift from the design system. The semantic scale provides a single source of truth that connects design intent ("warm background") to specific approved values, preventing the gradual erosion of visual consistency.

**Independent Test**: Can be fully tested by verifying that the semantic color reference document exists, covers all use cases (backgrounds, text, borders, status indicators), and that every approved token maps to a specific non-pure-white, non-pure-black value.

**Acceptance Scenarios**:

1. **Given** a developer needing a background color, **When** they consult the semantic color scale, **Then** they find categorized tokens: warm backgrounds (surface-bright, surface-container), ink values (ink-primary, ink-secondary, ink-muted), and status colors (success, warning, error).
2. **Given** the approved semantic scale, **When** reviewed, **Then** no token maps to `#FFFFFF`, `#000000`, `white`, or `black`.
3. **Given** any implemented component, **When** its colors are audited, **Then** every color value traces back to a named semantic token rather than an ad-hoc hex value.
4. **Given** a new component needing a color not in the scale, **When** a developer requests it, **Then** the design system is extended through a documented review process rather than an ad-hoc inline value.

---

### Edge Cases

- What happens when a third-party library injects pure white or black styles? → The audit flags third-party style overrides; developers must wrap or override them with semantic tokens at the application layer.
- How does the system handle CSS custom properties that resolve to banned values at runtime? → The audit checks both the custom property definition (in `:root` or theme files) and any fallback values in `var()` functions.
- What happens when a developer uses `opacity: 0` to create "invisible" elements — does this trigger a false positive for contrast? → The audit excludes elements with `opacity: 0`, `visibility: hidden`, or `display: none` from contrast checks.
- How does the system handle images or SVG fills that use pure white/black? → SVG fills within icon components are flagged. Photographic or raster image content is excluded from color enforcement.
- What happens when a Tailwind class implicitly resolves to a banned color (e.g., `bg-white`)? → Tailwind utility classes resolving to `#FFF` or `#000` are flagged identically to raw hex values.
- Does using `top`, `bottom`, or `padding-top` trigger a false positive for the logical property rule? → No. Vertical physical properties are exempt since they are directionally irrelevant in RTL/LTR. Only horizontal physical properties (`left`, `right`, `margin-left`, etc.) are enforced.

## Requirements *(mandatory)*

### Functional Requirements

#### Color System Enforcement

- **FR-001**: All implementations MUST use semantic color tokens from the approved Ihsane design palette. Raw hex values, RGB functions, or CSS named colors MUST NOT appear in component styles.
- **FR-002**: The following color values MUST be strictly banned across all stylesheets, component styles, and utility class usage: `#FFFFFF`, `#FFF`, `#000000`, `#000`, `white`, `black`, `rgb(255,255,255)`, `rgb(0,0,0)`, and any alpha/opacity variants (`rgba(255,255,255,*)`, `rgba(0,0,0,*)`).
- **FR-003**: The approved semantic color scale MUST include, at minimum: warm backgrounds (`surface-bright`, `surface-container`), ink values (`ink-primary`, `ink-secondary`, `ink-muted`), primary brand (`primary-fixed`, `primary-container`), secondary accent (`secondary-fixed`, `secondary-container`), and semantic status tokens (success, warning, error) — all mapped to non-pure-white, non-pure-black values.
- **FR-004**: Shadow definitions MUST use brand-tinted shadows (e.g., `rgba(140,78,53,0.08)`) instead of pure black shadows (`rgba(0,0,0,*)` at any opacity).

#### RTL Logical Property Enforcement

- **FR-010**: All horizontal spacing (margins, padding) MUST use CSS logical properties (`margin-inline-start`, `padding-inline-end`, etc.) instead of physical properties (`margin-left`, `padding-right`, etc.).
- **FR-011**: All horizontal positioning MUST use CSS logical properties (`inset-inline-start`, `inset-inline-end`) instead of physical properties (`left`, `right`).
- **FR-012**: All directional borders MUST use logical properties (`border-inline-start`, `border-inline-end`) instead of physical properties (`border-left`, `border-right`).
- **FR-013**: Text alignment MUST use logical values (`start`, `end`) instead of physical values (`left`, `right`) when controlling horizontal text flow.
- **FR-014**: Tailwind utility classes MUST use logical equivalents (`ps-*`, `pe-*`, `ms-*`, `me-*`, `start-*`, `end-*`) instead of physical equivalents (`pl-*`, `pr-*`, `ml-*`, `mr-*`, `left-*`, `right-*`).
- **FR-015**: Flexbox and Grid layouts MUST rely on document direction inheritance rather than explicit `direction` overrides, ensuring natural RTL/LTR flow.
- **FR-016**: Vertical physical CSS properties (`top`, `bottom`, `padding-top`, `padding-bottom`, `margin-top`, `margin-bottom`, `border-top`, `border-bottom`) are exempt from logical property enforcement since they are directionally irrelevant in RTL/LTR contexts. Horizontal physical properties (`left`, `right`, `margin-left`, `padding-right`, `border-left`, `border-right`) MAY only be used with a documented exemption comment (e.g., `/* physical-override: [justification] */`) for rare cases of intentionally fixed physical placement.

#### WCAG AA Accessibility Audit

- **FR-020**: All foreground/background color combinations MUST meet WCAG AA minimum contrast ratios: 4.5:1 for normal text (below 18pt regular or 14pt bold), 3:1 for large text (18pt+ regular or 14pt+ bold) and UI components.
- **FR-021**: Every page MUST contain exactly one `<h1>` element, and heading levels MUST follow a sequential hierarchy without skipping levels (e.g., `<h1>` → `<h2>` → `<h3>`, never `<h1>` → `<h3>`).
- **FR-022**: Every page MUST use semantic landmark elements: `<header>`, `<main>`, `<nav>`, and `<footer>` where applicable.
- **FR-023**: Every interactive element MUST have an accessible name — either through visible text content, an associated `<label>`, an `aria-label`, or an `aria-labelledby` reference.
- **FR-024**: Every form input MUST have a programmatically associated label (via `<label for>`, `aria-label`, or `aria-labelledby`).
- **FR-025**: Touch targets for student-facing interactive elements MUST be at minimum 60×60px; touch targets for parent and expert-facing interactive elements MUST be at minimum 44×44px.
- **FR-026**: All images MUST have meaningful `alt` text or be marked as decorative with `alt=""` and `role="presentation"`.
- **FR-027**: Focus indicators MUST be visible on all interactive elements when navigated via keyboard, with a minimum 2px outline offset using a high-contrast color.

#### Audit Process & Reporting

- **FR-030**: A comprehensive accessibility and design-system compliance audit MUST be executed during the polish phase of every feature implementation.
- **FR-031**: The audit report MUST categorize findings by severity: Critical (contrast failures, missing labels on primary interactions), Warning (semantic structure issues, non-logical CSS properties), Info (best-practice suggestions).
- **FR-032**: The audit MUST produce a machine-readable output listing each violation with: element identifier, rule violated, current value, required value, and remediation guidance.
- **FR-033**: No feature MUST be considered complete until the polish-phase audit produces zero Critical findings and acknowledges all Warning findings with documented justifications or fixes.
- **FR-034**: All enforcement rules (color bans, logical CSS properties, WCAG AA compliance, semantic HTML) MUST apply retroactively to all existing implemented screens, not only to new or modified code. All existing screens MUST be remediated to full compliance.
- **FR-035**: Automated quality checks for color bans and logical CSS property enforcement MUST run at two stages: (1) pre-commit hooks providing instant local developer feedback, and (2) CI pipeline checks that block pull request merges on any Critical violation.

### Key Entities

- **Semantic Color Token**: A named design variable (e.g., `surface-bright`, `ink-primary`) that maps an intended usage to a specific approved color value. Tokens are organized by category (warm, ink, primary, secondary, status).
- **Audit Finding**: A single violation detected during the WCAG AA or design-system compliance audit. Contains the element reference, rule identifier, current value, expected value, and severity classification.
- **Design System Rule**: A codified constraint from the Constitution and UI Specification (e.g., "ban pure whites") that is enforced through automated checks.
- **Logical CSS Property**: A CSS property that uses inline/block axes instead of physical left/right/top/bottom directions, enabling automatic RTL/LTR adaptation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of component stylesheets — including all existing screens — use semantic color tokens — zero instances of `#FFF`, `#000`, `white`, `black`, or equivalents in production code.
- **SC-002**: 100% of horizontal spacing and positioning in component stylesheets — including all existing screens — use CSS logical properties — zero instances of `margin-left`, `padding-right`, `left`, `right`, or physical Tailwind equivalents.
- **SC-003**: All screens pass WCAG AA contrast ratio validation with zero Critical findings (4.5:1 for normal text, 3:1 for large text and UI components).
- **SC-004**: All screens pass semantic HTML structure validation: single `<h1>`, sequential heading hierarchy, landmark elements present.
- **SC-005**: All interactive elements across all screens meet touch-target minimums (60px student-facing, 44px parent/expert-facing) as verified by the audit.
- **SC-006**: All form inputs across all screens have programmatically associated labels as verified by the audit.
- **SC-007**: Every implemented screen switches between RTL (Arabic) and LTR (French) without any visual breakage — no overlapping text, misaligned buttons, or collapsed layouts, verified by visual inspection in both directions.
- **SC-008**: The polish-phase audit completes in under 5 minutes per screen and produces a clear pass/fail report.

## Assumptions

- The existing Constitution (Article 3.1) and UI Specification (Section 1.1) already define the semantic color palette; this specification codifies enforceability rather than introducing new design values.
- CSS logical properties are supported by all target browsers (modern Chrome, Firefox, Safari, Edge) — no polyfills are needed.
- The 4pt grid spacing system and Tailwind breakpoints from the UI Specification remain unchanged.
- Shadow definitions using brand-tinted colors (e.g., `rgba(140,78,53,0.08)`) have already been validated for visual consistency.
- The audit process applies to all screens defined in the UI Specification: Parent Mobile Dashboard, Student Diagnostic Dashboard, and Expert Pedagogical Back-Office.
- Third-party component styles (e.g., Chart.js, headless UI primitives) may require application-layer overrides to comply with color and logical property requirements.
- Tailwind CSS is configured with custom theme tokens that map to the semantic color scale — developers use token-based utility classes rather than default Tailwind color names.
