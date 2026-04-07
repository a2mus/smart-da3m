# Technical Context

## Stack

| Layer | Technology | Version | Notes |
|-------|-----------|---------|-------|
| Frontend | Vue 3 + Vite | Vue 3.5+, Vite 6+ | Composition API, SPA, bundle < 200 KB |
| i18n | vue-i18n | 10+ | Arabic RTL + French LTR direction switching |
| Offline Cache | Workbox 7 + Dexie.js | 7.x, 4.x | Service workers, IndexedDB, Background Sync |
| Animations | CSS transitions + Lottie | — | Lightweight, no CPU-heavy libraries |
| Backend | FastAPI + Python | 0.115+, 3.12+ | Async REST, Pydantic v2 validation |
| Adaptive Engine | scikit-learn + custom BKT | — | Bayesian Knowledge Tracing, multi-arm bandit |
| Database | PostgreSQL | 16+ | JSONB for competency trees, full-text Arabic search |
| Migrations | Alembic | 1.13+ | Schema versioning |
| Cache/Sessions | Valkey | 8.x | Open-source Redis fork, Celery broker |
| Async Tasks | Celery + Valkey broker | 5.4+ | Offline sync, analytics, notifications |
| Hosting | OVH VPS | 4 vCPU, 8 GB RAM | Low latency from Algiers (< 20 ms) |
| CDN | Cloudflare Free | — | SSL, DDoS, caching |
| CI/CD | GitHub Actions + Docker | — | Multi-stage builds, SSH deploy |

## Key Dependencies
- **Pydantic v2** — API request/response validation
- **Alembic** — Database migrations
- **vue-i18n** — Internationalization with RTL/LTR switching
- **Workbox** — Service worker management for offline caching
- **Dexie.js** — IndexedDB wrapper for local content storage
- **scikit-learn** — ML algorithms for adaptive engine (BKT, bandits)

## Environment

- **Dev**: Docker Compose stack (FastAPI + PostgreSQL + Valkey + Celery + Nginx)
- **Prod**: Single OVH VPS, Docker Compose, Cloudflare CDN in front
- **CI/CD**: GitHub Actions → lint → test → Docker build → deploy via SSH

## Configuration
- `DATABASE_URL` — PostgreSQL connection string
- `VALKEY_URL` — Valkey connection string (redis:// protocol)
- `SECRET_KEY` — JWT signing key
- `CORS_ORIGINS` — Allowed frontend origins
- `CLOUDFLARE_*` — CDN configuration (if needed)
- All secrets via `.env` file (never committed) or Docker secrets
