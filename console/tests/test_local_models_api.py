"""Tests for the local-model registry API (/local-models)."""

from __future__ import annotations

SHA = "a" * 64


def _payload(**overrides) -> dict:
    base = dict(
        template_id="voice_vad",
        model_url="https://cdn.example/silero_vad.tflite",
        sha256=SHA,
        size_bytes=2_327_524,
        license="MIT",
    )
    base.update(overrides)
    return base


async def test_list_empty(client) -> None:
    resp = await client.get("/local-models")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_register_and_list(client) -> None:
    resp = await client.post("/local-models", json=_payload())
    assert resp.status_code == 201, resp.text
    row = resp.json()
    assert row["template_id"] == "voice_vad"
    assert row["sha256"] == SHA
    assert row["id"]

    listed = await client.get("/local-models")
    assert len(listed.json()) == 1


async def test_list_filter_by_template(client) -> None:
    await client.post("/local-models", json=_payload(template_id="a", model_url="https://x/a.tflite"))
    await client.post("/local-models", json=_payload(template_id="b", model_url="https://x/b.tflite"))
    resp = await client.get("/local-models", params={"template_id": "a"})
    rows = resp.json()
    assert len(rows) == 1 and rows[0]["template_id"] == "a"


async def test_duplicate_template_url_conflicts(client) -> None:
    await client.post("/local-models", json=_payload())
    dup = await client.post("/local-models", json=_payload(sha256="b" * 64))
    assert dup.status_code == 409


async def test_rejects_bad_sha(client) -> None:
    resp = await client.post("/local-models", json=_payload(sha256="tooshort"))
    assert resp.status_code == 422


async def test_rejects_non_http_url(client) -> None:
    resp = await client.post("/local-models", json=_payload(model_url="file:///etc/passwd"))
    assert resp.status_code == 422


async def test_rejects_negative_size(client) -> None:
    resp = await client.post("/local-models", json=_payload(size_bytes=-1))
    assert resp.status_code == 422


async def test_uppercase_sha_is_normalised(client) -> None:
    resp = await client.post("/local-models", json=_payload(sha256="A" * 64))
    assert resp.status_code == 201
    assert resp.json()["sha256"] == "a" * 64
