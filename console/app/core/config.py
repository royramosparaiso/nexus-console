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

    # --- Voicebox (optional local-first TTS/STT sidecar) --------------------
    # Voicebox (https://github.com/jamiepine/voicebox) runs *outside* Nexus as
    # a local or self-hosted sidecar exposing a REST API + HTTP MCP server.
    # Nexus never bundles it; it only talks to a configured endpoint. All voice
    # data stays on the operator's Voicebox instance.
    voicebox_enabled: bool = False
    # Base URL of the operator's Voicebox REST API, e.g. http://localhost:5111.
    voicebox_base_url: str | None = None
    # Optional bearer/client key if the operator put Voicebox behind auth. Kept
    # server-side only and never returned by the API (redacted).
    voicebox_api_key: str | None = None
    # Path Voicebox exposes for MCP (HTTP MCP server). Informational — surfaced
    # so operators can point Claude Code / Cursor / Cline at it.
    voicebox_mcp_path: str = "/mcp"
    # Voice cloning is OFF unless the operator explicitly asserts they own the
    # voice and consent to clone it. Nexus never uploads audio on its own.
    voicebox_voice_cloning_consent: bool = False


settings = Settings()

# Ensure runtime dirs exist (safe to run at import).
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.deployments_dir.mkdir(parents=True, exist_ok=True)
