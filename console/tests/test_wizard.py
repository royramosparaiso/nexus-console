"""Wizard smoke tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


SAMPLE_SUBMISSION = {
    "instance_name": "acme",
    "persona": {
        "display_name": "Acme Corp",
        "kind": "company",
        "description": "",
        "default_locale": "en-US",
    },
    "deployment": {
        "modality": "fly",
        "domain": "nexus.acme.example",
        "region": "ams",
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


@pytest.mark.asyncio
async def test_wizard_schema_has_six_steps():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/wizard/schema")
    assert r.status_code == 200
    body = r.json()
    assert len(body["steps"]) == 6
    assert {s["id"] for s in body["steps"]} == {
        "persona", "deployment", "llms", "memory", "areas", "governance"
    }


@pytest.mark.asyncio
async def test_wizard_preview_renders_yaml():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/wizard/preview", json=SAMPLE_SUBMISSION)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "apiVersion: nexus.v0.6" in body["yaml"]
    assert "kind: Instance" in body["yaml"]
    assert "modality: fly" in body["yaml"]
    assert "- personal_organization" in body["yaml"]
    assert isinstance(body["warnings"], list)


@pytest.mark.asyncio
async def test_wizard_submit_registers_instance(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/wizard/submit", json=SAMPLE_SUBMISSION)
        assert r.status_code == 200, r.text
        result = r.json()
        assert result["status"] == "bootstrap-pending"
        iid = result["instance_id"]

        # Registered in the in-memory registry
        r2 = await client.get(f"/instances/{iid}")
        assert r2.status_code == 200
        assert r2.json()["name"] == "acme"

    # YAML file was written
    yaml_file = tmp_path / "console" / "instance" / iid / "nexus.instance.yaml"
    assert yaml_file.exists()
    content = yaml_file.read_text()
    assert "persona:" in content
    assert "kind: company" in content


@pytest.mark.asyncio
async def test_wizard_rejects_unknown_area():
    bad = {**SAMPLE_SUBMISSION, "areas": {"enabled": ["not_a_real_area"]}}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/wizard/preview", json=bad)
    assert r.status_code == 422
