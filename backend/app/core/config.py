"""Core configuration settings for the Ihsane MVP Platform.
"""


from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Ihsane MVP Platform"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ihsane"

    # Cache/Session Store (Valkey/Redis)
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # LiteLLM Integration Settings
    LLM_BASE_URL: str | None = "http://127.0.0.1:8045/v1"
    LLM_API_KEY: str | None = "sk-b0d11f45e2484569a9eb9d56d3d8816f"
    LLM_MODEL: str = "openai/gemini-3.6-flash-high"

    # Pedagogical Alert Threshold Settings (OQ-4)
    ALERT_WARNING_FAILURE_THRESHOLD: int = 2
    ALERT_CRITICAL_FAILURE_THRESHOLD: int = 3
    ALERT_FAILURE_WINDOW_DAYS: int = 7
    ALERT_CRITICAL_PASSPORT_FAILS: int = 2
    ALERT_COOLDOWN_HOURS: int = 24

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
