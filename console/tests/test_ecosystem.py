"""Tests for the ecosystem / capability registry (service + API)."""

from __future__ import annotations

from app.core.config import Settings
from app.services.ecosystem import (
    CATEGORY_ORDER,
    Integration,
    Status,
    build_registry,
    build_view,
)


def _settings(**overrides) -> Settings:
    return Settings(**overrides)


# ---------------------------------------------------------------------------
# Service-level invariants
# ---------------------------------------------------------------------------

def test_registry_ids_are_unique() -> None:
    entries = build_registry(_settings())
    ids = [e.id for e in entries]
    assert len(ids) == len(set(ids)), "ecosystem entry ids must be unique"


def test_registry_statuses_and_integrations_are_valid() -> None:
    for e in build_registry(_settings()):
        assert e.status in set(Status)
        assert e.integration in set(Integration)


def test_planned_entries_are_catalog_integration() -> None:
    for e in build_registry(_settings()):
        if e.status == Status.planned:
            assert e.integration == Integration.catalog, (
                f"{e.id}: planned entries must be catalog-only"
            )


def test_real_repo_capabilities_present_and_honest() -> None:
    entries = {e.id: e for e in build_registry(_settings())}
    # LiteRT is native + experimental (real code, early).
    assert entries["litertjs"].status == Status.experimental
    assert entries["litertjs"].integration == Integration.native
    # Voicebox is external + configurable (real client, needs a running sidecar).
    assert entries["voicebox"].status == Status.configurable
    assert entries["voicebox"].integration == Integration.external
    # Real entries link to a catalogue card.
    assert entries["litertjs"].template_id == "local_inference"
    assert entries["voicebox"].template_id == "voicebox_tts"


def test_llm_provider_slots_are_configurable() -> None:
    entries = {e.id: e for e in build_registry(_settings())}
    for pid in ("anthropic", "openai", "ollama"):
        assert entries[f"llm_{pid}"].status == Status.configurable


def test_no_entry_claims_available_without_earning_it() -> None:
    # We are deliberately honest: nothing is "available" (zero-setup) yet.
    entries = build_registry(_settings())
    for e in entries:
        if e.status == Status.available:
            assert not e.requires, f"{e.id}: available entries must need no setup"


def test_voicebox_summary_notes_configuration_when_enabled() -> None:
    off = {e.id: e for e in build_registry(_settings())}["voicebox"]
    on = {
        e.id: e
        for e in build_registry(
            _settings(voicebox_enabled=True, voicebox_base_url="http://localhost:5111")
        )
    }["voicebox"]
    assert "configured" in on.summary
    assert "configured" not in off.summary


def test_build_view_groups_and_counts() -> None:
    view = build_view(_settings(), "9.9.9")
    assert view.version == "9.9.9"
    # counts sum to number of entries
    total_entries = sum(len(g.entries) for g in view.groups)
    assert sum(view.counts.values()) == total_entries
    # groups follow the declared order (filtered to non-empty)
    seen = [g.category for g in view.groups]
    assert seen == [c for c in CATEGORY_ORDER if c in seen]


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

async def test_get_ecosystem_endpoint(client) -> None:
    resp = await client.get("/ecosystem")
    assert resp.status_code == 200
    body = resp.json()
    assert "groups" in body and "counts" in body and "version" in body
    ids = {e["id"] for g in body["groups"] for e in g["entries"]}
    assert {"litertjs", "voicebox", "llm_anthropic"} <= ids


async def test_get_ecosystem_entry_and_404(client) -> None:
    ok = await client.get("/ecosystem/voicebox")
    assert ok.status_code == 200
    assert ok.json()["id"] == "voicebox"

    missing = await client.get("/ecosystem/does_not_exist")
    assert missing.status_code == 404
