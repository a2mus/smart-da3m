# Quickstart: Ihsane MVP Platform

Complete guide for setting up and running the Ihsane adaptive learning platform.

## Prerequisites

- Docker Compose v2+
- Node.js v20+ and pnpm
- Python 3.12+ (for local development)
- Git

## Quick Start (Docker - Recommended)

The fastest way to get started:

```bash
# 1. Clone the repository
git clone https://github.com/your-org/ihsane-platform.git
cd ihsane-platform

# 2. Start all services
docker compose up -d

# 3. Run database migrations
docker compose exec backend alembic upgrade head

# 4. Access the application
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
# Health Check: http://localhost:8000/health
```

## Manual Development Setup

### 1. Start Infrastructure Services

```bash
# Start database and cache
docker compose up -d postgres valkey
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start development server
fastapi dev app/main.py --port 8000
```

**API Documentation:** http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Configure environment
cp .env.example .env

# Start development server
pnpm run dev
```

**Application:** http://localhost:5173

## Verification Steps

After setup, verify the installation:

### 1. Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "service": "ihsane-api"}
```

### 2. API Documentation
Open http://localhost:8000/docs in your browser to explore the API.

### 3. Test User Flows

**As an Expert:**
1. Register/login at http://localhost:5173
2. Create a module (Content → Modules → Create)
3. Add questions to the module
4. Preview the module

**As a Student:**
1. Login with PIN code
2. Select a module
3. Complete diagnostic test
4. Follow remediation pathway

**As a Parent:**
1. Login with email/password
2. View child's dashboard
3. Check progress and recommendations

### 4. Test Bilingual Support
1. Switch language using the toggle (عربية ↔ Français)
2. Verify layout changes (RTL ↔ LTR)
3. Check font changes

## Production Deployment

```bash
# Build and run production containers
docker compose -f docker-compose.prod.yml up --build -d

# Or with explicit environment
docker compose -f docker-compose.prod.yml \
  --env-file .env.production \
  up -d
```

## Environment Variables

### Backend (.env)
```bash
# Required
SECRET_KEY=your-super-secret-key-min-32-chars
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Optional
DEBUG=false
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:5173"]
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Ihsane
```

## Troubleshooting

### Database Connection Issues
```bash
# Reset database
docker compose down -v
docker compose up -d postgres
alembic upgrade head
```

### Port Already in Use
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9
```

### CORS Errors
Update `CORS_ORIGINS` in backend `.env` to include your frontend URL.

## Next Steps

1. Read the [Architecture Documentation](../architecture.md)
2. Review [API Contracts](../contracts/)
3. Check [Testing Guide](../testing.md)
4. Explore [User Stories](../spec.md)

## Support

For issues and questions:
- 📧 Email: support@ihsane-platform.com
- 💬 Discord: [Join our server](https://discord.gg/ihsane)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/ihsane-platform/issues)