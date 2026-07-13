"""Console configuration — loaded from env / .env."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="CONSOLE_", extra="ignore")

    # Deployment
    env: str = "local"  # local | dev | prod

    # Database — defaults to sqlite for local + tests so `python -m app.main`
    # works out of the box; Postgres is used in Docker Compose.
    database_url: str = "sqlite+aiosqlite:///./console.db"

    # Data directory (holds console.db, instance yamls, console keypair)
    data_dir: Path = Path("./console_data")

    # JWT / signing
    jwt_ttl_seconds: int = 300

    # Local single-tenant deployer
    local_platform_image: str = "ghcr.io/royramosparaiso/nexus-platform:0.7.0"
    local_platform_port: int = 7100
    local_platform_host: str = "http://localhost"

    # Bootstrap deliverable — where to write compose files
    deployments_dir: Path = Path("./console_data/deployments")

    # Public URL Platform uses to reach Console back after bootstrap. Only
    # needed for cloud deploys where Platform is not co-located with Console.
    # If unset, defaults to the container-local hostname (fine for local mode).
    console_webhook_url: str | None = None

    # CORS
    cors_origins: list[str] = [
        "http://localhost:7000", "http://localhost:5173", "http://localhost:3000",
    ]


settings = Settings()

# Ensure runtime dirs exist (safe to run at import).
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.deployments_dir.mkdir(parents=True, exist_ok=True)
