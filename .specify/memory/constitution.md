# Project Constitution: Ihsane (إحسان)

**Ratification Date**: 2026-04-10
**Last Amended**: 2026-04-10
**Version**: 1.0.0
**Derived From**: product-spec.md, ui-spec.md

---

## Preamble

This constitution establishes the governing principles, standards, and practices
for the development of Ihsane. All development work MUST comply with
this document. Amendments require explicit review and version increment.

---

## Article 1: Architecture

### 1.1 System Architecture
- **Pattern**: Hybrid offline-intelligent SPA / Monolithic Async API
- **Rationale**: Ensures students can continue to use diagnostic flows in regions with intermittent internet connectivity, syncing automatically via IndexedDB (Dexie.js) to the truth database when possible.

### 1.2 Architecture Principles
1. **Offline-First Content**: MUST build student workflows assuming intermittent connectivity.
2. **Background Sync**: MUST queue analytics and progress data locally until network restores.
3. **Single Source of Truth**: MUST use PostgreSQL as the ultimate authority, validating synced offline data upon receipt.
4. **Containerization**: MUST use Docker Compose for unified dev, staging, and prod environments.

### 1.3 Technology Stack
| Layer | Technology | Version | Justification |
|-------|-----------|---------|---------------|
| Frontend | Vue 3 + Vite | 3.5+ / 6+ | Lightweight bundle, intuitive composition API, dynamic localization. |
| State/Cache | Pinia / Workbox / Dexie.js | Latest | Complete SPA data integrity & offline PWA baseline. |
| Backend API | FastAPI (Python) | 0.115+ | High-performance asynchronous endpoints matched with strict Pydantic parsing. |
| Database | PostgreSQL + Alembic | 16+ / 1.13+ | Proven RDBMS with powerful JSONB document modeling for competency graphs. |

### 1.4 Dependency Policy
Dependencies MUST be audited for size impact on the Vue frontend bundle. Any package exceeding 100KB gzipped requires explicit justification due to the target demographic's reliance on budget devices.

---

## Article 2: Code Quality

### 2.1 Testing Standards
- **Unit Testing**: 80% coverage on core pedagogical algorithms & auth. Vitest for Frontend; PyTest for Backend.
- **Integration Testing**: MUST test the DB <-> Backend <-> SDK flows for diagnostic evaluation logic.
- **Test Naming**: `should_do_X_when_Y` style for clarity.

### 2.2 Code Style & Linting
- **Linter**: ESLint (Frontend), Ruff (Backend python).
- **Formatter**: Prettier (Frontend), Black/Ruff (Backend).
- **Rules**: Enforce Vue 3 script setup patterns. Max line length 120 (Backend).

### 2.3 Type Safety
- Frontend: TypeScript MUST be in strict mode. No implicit any.
- Backend: Python MUST use strict typing annotations and Pydantic v2 schemas for all IO.

### 2.4 Code Review
PRs require at least 1 approval before `main` merge. No forceful pushes to `main`.

### 2.5 Documentation
- TSDoc for frontend stores/components.
- Comprehensive Docstrings / OpenAPI swagger for the FastAPI backend.

---

## Article 3: Design & UI

### 3.1 Design System
Nurturing Soft Modernism. Semantic Tokens defined in `ui-spec.md` (`primary-fixed`, `surface-container-highest`) MUST be strictly obeyed. Pure whites (`#FFF`) and pure blacks (`#000`) are banned.

### 3.2 Component Standards
- **Library**: Headless UI + Tailwind CSS.
- **Custom Components**: MUST lean heavily on asymmetric borders (`2rem 1rem 3rem 1rem`) and distinct geometry.
- **Naming Convention**: `[Concept][Element].vue` e.g., `DiagnosticCard.vue`, `RiskBento.vue`.

### 3.3 Accessibility
- **Compliance Level**: WCAG AA.
- **Requirements**: Enforce strictly RTL-optimized structures. 60px minimum touch targets for Student-facing components, 44px for Parent/Expert components.

### 3.4 Responsive Design
- **Approach**: Mobile-First (Parent Dashboard), Tablet-Optimized (Student), Desktop-Optimized (Expert).
- **Breakpoints**: Tailwind defaults (sm: 640px, md: 768px, lg: 1024px, xl: 1280px).

---

## Article 4: Security

### 4.1 Authentication & Authorization
- RBAC implemented via JWTs (Student, Parent, Expert).
- Students MUST authenticate anonymously via 4-6 Digit PINs tied to Parent accounts. 

### 4.2 Data Protection
- MUST hash all parent/expert passwords (bcrypt).

### 4.3 Input Validation
- Frontend: VeeValidate / Zod.
- Backend: Pydantic parsing strictly rejects extra fields.

### 4.4 Secrets Management
- `.env` files NEVER checked into source control. Backend API keys managed as VPS machine variables.

### 4.5 Dependency Auditing
- GitHub Dependabot MUST be enabled to block PRs parsing critical vulnerability vectors.

---

## Article 5: DevOps & Deployment

### 5.1 CI/CD Pipeline
- GitHub Actions MUST lint, test, and build immutable Docker images on code push.

### 5.2 Environment Strategy
- Docker compose environment (Postgres, Valkey, FastAPI) mirrored across Dev -> Prod. VPS deploys the Compose stack via securely hosted shell scripts.

### 5.3 Release Process
- Immutable Docker tags (`:v1.0.1`) pushed to GHCR (GitHub Container Registry). Auto-deployed/pulled by VPS via runner scripts.

### 5.4 Monitoring & Observability
- Application structured logging exported as JSON to rotating files on the VPS. 

### 5.5 Versioning
- SemVer (MAJOR.MINOR.PATCH) for the Core Platform.

---

## Article 6: Git Workflow

### 6.1 Branching Strategy
- Feature branching: `feat/[feature-name]`, `fix/[bug-name]`, `chore/[task-name]`.

### 6.2 Commit Convention
- Conventional Commits enforced. e.g., `feat: implemented adaptive remediation gating`.

### 6.3 PR Process
- Linear history maintained via Squash and Merge.

---

## Article 7: Project Organization

### 7.1 Directory Structure
- `/frontend`: Vue 3 modular structure (`src/views`, `src/components/common`, `src/stores`, `src/services`).
- `/backend`: FastAPI strict app layout (`app/api`, `app/core`, `app/models`, `app/schemas`, `app/services`, `app/db`).

### 7.2 Naming Conventions
- `snake_case` for python backend variables, methods, schemas.
- `camelCase` for typescript / vue logical models.
- `PascalCase` for Vue Components.

---

## Article 8: Governance

### 8.1 Amendment Process
- Changes to this constitution require explicit documentation and version increments.

### 8.2 Compliance
- All PRs MUST comply with this constitution. Non-compliance results in immediate request for changes during Code Review.

---

## Appendix A: Reference Documents
- [product-spec.md](./product-spec.md) — Product requirements
- [ui-spec.md](./ui-spec.md) — UI specification
