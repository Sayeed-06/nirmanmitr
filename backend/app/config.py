"""Application configuration via environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ─── Application ───
    app_name: str = "NirmanMitr"
    environment: str = "development"
    log_level: str = "INFO"
    secret_key: str = "dev-secret-key-change-in-production"

    # ─── Server ───
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_cors_origins: str = "http://localhost:3000"

    # ─── Database ───
    database_url: str = (
        "postgresql+asyncpg://nirmanmitr:changeme_in_production@localhost:5432/nirmanmitr"
    )

    # Clerk Authentication
    clerk_secret_key: str = ""
    
    # Gemini AI
    gemini_api_key: str = ""
    clerk_publishable_key: str = ""
    clerk_jwks_url: str = "https://api.clerk.com/v1/jwks"

    # ─── Supabase Storage ───
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_bucket: str = "boq-uploads"

    # ─── Upload Limits ───
    max_upload_size_mb: int = 25
    allowed_extensions: str = ".pdf,.xlsx,.xls,.xlsm,.csv"

    # ─── Rate Limiting ───
    rate_limit_per_minute: int = 100
    upload_rate_limit_per_minute: int = 20

    @property
    def cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.backend_cors_origins.split(",")]

    @property
    def allowed_ext_list(self) -> list[str]:
        """Parse allowed file extensions."""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]

    @property
    def max_upload_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
