"""Tests for the v0.13.4 local-inference schema:

- instance.local_inference feature flag (default, persistence, API serialization, PATCH)
- agent_local_model registry (persistence, defaults, uniqueness + check constraints)
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.db import AgentLocalModelRow, InstanceRow

SHA = "a" * 64


def _make_instance(**overrides) -> InstanceRow:
    base = dict(
        name=f"inst-{uuid4().hex[:8]}",
        persona_kind="individual",
        persona_display_name="Test",
        modality="local",
        agent_runtime="in_process",
        auth_provider="password_totp",
        manifest_json={},
        status="running",
        endpoint="http://127.0.0.1:9999",
    )
    base.update(overrides)
    return InstanceRow(**base)


# ---------------------------------------------------------------------------
# instance.local_inference flag
# ---------------------------------------------------------------------------

async def test_local_inference_defaults_false(session_factory) -> None:
    async with session_factory() as db:
        row = _make_instance()
        db.add(row)
        await db.commit()
        rid = row.id

    async with session_factory() as db:
        fetched = await db.get(InstanceRow, rid)
        assert fetched.local_inference is False


async def test_local_inference_persists_true(session_factory) -> None:
    async with session_factory() as db:
        row = _make_instance(local_inference=True)
        db.add(row)
        await db.commit()
        rid = row.id

    async with session_factory() as db:
        fetched = await db.get(InstanceRow, rid)
        assert fetched.local_inference is True


async def test_instance_api_exposes_local_inference(client, session_factory) -> None:
    async with session_factory() as db:
        row = _make_instance(local_inference=True)
        db.add(row)
        await db.commit()
        rid = str(row.id)

    resp = await client.get("/instances")
    assert resp.status_code == 200
    body = resp.json()
    match = next(r for r in body if r["instance_id"] == rid)
    assert match["local_inference"] is True

    single = await client.get(f"/instances/{rid}")
    assert single.status_code == 200
    assert single.json()["local_inference"] is True


async def test_patch_toggles_local_inference(client, session_factory) -> None:
    async with session_factory() as db:
        row = _make_instance(local_inference=False)
        db.add(row)
        await db.commit()
        rid = str(row.id)

    resp = await client.patch(f"/instances/{rid}", json={"local_inference": True})
    assert resp.status_code == 200
    assert resp.json()["local_inference"] is True

    async with session_factory() as db:
        fetched = await db.get(InstanceRow, row.id)
        assert fetched.local_inference is True


async def test_patch_without_flag_is_noop(client, session_factory) -> None:
    async with session_factory() as db:
        row = _make_instance(local_inference=True)
        db.add(row)
        await db.commit()
        rid = str(row.id)

    resp = await client.patch(f"/instances/{rid}", json={})
    assert resp.status_code == 200
    assert resp.json()["local_inference"] is True


async def test_patch_missing_instance_404(client) -> None:
    resp = await client.patch(f"/instances/{uuid4()}", json={"local_inference": True})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# agent_local_model registry
# ---------------------------------------------------------------------------

async def test_agent_local_model_persists_with_timestamps(session_factory) -> None:
    async with session_factory() as db:
        m = AgentLocalModelRow(
            template_id="voice_vad",
            model_url="https://cdn.example/silero_vad.tflite",
            sha256=SHA,
            size_bytes=2_327_524,
            license="MIT",
        )
        db.add(m)
        await db.commit()
        mid = m.id

    async with session_factory() as db:
        fetched = await db.get(AgentLocalModelRow, mid)
        assert fetched.template_id == "voice_vad"
        assert fetched.license == "MIT"
        assert fetched.size_bytes == 2_327_524
        assert fetched.created_at is not None
        assert fetched.updated_at is not None


async def test_agent_local_model_unique_template_url(session_factory) -> None:
    async with session_factory() as db:
        db.add(
            AgentLocalModelRow(
                template_id="voice_vad",
                model_url="https://cdn.example/m.tflite",
                sha256=SHA,
                size_bytes=10,
                license="MIT",
            )
        )
        await db.commit()

    with pytest.raises(IntegrityError):
        async with session_factory() as db:
            db.add(
                AgentLocalModelRow(
                    template_id="voice_vad",
                    model_url="https://cdn.example/m.tflite",
                    sha256="b" * 64,
                    size_bytes=20,
                    license="MIT",
                )
            )
            await db.commit()


async def test_agent_local_model_same_url_different_template_ok(session_factory) -> None:
    async with session_factory() as db:
        db.add(
            AgentLocalModelRow(
                template_id="agent_a",
                model_url="https://cdn.example/shared.tflite",
                sha256=SHA,
                size_bytes=10,
                license="MIT",
            )
        )
        db.add(
            AgentLocalModelRow(
                template_id="agent_b",
                model_url="https://cdn.example/shared.tflite",
                sha256=SHA,
                size_bytes=10,
                license="MIT",
            )
        )
        await db.commit()
        rows = (await db.execute(select(AgentLocalModelRow))).scalars().all()
        assert len(rows) == 2


async def test_agent_local_model_rejects_bad_sha256_length(session_factory) -> None:
    with pytest.raises(IntegrityError):
        async with session_factory() as db:
            db.add(
                AgentLocalModelRow(
                    template_id="voice_vad",
                    model_url="https://cdn.example/bad.tflite",
                    sha256="tooshort",
                    size_bytes=10,
                    license="MIT",
                )
            )
            await db.commit()


async def test_agent_local_model_rejects_negative_size(session_factory) -> None:
    with pytest.raises(IntegrityError):
        async with session_factory() as db:
            db.add(
                AgentLocalModelRow(
                    template_id="voice_vad",
                    model_url="https://cdn.example/neg.tflite",
                    sha256=SHA,
                    size_bytes=-1,
                    license="MIT",
                )
            )
            await db.commit()
