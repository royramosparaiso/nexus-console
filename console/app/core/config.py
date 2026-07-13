"""Console configuration — loaded from env / .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="CONSOLE_", extra="ignore")

    # Deployment
    env: str = "local"  # local | dev | prod

    # Database
    database_url: str = "postgresql+asyncpg://console:console@localhost:5432/nexus_console"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth / signing
    console_private_key_path: str = "./.console_keys/console_ed25519.pem"
    console_public_key_path: str = "./.console_keys/console_ed25519.pub"
    jwt_algorithm: str = "EdDSA"
    jwt_ttl_seconds: int = 60

    # Local single-tenant bootstrap
    local_mode: bool = True
    local_platform_url: str = "http://platform:7100"

    # CORS
    cors_origins: list[str] = ["http://localhost:7000", "http://localhost:5173"]


settings = Settings()
