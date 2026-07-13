"""Cloud provisioners + handoff playbook."""

from __future__ import annotations

from uuid import uuid4

from app.services.cloud_deployers import provision_fly, provision_hetzner
from app.services.handoff_playbook import (
    PLAYBOOK_FILENAME, SECRETS_FILENAME, render_playbook, render_secrets, write_playbook,
)


def _reroute(monkeypatch, tmp_path):
    from app.core.config import settings
    monkeypatch.setattr(settings, "deployments_dir", tmp_path, raising=False)


# ────────────────────────────────────────────────────────────────
# Fly
# ────────────────────────────────────────────────────────────────

def test_fly_provisioner_writes_fly_toml(tmp_path, monkeypatch):
    _reroute(monkeypatch, tmp_path)
    iid = uuid4()
    dir_, token, inputs = provision_fly(iid, "acme-prod", region="mad", domain="acme.example")

    assert (dir_ / "fly.toml").exists()
    fly_toml = (dir_ / "fly.toml").read_text()
    assert 'primary_region = "mad"' in fly_toml
    assert f"nexus-{str(iid)[:8]}" in fly_toml
    assert (dir_ / "docker-compose.yml").exists()  # reference compose still written

    # PlaybookInputs surfaces everything the playbook needs
    assert inputs.modality == "fly"
    assert inputs.region == "mad"
    assert inputs.domain == "acme.example"
    assert "FLY_API_TOKEN" in inputs.required_secrets
    assert any("fly deploy" in s["cmd"] for s in inputs.provider_steps)


def test_fly_default_region():
    dir_, token, inputs = provision_fly(uuid4(), "rodrigo-personal")
    assert inputs.region == "mad"


# ────────────────────────────────────────────────────────────────
# Hetzner
# ────────────────────────────────────────────────────────────────

def test_hetzner_provisioner_writes_cloud_init(tmp_path, monkeypatch):
    _reroute(monkeypatch, tmp_path)
    iid = uuid4()
    dir_, token, inputs = provision_hetzner(iid, "acme-eu", region="fsn1")

    ci = (dir_ / "cloud-init.yaml").read_text()
    assert "docker.io" in ci
    assert "docker-compose-v2" in ci
    # The compose YAML is embedded inside cloud-init (indented)
    assert "postgres:16" in ci
    assert "ghcr.io/remsky/kokoro-fastapi-cpu:latest" in ci

    assert inputs.modality == "hetzner"
    assert "HCLOUD_TOKEN" in inputs.required_secrets
    assert any("hcloud server create" in s["cmd"] for s in inputs.provider_steps)
    # cx22 is the intended default size
    assert any("cx22" in s["cmd"] for s in inputs.provider_steps)


# ────────────────────────────────────────────────────────────────
# Handoff playbook rendering
# ────────────────────────────────────────────────────────────────

def test_playbook_never_leaks_real_secrets(tmp_path, monkeypatch):
    _reroute(monkeypatch, tmp_path)
    iid = uuid4()
    dir_, token, inputs = provision_fly(iid, "rodrigo-fly", region="mad")

    body = render_playbook(inputs, bootstrap_token=token)

    # The playbook MUST reference secrets as ${VAR} — never the real token.
    assert token not in body, "playbook must not contain the real bootstrap token"
    assert "${PLATFORM_BOOTSTRAP_TOKEN}" in body
    assert "${FLY_API_TOKEN}" in body
    assert "${ANTHROPIC_API_KEY}" in body

    # Structural markers we rely on when we later parse the playbook.
    assert "# Nexus OS Handoff Playbook" in body
    assert "## Required secrets" in body
    assert "## Deploy steps" in body
    assert "## Post-deploy verification" in body
    assert "## Handing back to Console" in body
    assert "## Safety notes" in body


def test_secrets_env_carries_bootstrap_token(tmp_path, monkeypatch):
    _reroute(monkeypatch, tmp_path)
    iid = uuid4()
    dir_, token, inputs = provision_hetzner(iid, "rodrigo-hetzner", region="fsn1")
    body = render_secrets(inputs, bootstrap_token=token)

    # Bootstrap token has a real value (single-use), everything else placeholder
    assert f"PLATFORM_BOOTSTRAP_TOKEN={token}" in body
    assert "CHANGE_ME_hcloud_token" in body
    assert "CHANGE_ME_anthropic_api_key" in body


def test_write_playbook_creates_files_and_gitignore(tmp_path, monkeypatch):
    _reroute(monkeypatch, tmp_path)
    iid = uuid4()
    dir_, token, inputs = provision_fly(iid, "rodrigo-fly", region="mad")
    playbook_path, secrets_path = write_playbook(inputs, bootstrap_token=token)

    assert playbook_path.name == PLAYBOOK_FILENAME
    assert secrets_path.name == SECRETS_FILENAME
    assert playbook_path.exists()
    assert secrets_path.exists()

    gitignore = (dir_ / ".gitignore").read_text()
    assert SECRETS_FILENAME in gitignore
    assert ".env" in gitignore

    # Secrets file has 0600 permissions on unix
    import os
    if os.name == "posix":
        mode = secrets_path.stat().st_mode & 0o777
        assert mode == 0o600
