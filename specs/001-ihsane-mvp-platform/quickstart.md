# Quickstart: Ihsane MVP Platform

This guide covers spinning up the MVP platform locally.

## Prerequisites
- Docker Compose v2+
- Node.js v20+ / pnpm
- Python 3.12+ (for local IDE inference)

## 1. Start Support Services
The database and cache are containerized for immediate access:
```bash
docker compose up -d postgres valkey
```

## 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # (or venv\Scripts\activate on Windows)
pip install -r requirements.txt

# Run migrations to generate the schema
alembic upgrade head

# Start the dev server
fastapi dev app/main.py --port 8000
```
*API docs available at: http://localhost:8000/docs*

## 3. Frontend Setup
```bash
cd frontend
pnpm install

# Start Vite dev server
pnpm run dev
```
*App connects to API on port 8000 automatically.*

## Architecture Note
For production/staging simulation, the full stack can be launched via:
```bash
docker compose -f docker-compose.prod.yml up --build
```
