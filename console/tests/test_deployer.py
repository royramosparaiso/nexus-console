"""Deployer template tests — verify compose contents."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.services.deployer import provision_local


def test_provision_local_writes_compose_with_kokoro(tmp_path, monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "deployments_dir", tmp_path, raising=False)

    iid = uuid4()
    dir_, token, endpoint = provision_local(iid, port=18001)

    assert dir_.exists()
    compose = (dir_ / "docker-compose.yml").read_text()
    env = (dir_ / ".env").read_text()

    # Postgres + Platform + Kokoro sidecar all present
    assert "postgres:16" in compose
    assert "ghcr.io/remsky/kokoro-fastapi-cpu:latest" in compose
    assert "platform:" in compose

    # Platform receives KOKORO_URL so voice endpoint activates on boot
    assert "KOKORO_URL: http://kokoro:8880" in compose

    # Platform depends on both postgres AND kokoro so the WS is never dead on startup
    assert "depends_on: [postgres, kokoro]" in compose

    # No published port on kokoro — internal-only. Grep for port mapping under kokoro.
    kokoro_block = compose.split("kokoro:", 1)[1].split("platform:", 1)[0]
    assert "ports:" not in kokoro_block, "kokoro should not publish a port"

    # Token wired via .env
    assert f"PLATFORM_BOOTSTRAP_TOKEN={token}" in env

    # Endpoint follows local_platform_host:port
    assert endpoint.endswith(":18001")
