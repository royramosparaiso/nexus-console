"""Wizard tests — preview, submit (dry_run), rejections."""

SAMPLE_SUBMISSION = {
    "instance_name": "acme",
    "persona": {
        "display_name": "Acme Corp",
        "kind": "company",
        "description": "",
        "default_locale": "en-US",
    },
    "deployment": {
        "modality": "local",
        "domain": None,
        "region": None,
        "tls": True,
        "autoscale": False,
    },
    "llms": {
        "enabled_providers": ["anthropic", "openai"],
        "roles": {
            "planner": "claude-opus-4-8",
            "coordinator": "claude-sonnet-4-6",
            "worker": "gpt-5-mini",
            "embeddings": "text-embedding-3-large",
        },
        "allow_fallback": True,
        "monthly_budget_usd": 100.0,
    },
    "memory": {
        "driver": "postgres_pgvector",
        "graph": "none",
        "retention_days": 365,
        "encryption_at_rest": True,
    },
    "areas": {"enabled": ["personal_organization", "meetings", "comms"]},
    "governance": {
        "default_autonomy": "act_with_approval",
        "kill_switch_enabled": True,
        "audit_retention_days": 730,
        "monthly_budget_alert_pct": 80,
        "require_2fa_for_superadmin": True,
    },
}


async def test_wizard_schema_has_seven_steps(client):
    r = await client.get("/wizard/schema")
    assert r.status_code == 200
    body = r.json()
    assert len(body["steps"]) == 7
    assert {s["id"] for s in body["steps"]} == {
        "persona", "deployment", "llms", "memory", "areas", "governance", "stack"
    }
    # New fields exposed to the frontend
    assert any(x["value"] == "in_process" for x in body["agent_runtimes"])
    assert any(x["value"] == "clerk" for x in body["auth_providers"])


async def test_wizard_preview_renders_yaml(client):
    r = await client.post("/wizard/preview", json=SAMPLE_SUBMISSION)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "apiVersion: nexus.v0.6" in body["yaml"]
    assert "kind: Instance" in body["yaml"]
    assert "modality: local" in body["yaml"]
    assert "- personal_organization" in body["yaml"]
    assert isinstance(body["warnings"], list)


async def test_wizard_submit_local_provisions_and_registers(client):
    r = await client.post(
        "/wizard/submit?dry_run=true",
        json=SAMPLE_SUBMISSION,
    )
    assert r.status_code == 200, r.text
    result = r.json()
    assert result["status"] == "bootstrap-pending"
    iid = result["instance_id"]

    # Registered
    r2 = await client.get(f"/instances/{iid}")
    assert r2.status_code == 200
    detail = r2.json()
    assert detail["name"] == "acme"
    assert detail["persona_kind"] == "company"
    assert detail["modality"] == "local"
    assert detail["agent_runtime"] == "in_process"
    assert detail["auth_provider"] == "password_totp"
    assert detail["endpoint"].startswith("http://localhost:")


async def test_wizard_rejects_unknown_area(client):
    bad = {**SAMPLE_SUBMISSION, "areas": {"enabled": ["not_a_real_area"]}}
    r = await client.post("/wizard/preview", json=bad)
    assert r.status_code == 422


async def test_wizard_fly_modality_generates_handoff_playbook(client, tmp_path, monkeypatch):
    # Point deployments to a scratch dir so we can inspect the artefacts.
    from app.core.config import settings
    monkeypatch.setattr(settings, "deployments_dir", tmp_path, raising=False)

    body = {**SAMPLE_SUBMISSION, "deployment": {
        **SAMPLE_SUBMISSION["deployment"], "modality": "fly", "region": "mad",
        "domain": "nexus.acme.example",
    }}
    r = await client.post("/wizard/submit?dry_run=true", json=body)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["status"] == "handoff-pending"

    # Locate the instance directory that the provisioner wrote to.
    iid_dir = tmp_path / j["instance_id"]
    assert (iid_dir / "fly.toml").exists()
    assert (iid_dir / "docker-compose.yml").exists()
    assert (iid_dir / "nexus.handoff.md").exists()
    assert (iid_dir / "nexus.secrets.env").exists()
    assert (iid_dir / ".gitignore").exists()

    # Playbook must reference secrets as ${VAR}, never inline values.
    playbook = (iid_dir / "nexus.handoff.md").read_text()
    assert "${FLY_API_TOKEN}" in playbook
    assert "${PLATFORM_BOOTSTRAP_TOKEN}" in playbook
    # The real bootstrap token lives in secrets.env, NOT in the playbook.
    secrets_body = (iid_dir / "nexus.secrets.env").read_text()
    real_token = [l.split("=",1)[1] for l in secrets_body.splitlines() if l.startswith("PLATFORM_BOOTSTRAP_TOKEN=")][0]
    assert real_token not in playbook, "real token must not appear in playbook body"


async def test_wizard_hetzner_modality_writes_cloud_init(client, tmp_path, monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "deployments_dir", tmp_path, raising=False)

    body = {**SAMPLE_SUBMISSION, "deployment": {
        **SAMPLE_SUBMISSION["deployment"], "modality": "hetzner", "region": "fsn1",
    }}
    r = await client.post("/wizard/submit?dry_run=true", json=body)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["status"] == "handoff-pending"

    iid_dir = tmp_path / j["instance_id"]
    assert (iid_dir / "cloud-init.yaml").exists()
    ci = (iid_dir / "cloud-init.yaml").read_text()
    assert "ghcr.io/remsky/kokoro-fastapi-cpu" in ci


async def test_wizard_unknown_modality_still_unsupported(client):
    body = {**SAMPLE_SUBMISSION, "deployment": {**SAMPLE_SUBMISSION["deployment"], "modality": "k8s"}}
    r = await client.post("/wizard/submit?dry_run=true", json=body)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "unsupported"
