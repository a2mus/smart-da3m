# Feature Brief: Conditional Remediation Pathways (F2)

**Priority**: Must Have — Core Value Proposition
**Status**: 🔲 Pending — no spec yet
**Dependencies**: 006-adaptive-diagnostic-engine (needs diagnostic output)
**Complexity**: XL (remediation engine, content delivery, backend-heavy)

## Description
Implements the conditional remediation engine that delivers personalized learning pathways based on diagnostic results. Progression is gated — students must master a concept before advancing. Three remediation modalities per difficulty type: audio-visual (linguistic difficulties), virtual simulations (mathematical difficulties), and mind maps (comprehension difficulties). Content is structured as "knowledge atoms" (micro-learning units). Includes dynamic difficulty adjustment, competency verification ("Passport" assessments), and mastery level tracking (Not Started → Attempted → Familiar → Proficient → Mastered) with regression detection.

**Derived from**: product-spec.md §5.1 (F2), Appendix C.2
