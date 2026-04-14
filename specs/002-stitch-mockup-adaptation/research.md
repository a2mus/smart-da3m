# Research & Decisions: Stitch Mockup Adaptation

## 1. UI Architecture & Translation
- **Decision**: Map Stitch mockup elements directly to Tailwind CSS utility clusters, reusing existing `tailwind.config.js` scales (especially `ink`, `warm`, `surface`).
- **Rationale**: Keeps the codebase lean and aligns perfectly with the "Nurturing Soft Modernism" directive from the Constitution (Article 3.1).
- **Alternatives**: Custom CSS Modules (rejected due to reduced consistency and higher maintenance).

## 2. Interaction & State Management
- **Decision**: Manage UI states (modals, journey map toggles, hovers) using Vue 3 `<script setup>` localized `ref`s and shallow state, rather than over-engineering Pinia stores for pure UI prototypes.
- **Rationale**: The spec mandates mock data and frontend states. Pinia is overkill until backend integration.
- **Alternatives**: Complex Pinia definitions (rejected to speed up component velocity).

## 3. Responsive Strategy
- **Decision**: "Mobile-First" for Parent/Landing views, "Tablet-First" for Student Journey views.
- **Rationale**: The Constitution (Article 3.4) specifically dictates Target Demographic contexts: Students use tablets, Parents use mobiles.
- **Alternatives**: Desktop-first (violates target physical environment realities in Algeria).
