"""Tests for the deterministic area/department recommender + its API."""

from __future__ import annotations

from uuid import UUID, uuid4

from app.models.db import InstanceRow
from app.models.wizard import AVAILABLE_AREAS
from app.services.area_recommender import (
    is_valid_area,
    recommend_area_for_card,
    recommend_areas,
)

VALID_SLUGS = {a["slug"] for a in AVAILABLE_AREAS}


# --------------------------------------------------------------------------
# Domain service — deterministic mapping
# --------------------------------------------------------------------------


def test_tag_match_takes_priority_over_domain() -> None:
    card = {
        "id": "banking_operations",
        "artifact_type": "agent",
        "domain": "back-office",
        "tags": ["banking", "treasury"],
    }
    rec = recommend_area_for_card(card)
    assert rec.area_slug == "finance_personal"
    assert rec.source == "tag_match"
    assert "banking" in rec.rationale
    # back-office would have mapped to operations — surfaced as an alternative.
    assert "operations" in rec.candidates


def test_domain_match_when_no_tag_rule_fires() -> None:
    card = {
        "id": "some_sales_agent",
        "artifact_type": "agent",
        "domain": "sales",
        "tags": ["nonexistent-tag"],
    }
    rec = recommend_area_for_card(card)
    assert rec.area_slug == "sales"
    assert rec.source == "domain_match"


def test_category_match_for_lifecycle_card_without_domain() -> None:
    card = {
        "id": "intake_agent",
        "artifact_type": "agent",
        "category": "intake",
        "domain": None,
        "tags": [],
    }
    rec = recommend_area_for_card(card)
    assert rec.area_slug == "operations"
    assert rec.source == "domain_match"
    assert "intake" in rec.rationale


def test_explicit_recommended_area_wins() -> None:
    card = {
        "id": "custom_agent",
        "artifact_type": "agent",
        "domain": "sales",
        "recommended_area": "legal",
        "tags": ["crm"],
    }
    rec = recommend_area_for_card(card)
    assert rec.area_slug == "legal"
    assert rec.source == "template_default"
    # sales (domain) + sales (crm tag) remain as candidates.
    assert "sales" in rec.candidates


def test_invalid_explicit_area_is_ignored() -> None:
    card = {
        "id": "x",
        "domain": "sales",
        "recommended_area": "not-a-real-area",
        "tags": [],
    }
    rec = recommend_area_for_card(card)
    assert rec.area_slug == "sales"
    assert rec.source == "domain_match"


def test_fallback_when_no_metadata_matches() -> None:
    card = {"id": "orphan", "artifact_type": "agent", "tags": ["totally-unknown"]}
    rec = recommend_area_for_card(card)
    assert rec.area_slug is None
    assert rec.area_label is None
    assert rec.source == "fallback"
    assert "manually" in rec.rationale.lower()


def test_multi_area_template_lists_candidates() -> None:
    card = {
        "id": "multi",
        "domain": "customer",       # -> comms
        "tags": ["contract", "crm"],  # legal (chosen) + sales
    }
    rec = recommend_area_for_card(card)
    assert rec.area_slug == "legal"
    assert set(rec.candidates) >= {"sales", "comms"}
    assert rec.area_slug not in rec.candidates


def test_recommend_areas_preserves_order_and_duplicates() -> None:
    cards = [
        {"id": "a", "domain": "sales", "tags": []},
        {"id": "b", "domain": "marketing", "tags": []},
        {"id": "a", "domain": "sales", "tags": []},  # duplicate id
    ]
    recs = recommend_areas(cards)
    assert [r.template_id for r in recs] == ["a", "b", "a"]
    assert [r.area_slug for r in recs] == ["sales", "brand", "sales"]


def test_every_area_slug_is_valid() -> None:
    assert is_valid_area("sales")
    assert not is_valid_area("bogus")


def test_all_recommended_slugs_are_canonical() -> None:
    # A fuzz over representative cards: any non-None recommendation must be a
    # real area slug.
    samples = [
        {"id": "1", "domain": "sales"},
        {"id": "2", "domain": "back-office", "tags": ["invoice"]},
        {"id": "3", "category": "mvs"},
        {"id": "4", "tags": ["seo"]},
    ]
    for rec in recommend_areas(samples):
        if rec.area_slug is not None:
            assert rec.area_slug in VALID_SLUGS


# --------------------------------------------------------------------------
# API — POST /agent-templates/recommend-areas
# --------------------------------------------------------------------------


async def test_recommend_areas_endpoint_returns_proposals(client) -> None:
    body = {"template_ids": ["banking_operations", "lead_qualification"]}
    r = await client.post("/agent-templates/recommend-areas", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    ids = {rec["template_id"] for rec in data["recommendations"]}
    assert ids == {"banking_operations", "lead_qualification"}
    assert data["unknown_template_ids"] == []
    # Canonical area catalogue is echoed for the UI dropdowns.
    slugs = {a["slug"] for a in data["areas"]}
    assert slugs == VALID_SLUGS
    for rec in data["recommendations"]:
        assert rec["source"] in {
            "template_default", "tag_match", "domain_match", "fallback"
        }


async def test_recommend_areas_endpoint_reports_unknown_ids(client) -> None:
    body = {"template_ids": ["lead_qualification", "does_not_exist"]}
    r = await client.post("/agent-templates/recommend-areas", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["unknown_template_ids"] == ["does_not_exist"]
    assert len(data["recommendations"]) == 1


async def test_recommend_areas_endpoint_empty_selection(client) -> None:
    r = await client.post("/agent-templates/recommend-areas", json={"template_ids": []})
    assert r.status_code == 200, r.text
    assert r.json()["recommendations"] == []


# --------------------------------------------------------------------------
# API — deploy-time area validation on POST /instances/{id}/command
# --------------------------------------------------------------------------


async def _seed_running_instance(session_factory) -> UUID:
    from app.services.keypair import get_or_create_keypair

    async with session_factory() as db:
        await get_or_create_keypair(db)
        row = InstanceRow(
            name=f"inst-{uuid4().hex[:8]}",
            persona_kind="individual",
            persona_display_name="Test",
            modality="text",
            agent_runtime="in_process",
            auth_provider="password_totp",
            endpoint="http://platform.local",
            status="running",
            manifest_json={},
            platform_public_key_pem="",
            platform_version="0.13.8",
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return row.id


async def test_deploy_agent_rejects_unknown_area(client, session_factory) -> None:
    iid = await _seed_running_instance(session_factory)
    payload = {
        "kind": "deploy_agent",
        "payload": {"template_id": "banking_operations", "area": "not-an-area"},
    }
    r = await client.post(f"/instances/{iid}/command", json=payload)
    assert r.status_code == 422, r.text
    assert "unknown area" in r.json()["detail"].lower()


async def test_deploy_agent_accepts_valid_area(client, session_factory) -> None:
    iid = await _seed_running_instance(session_factory)
    payload = {
        "kind": "deploy_agent",
        "payload": {"template_id": "banking_operations", "area": "finance_personal"},
    }
    r = await client.post(f"/instances/{iid}/command", json=payload)
    assert r.status_code == 202, r.text


async def test_deploy_agent_allows_omitted_area(client, session_factory) -> None:
    iid = await _seed_running_instance(session_factory)
    payload = {"kind": "deploy_agent", "payload": {"template_id": "banking_operations"}}
    r = await client.post(f"/instances/{iid}/command", json=payload)
    assert r.status_code == 202, r.text
