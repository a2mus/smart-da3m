---
project_name: 'Ihsane Platform (moody-bird)'
user_name: 'Mus'
date: '2026-07-09'
sections_completed:
  ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'quality_rules', 'workflow_rules', 'anti_patterns']
status: 'complete'
rule_count: 38
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

### Backend (`backend/`) — Python 3.12, async
- **FastAPI** ≥0.115 + Uvicorn[standard] ≥0.32 — async web framework
- **Pydantic** ≥2.9 + pydantic-settings ≥2.6 — validation & settings (v2 API only)
- **SQLAlchemy** ≥2.0 async + asyncpg ≥0.30 — Postgres 16 ORM (2.0-style, async sessions)
- **Alembic** ≥1.14 — migrations
- **Redis** ≥5.2 (cache/session) + **Celery** ≥5.4 (background tasks)
- **python-jose[cryptography]** ≥3.3 + **passlib[bcrypt]** ≥1.7.4 — JWT auth
- Tests: pytest ≥8.3 + pytest-asyncio ≥0.24 (asyncio_mode=auto) + aiosqlite (in-memory async tests)
- Lint/format: **Ruff** ≥0.8 (replaces black/isort/flake8)

### Frontend (`frontend/`, pkg `ihsane-frontend`) — Vue 3 + TS, ESM
- **Vue** ^3.5 (Composition API, `<script setup>`) + **TypeScript** ~5.6 (strict)
- **Vite** ^6.0 + vite-plugin-pwa ^0.21 (offline-first PWA)
- **Pinia** ^2.3 (state) + **Vue Router** ^4.5 + **Vue I18n** ^10 (AR/FR)
- **Tailwind CSS** ^3.4 + **Chart.js** ^4.4 / vue-chartjs ^5.3
- **Axios** ^1.7 (HTTP) + **Dexie** ^4.0 (IndexedDB offline cache) + @vueuse/core ^11
- Tests: **Vitest** ^2.1 (jsdom) + **Playwright** ^1.49 (+ @axe-core/playwright a11y)
- Lint/format: ESLint 9 flat config + Stylelint 17 + Prettier 3

### Infra
- Docker / docker-compose (+ prod compose), Caddy reverse proxy, GitHub Actions (`deploy.yml`)
- Husky pre-commit → `lint-staged` on frontend

### Version constraints agents must respect
- Pydantic **v2** syntax only (no v1 `BaseSettings`/validators).
- SQLAlchemy **2.0** async API (`select()`, `AsyncSession`) — never legacy `Query`/sync session.
- Tailwind **v3** — do NOT use v4 directives/utilities.

## Critical Implementation Rules

### Language-Specific Rules

**TypeScript / JavaScript (frontend)**
- `tsconfig` is **strict** with `noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`. `npm run build` runs `vue-tsc` first — unused vars fail the build even though ESLint disables `no-unused-vars`.
- Use the `@/` alias for all `src/` imports (configured in tsconfig + Vite). No relative paths climbing `../../`.
- ESM only (`"type": "module"`); use `import/export`, never `require`.
- **Prettier style is enforced**: no semicolons, single quotes, trailing comma `es5`, arrow parens `avoid`, 2-space indent, printWidth 88, LF endings.
- Components are Composition API + `<script setup lang="ts">` only. No Options API.

**Python (backend)**
- Target **Python 3.12**. Write `async def` endpoints/services and `await` the async session — the whole stack is async; never block the event loop.
- **Ruff** is the single linter/formatter (no black/isort/flake8). Line length 88, double quotes, google-convention docstrings.
- Import order enforced by Ruff isort with `known-first-party = ["app"]` — group stdlib / 3rd-party / `app`.
- Security rules (Bandit `S`) active: no `eval`, no hardcoded secrets, no unsafe YAML. `assert` is allowed only in `tests/**`.
- Use SQLAlchemy 2.0 `select()` + `AsyncSession`; inject `get_db()` as a FastAPI dependency.

### Framework-Specific Rules

**Vue 3 / Frontend**
- All HTTP goes through the central Axios instance in `src/services/api.ts` — never call `fetch`/`axios` directly in components. JWT injection + 401 token-refresh live in its interceptors.
- State via **Pinia** (`src/stores/`); one store per domain. Routes use **named routes** with auth guards.
- Every user-facing string goes through **Vue I18n** (`src/locales/`) — AR (RTL, primary) and FR (LTR). Never hardcode UI text.
- Views (pages) live in `src/views/`, grouped by role (`student/`, `parent/`, `expert/`); reusable components in `src/components/`. Domain services in `src/services/`.

**FastAPI / Backend**
- Layered: thin routers in `app/api/endpoints/` → business logic in `app/services/` → SQLAlchemy models in `app/models/` + Pydantic schemas in `app/schemas/`.
- Register every router in `app/main.py` under prefix `/api/v1/<domain>` with a tag. Health check at `GET /health`.
- Settings via the pydantic-settings `Settings` singleton in `app/core/config.py` (case-sensitive, env-driven). Inject dependencies with `Depends()`.

### Testing Rules

- **Backend**: pytest with `asyncio_mode=auto` (no `@pytest.mark.asyncio` needed). Tests in `backend/tests/` mirror `app/` (`api/`, `services/`); `conftest.py` provides fixtures. Use **aiosqlite in-memory** for async DB tests (no Postgres server needed).
- **Frontend unit**: Vitest + jsdom + `@vue/test-utils` (`globals: true`). Tests in `frontend/tests/` (`components/`, `views/`).
- **E2E / a11y**: Playwright (`npm run test:e2e`) and axe-core audit (`npm run audit:a11y`). Don't write a11y checks as unit tests — use the axe audit.
- API contract tests must use **snake_case** matching the wire format (e.g. `parent_email`, `pin_code`, `response_time_ms`).

### Code Quality & Style Rules

- **RTL / logical CSS is a HARD RULE** (see Critical Don't-Miss Rules) — enforced by ESLint `vue/no-restricted-class`.
- Prettier (frontend) and Ruff (backend) configs are the source of truth; the Husky pre-commit runs `lint-staged` on frontend only.
- **Naming**: Vue components PascalCase `.vue`; TS modules camelCase; Python modules/models snake_case; API fields snake_case on the wire.
- **Docs**: google-convention docstrings on public Python functions/classes; TS code should self-document (minimal comments).

### Development Workflow Rules

- **Branches**: `NNN-kebab-case-description` (e.g. `011-advanced-analytics`), merged into `master`.
- **Commits**: Conventional Commits with scope — `type(scope): subject` (e.g. `fix(frontend): …`, `docs(memory-bank): …`).
- **Pre-commit**: Husky → `cd frontend && npx lint-staged` (frontend staged files only).
- **API versioning**: all routes under `/api/v1/`.
- **Config/env**: backend reads `.env` via pydantic-settings; frontend uses `VITE_*` env vars (`VITE_API_URL`). Never commit secrets.

### Critical Don't-Miss Rules

- **RTL / logical CSS (HARD RULE)**: NEVER use physical/directional utilities — `pl-*`/`pr-*`/`ml-*`/`mr-*`/`left-*`/`right-*`/`text-left`/`text-right`/`float-left`/`float-right`/`border-l`/`border-r`/`rounded-l`/`rounded-r`/`bg-white`. Use **logical** equivalents: `ps-*`/`pe-*`/`ms-*`/`me-*`/`start-*`/`end-*`/`text-start`/`text-end`. ESLint will fail the build.
- **Bilingual-first**: Arabic (RTL) is the default/primary locale (`lang=ar`, `dir=rtl`); French (LTR) secondary. All UI text via vue-i18n — no hardcoded strings.
- **Wire format**: snake_case between client and server; camelCase inside TS. The Axios service layer is the translation boundary.
- **Never bypass the API service layer** (`src/services/api.ts`) — auth tokens, refresh, and 403/401 handling live there.
- **Role-based auth**: 3 roles (STUDENT, PARENT, EXPERT). Students log in via **PIN**; parents/experts via **email + password**. Enforce RBAC on protected endpoints.
- **Async everywhere (backend)** — never use sync DB calls or blocking I/O.
- **PWA / offline-first**: don't break the service worker (vite-plugin-pwa) or Dexie (IndexedDB) caching. Test offline behaviour.
- **Secrets**: `SECRET_KEY` has a dev default that MUST be overridden in production. Never commit real credentials.

---

## Usage Guidelines

**For AI Agents:**
- Read this file before implementing any code.
- Follow ALL rules exactly as documented.
- When in doubt, prefer the more restrictive option.
- Update this file if new patterns emerge.

**For Humans:**
- Keep this file lean and focused on agent needs.
- Update when the technology stack or patterns change.
- Review periodically for outdated rules; remove rules that become obvious over time.

Last Updated: 2026-07-09
