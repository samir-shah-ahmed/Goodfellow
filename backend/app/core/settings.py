# app/core/settings.py
from __future__ import annotations
from functools import lru_cache
from typing import List, Set, Optional
from pydantic import BaseSettings, Field, validator

class Settings(BaseSettings):
    # --- App & Runtime ---
    ENV: str = Field("development", description="development | staging | production")
    RELEASE: str = "local"
    PORT: int = 8000

    # --- Logging ---
    LOG_LEVEL: str = "INFO"        # DEBUG | INFO | WARNING | ERROR
    LOG_FORMAT: str = "plain"      # plain | json
    REQUEST_LOG_SAMPLE: float = 1.0  # 0.0–1.0

    # --- CORS / Frontend ---
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # --- Database (Postgres recommended) ---
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "balanced_alpha"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    # Optional SQLite shortcut (only used if DATABASE_URL provided for sqlite)
    # SQLITE_PATH can be used to compose a sqlite URL externally if you want.

    # --- Redis / Queue ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Providers / Data Sources ---
    NEWSAPI_KEY: Optional[str] = None
    # TWITTER_BEARER, NYT_API_KEY, etc. can be added when needed.

    # --- AI / LLMs ---
    LLM_PROVIDER: str = "openai"   # openai | azureopenai | anthropic | vertex | stub
    OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    MODEL_NAME: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 1000

    # --- Embeddings / Semantic Search ---
    USE_EMBEDDINGS: bool = False
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    USE_PGVECTOR: bool = False

    # --- Ingestion Behavior ---
    DEFAULT_PAGE_SIZE: int = 50
    FETCH_TIMEOUT_SECS: int = 15
    USER_AGENT: str = "BalancedAlpha/0.1 (+https://example.com)"
    MAX_CONCURRENT_FETCHES: int = 10

    # --- Classification Thresholds ---
    CONFIDENCE_ATTACH: float = 0.6
    CONFIDENCE_WEAK: float = 0.4
    ONLY_CALL_LLM_WHEN_AMBIGUOUS: bool = True

    # --- API & Auth ---
    ENABLE_API_KEYS: bool = False
    API_KEY_HEADER: str = "X-API-Key"
    JWT_SECRET: str = "change-me"
    JWT_EXPIRES_MIN: int = 60

    # --- Rate Limiting ---
    RATE_LIMIT_WINDOW_SEC: int = 60
    RATE_LIMIT_MAX_REQUESTS: int = 120

    # --- Observability ---
    SENTRY_DSN: Optional[str] = None
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None
    ENABLE_PROMETHEUS_METRICS: bool = True

    # --- Features / Flags ---
    FEATURE_ADMIN_ENDPOINTS: bool = True
    FEATURE_STORE_FULLTEXT: bool = True
    FEATURE_CURSOR_PAGINATION: bool = True

    # --- Security / Compliance ---
    EXCERPT_ONLY_DOMAINS: str = ""     # comma-separated
    EXCERPT_MAX_CHARS: int = 1200

    # --- Frontend URLs ---
    FRONTEND_URL: str = "http://localhost:3000"
    PUBLIC_BASE_URL: str = "http://localhost:8000"

    # --- Email / Notifications ---
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = 'Balanced Alpha <no-reply@balancedalpha.local>'

    # --- Misc. Paths ---
    DATA_DIR: str = "./var"
    LOG_DIR: str = "./var/logs"

    class Config:
        env_file = ".env"
        case_sensitive = True

    # ---------- Computed helpers ----------
    @property
    def is_prod(self) -> bool:
        return self.ENV.lower() == "production"

    @property
    def is_staging(self) -> bool:
        return self.ENV.lower() == "staging"

    @property
    def origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def excerpt_domains_set(self) -> Set[str]:
        return {d.strip().lower() for d in self.EXCERPT_ONLY_DOMAINS.split(",") if d.strip()}

    @property
    def sql_url(self) -> str:
        """Compose DATABASE_URL from parts if not provided."""
        if self.DATABASE_URL and self.DATABASE_URL.strip():
            return self.DATABASE_URL
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # ---------- Validators (light sanity checks) ----------
    @validator("REQUEST_LOG_SAMPLE")
    def _clamp_sample(cls, v: float) -> float:
        return 0.0 if v < 0 else 1.0 if v > 1 else v

    @validator("LOG_FORMAT")
    def _normalize_logfmt(cls, v: str) -> str:
        v2 = v.lower().strip()
        return "json" if v2 == "json" else "plain"

@lru_cache
def get_settings() -> Settings:
    return Settings()