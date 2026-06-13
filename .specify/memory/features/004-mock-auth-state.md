# Feature Brief: Mock Authentication Flow & UI State Architecture

**Priority**: Must Have — High
**Status**: 🔲 Planned — spec exists, needs plan + tasks + implementation
**Dependencies**: 002-stitch-mockup-adaptation, 003-design-quality-enforcement
**Complexity**: M (auth routing, Pinia store, role selection UI)

## Description
Implements a mock authentication layer bridging the landing page to role-specific dashboards. Visitors clicking "ابدأ الآن" (Start Now) from the landing page encounter a lightweight role-selection screen where they choose Student, Parent, or Expert. Selection sets mock session state in a centralized Pinia store (`useMockUiStore`) and redirects to the appropriate dashboard. Supports session persistence (returning visitors skip re-selection), role switching, and logout/clear. This enables full frontend demonstration and design review without a real backend.

**Derived from**: product-spec.md §6.3 (Authentication), feature spec at specs/004-mock-auth-state/spec.md
