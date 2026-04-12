# Research: Ihsane MVP Platform

**Date**: 2026-04-10

This document consolidates key technical research and architectural decisions aligning the generic requirements to the technical constraints in the Project Constitution.

## 1. Hybrid Offline-Intelligent State

- **Decision**: Use Workbox 7 for static asset/route caching, Dexie.js for IndexedDB storage, and Background Sync for deferred analytical events.
- **Rationale**: Students in Algeria may have intermittent connectivity. A live connection is required to sync diagnostic results, but downloading a full module to Dexie.js allows a remediation session to complete without interruption.
- **Alternatives considered**: LocalStorage (too small, blocking API), standard fetch caching (no structured query capability for complex module states).

## 2. Pydantic v2 & FastAPI Architecture

- **Decision**: Strictly typed API contracts using Pydantic v2 schemas and FastAPI's native async capabilities.
- **Rationale**: Guarantees input validation with minimal boilerplate; easily handles concurrent multi-student API load during pilot testing. Generates OpenAPI Swagger UI automatically for Vue code generation / contract validation.
- **Alternatives considered**: Django/DRF (heavy, synchronous defaults), Express.js (weaker typing).

## 3. Session Management & Auth

- **Decision**: Valkey-backed JWTs with short-lived access tokens and refresh tokens. Role-Based Access Control (RBAC) via JWT claims.
- **Rationale**: Supports the three-tier model (Expert, Parent, Student). Students authenticate anonymously via PINs linked to parent accounts, respecting COPPA/Loi n° 18-07 privacy constraints. Valkey provides ultra-fast revocation and tracking.
- **Alternatives considered**: Stateful server sessions (harder to scale horizontally/PWA sync), long-lived JWTs without server validation (security risk).

## 4. Frontend State Management

- **Decision**: Pinia for reactive local state, integrated with vue-i18n for reactive Right-to-Left (RTL) localization.
- **Rationale**: Pinia's composition API style seamlessly integrates with Vue 3.5. `vue-i18n` handles dynamic swapping of text and layout direction automatically.
- **Alternatives considered**: Vuex (deprecated), plain ref composition (lacks devtools/SSR support).
