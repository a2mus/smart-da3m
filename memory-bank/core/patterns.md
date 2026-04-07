# Architecture & Code Patterns

## Architecture Decisions

- **ADR-001:** SPA over SSR — Vue 3 SPA chosen over Next.js/Nuxt SSR because the primary interface is interactive exercises (not SEO-critical), and bundle size is the main constraint (< 200 KB). The landing page can be a separate static page if SEO is needed.
- **ADR-002:** Hybrid offline strategy — Content is cached locally (IndexedDB via Dexie.js), analytics sync to cloud via Background Sync. Full PWA offline deferred to v2.
- **ADR-003:** Three-tier auth — PIN for students (no email for children), email+password for parents/experts. JWT with Valkey-stored sessions.
- **ADR-004:** Valkey over Redis — Open-source fork, compatible with Redis driver/protocol, avoids Redis licensing concerns.
- **ADR-005:** Feature-based file organization — Code organized by feature/domain (not by type). Each feature folder contains its components, composables, stores, and types.
- **ADR-006:** RTL-first CSS — All layouts use CSS logical properties (`inline-start`, `inline-end`, `block-start`). Direction set by `dir` attribute on root element, toggled by vue-i18n locale.

## Code Conventions

- **Naming**: camelCase (JS/TS), PascalCase (components), UPPER_SNAKE_CASE (constants)
- **File structure**: Feature-based, < 400 lines per file
- **Error handling**: All API calls wrapped in try/catch with `error: unknown` narrowing
- **Testing**: Vitest (frontend), pytest (backend), 80%+ coverage target
- **Linting**: ESLint + Prettier (frontend), Ruff + Black (backend)
- **API design**: RESTful, Pydantic v2 schemas, auto-generated OpenAPI docs

## Patterns to Enforce

- **Immutability**: Never mutate props or state directly — use spread operators or dedicated state management
- **Composition API only**: No Options API in Vue components
- **Typed API contracts**: All API endpoints defined with Pydantic models (backend) and TypeScript interfaces (frontend)
- **Schema validation**: Pydantic for backend input validation, Zod for frontend form validation
- **Arabic content**: All user-facing strings go through vue-i18n, never hardcoded

## Anti-Patterns to Avoid

- No `any` types in TypeScript — use `unknown` and narrow
- No `console.log` in production — use structured logger
- No inline styles for RTL — always CSS logical properties
- No hardcoded curriculum structure — always driven by database/API
- No direct DOM manipulation — always through Vue reactivity
