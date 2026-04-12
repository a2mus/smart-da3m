"""
Ihsane MVP Platform - FastAPI Backend Main Application
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import analytics, auth, content, dashboard, diagnostic, remediation
from app.core.config import settings
from app.db.session import engine
from app.models import user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    # TODO: Add connection pool validation, cache warm-up
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="Ihsane MVP Platform",
    description="Adaptive learning platform for Algerian primary education",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(content.router, prefix="/api/v1/content", tags=["content"])
app.include_router(
    dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"]
)
app.include_router(
    diagnostic.router, prefix="/api/v1/diagnostic", tags=["diagnostic"]
)
app.include_router(
    remediation.router, prefix="/api/v1/remediation", tags=["remediation"]
)
app.include_router(
    analytics.router, prefix="/api/v1/analytics", tags=["analytics"]
)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "ihsane-api"}


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Ihsane MVP Platform",
        "version": "0.1.0",
        "docs_url": "/docs",
    }
