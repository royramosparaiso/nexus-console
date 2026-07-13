"""Local deployer — provisions a Platform via Docker Compose.

Only the `local` modality is implemented in v0.6. Other modalities emit stubs
and mark the instance as `bootstrap-pending` with a clear error message.

Flow:
  1. Generate a one-time BOOTSTRAP_TOKEN.
  2. Write a docker-compose.yml + .env in {settings.deployments_dir}/{iid}/.
  3. Persist token + compose_dir in the InstanceRow.
  4. Optionally start Compose (skipped in tests via `dry_run=True`).
  5. Return endpoint URL for the Platform.

The actual bootstrap call to /_bootstrap lives in `bootstrap_client.py`.
"""

from __future__ import annotations

import secrets
import subprocess
from pathlib import Path
from uuid import UUID

from app.core.config import settings

_COMPOSE_TEMPLATE = """version: "3.9"

services:
  postgres:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_USER: nexus
      POSTGRES_PASSWORD: nexus
      POSTGRES_DB: nexus
    volumes:
      - pg_data:/var/lib/postgresql/data

  kokoro:
    image: ghcr.io/remsky/kokoro-fastapi-cpu:latest
    restart: unless-stopped
    # No published port — only Platform talks to Kokoro. Voice reaches the user
    # via Platform's /_voice/stream WebSocket, not directly.

  platform:
    image: {image}
    restart: unless-stopped
    depends_on: [postgres, kokoro]
    environment:
      PLATFORM_DATABASE_URL: postgresql+psycopg://nexus:nexus@postgres:5432/nexus
      PLATFORM_BOOTSTRAP_TOKEN: ${{PLATFORM_BOOTSTRAP_TOKEN}}
      KOKORO_URL: http://kokoro:8880
    ports:
      - "{port}:8000"

volumes:
  pg_data:
"""


class DeployerError(RuntimeError):
    pass


def _slug_dir(instance_id: UUID) -> Path:
    d = settings.deployments_dir / str(instance_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def provision_local(instance_id: UUID, port: int | None = None) -> tuple[Path, str, str]:
    """Write compose files + return (compose_dir, bootstrap_token, endpoint_url)."""
    dir_ = _slug_dir(instance_id)
    token = secrets.token_urlsafe(32)
    resolved_port = port or settings.local_platform_port

    compose_yaml = _COMPOSE_TEMPLATE.format(
        image=settings.local_platform_image, port=resolved_port,
    )
    (dir_ / "docker-compose.yml").write_text(compose_yaml, encoding="utf-8")
    (dir_ / ".env").write_text(
        f"PLATFORM_BOOTSTRAP_TOKEN={token}\n", encoding="utf-8",
    )
    endpoint = f"{settings.local_platform_host}:{resolved_port}"
    return dir_, token, endpoint


def start_compose(compose_dir: Path) -> None:
    """Best-effort `docker compose up -d`. Raises DeployerError if docker missing."""
    try:
        subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=str(compose_dir), check=True, capture_output=True, text=True,
        )
    except FileNotFoundError as e:
        raise DeployerError(
            "docker binary not found — install Docker to enable local deployment.",
        ) from e
    except subprocess.CalledProcessError as e:
        raise DeployerError(
            f"docker compose up failed: {e.stderr or e.stdout or e}",
        ) from e


def stop_compose(compose_dir: Path) -> None:
    """Best-effort `docker compose down`. Silent if docker missing."""
    try:
        subprocess.run(
            ["docker", "compose", "down", "-v"],
            cwd=str(compose_dir), check=False, capture_output=True, text=True,
        )
    except FileNotFoundError:
        pass
