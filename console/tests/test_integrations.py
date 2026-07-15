"""Tests for the generic integration adapter layer (registry, API, probes)."""

from __future__ import annotations

import app.services.integrations.probes as probes_mod
from app.services.integrations import ADAPTERS, adapter_by_id
from app.services.integrations.probes import probe
from app.services.integrations.registry import ProbeKind


# ---------------------------------------------------------------------------
# Registry completeness — every screenshot item is covered by a real adapter.
# ---------------------------------------------------------------------------

# (adapter_id, category) pairs that MUST exist for the ecosystem to be honest.
REQUIRED_ADAPTERS: dict[str, list[str]] = {
    "llm": [
        "llm_openai", "llm_anthropic", "llm_gemini", "llm_mistral", "llm_bedrock",
        "llm_deepseek", "llm_cohere", "llm_groq", "llm_together", "llm_ollama",
    ],
    "open_model_access": [
        "open_phi4", "open_gemma3", "open_llama4", "open_qwen3", "open_huggingface",
    ],
    "embeddings": [
        "embed_nomic", "embed_sbert", "embed_openai", "embed_voyage",
        "embed_google", "embed_cohere",
    ],
    "vector_db": [
        "vdb_chroma", "vdb_pinecone", "vdb_qdrant", "vdb_weaviate", "vdb_milvus",
        "vdb_pgvector", "vdb_cassandra", "vdb_opensearch",
    ],
    "framework": ["fw_langchain", "fw_llamaindex", "fw_haystack", "fw_txtai"],
    "data_extraction": [
        "extract_crawl4ai", "extract_firecrawl", "extract_scrapegraphai",
        "extract_megaparser", "extract_docling", "extract_llamaparse",
        "extract_extractthinker",
    ],
    "evaluation": ["eval_giskard", "eval_ragas", "eval_deepeval"],
}


def test_every_screenshot_item_has_an_adapter() -> None:
    for category, ids in REQUIRED_ADAPTERS.items():
        for aid in ids:
            ad = adapter_by_id(aid)
            assert ad is not None, f"missing adapter {aid}"
            assert ad.category == category, f"{aid} category {ad.category} != {category}"


def test_adapter_ids_unique_and_have_capabilities() -> None:
    ids = [a.id for a in ADAPTERS]
    assert len(ids) == len(set(ids))
    for a in ADAPTERS:
        assert a.capabilities, f"{a.id} declares no capabilities"
        assert a.template_id, f"{a.id} has no skill-card template link"


def test_local_families_use_runtime_not_fake_cloud_api() -> None:
    # Phi/Gemma/Llama/Qwen must route through an OpenAI-compatible runtime.
    for aid in ("open_phi4", "open_gemma3", "open_llama4", "open_qwen3"):
        ad = adapter_by_id(aid)
        assert ad.probe == ProbeKind.openai_compat
        assert ad.provider == "ollama"
        assert "local" in ad.tags


def test_no_adapter_ships_a_secret_value() -> None:
    for a in ADAPTERS:
        for s in a.secrets:
            # Secrets are references (env var names), never values.
            assert s.env and s.env.isupper() or "_" in s.env


# ---------------------------------------------------------------------------
# Adapters API
# ---------------------------------------------------------------------------

async def test_list_adapters(client) -> None:
    resp = await client.get("/integrations/adapters")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == len(ADAPTERS)
    # No secret VALUES anywhere — only env names.
    for a in body:
        for s in a["secrets"]:
            assert set(s.keys()) == {"key", "label", "env", "required"}


async def test_list_adapters_filter_by_category(client) -> None:
    resp = await client.get("/integrations/adapters", params={"category": "vector_db"})
    ids = {a["id"] for a in resp.json()}
    assert "vdb_qdrant" in ids and "llm_openai" not in ids


# ---------------------------------------------------------------------------
# Profiles CRUD
# ---------------------------------------------------------------------------

def _profile(**overrides) -> dict:
    base = dict(
        adapter_id="llm_openai",
        name="prod",
        base_url="https://api.openai.com/v1",
        config={},
        secret_refs={"api_key": "OPENAI_API_KEY"},
        template_ids=[],
        enabled=False,
    )
    base.update(overrides)
    return base


async def test_create_and_list_profile(client) -> None:
    resp = await client.post("/integrations/profiles", json=_profile())
    assert resp.status_code == 201, resp.text
    row = resp.json()
    assert row["adapter_id"] == "llm_openai"
    assert row["capabilities"] == ["chat", "completion"]
    # secret_refs are redacted to env-name + present flag; no values.
    ref = row["secret_refs"][0]
    assert ref["env"] == "OPENAI_API_KEY"
    assert "value" not in ref

    listed = await client.get("/integrations/profiles")
    assert len(listed.json()) == 1


async def test_create_unknown_adapter_422(client) -> None:
    resp = await client.post("/integrations/profiles", json=_profile(adapter_id="nope"))
    assert resp.status_code == 422


async def test_create_bad_base_url_422(client) -> None:
    resp = await client.post("/integrations/profiles", json=_profile(base_url="file:///etc/passwd"))
    assert resp.status_code == 422


async def test_secret_refs_reject_embedded_value(client) -> None:
    # A ref that looks like a real secret (has spaces / too long) is rejected.
    resp = await client.post(
        "/integrations/profiles",
        json=_profile(secret_refs={"api_key": "sk-this is a real secret value"}),
    )
    assert resp.status_code == 422


async def test_duplicate_adapter_name_409(client) -> None:
    await client.post("/integrations/profiles", json=_profile())
    dup = await client.post("/integrations/profiles", json=_profile())
    assert dup.status_code == 409


async def test_patch_enable_and_delete(client) -> None:
    created = (await client.post("/integrations/profiles", json=_profile())).json()
    pid = created["id"]
    patched = await client.patch(f"/integrations/profiles/{pid}", json={"enabled": True})
    assert patched.status_code == 200
    assert patched.json()["enabled"] is True

    deleted = await client.delete(f"/integrations/profiles/{pid}")
    assert deleted.status_code == 204
    assert len((await client.get("/integrations/profiles")).json()) == 0


# ---------------------------------------------------------------------------
# Connection test (probe) — via API, httpx mocked
# ---------------------------------------------------------------------------

class _FakeResponse:
    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


class _FakeClient:
    def __init__(self, response=None, exc=None):
        self._response = response
        self._exc = exc
        self.last = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def get(self, url, headers=None, auth=None):
        self.last = {"url": url, "headers": headers or {}, "auth": auth}
        if self._exc is not None:
            raise self._exc
        return self._response


async def test_test_endpoint_reachable(client, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    created = (await client.post("/integrations/profiles", json=_profile())).json()
    fake = _FakeClient(response=_FakeResponse(200))
    monkeypatch.setattr(probes_mod.httpx, "AsyncClient", lambda *a, **k: fake)
    resp = await client.post(f"/integrations/profiles/{created['id']}/test")
    assert resp.status_code == 200
    assert resp.json()["state"] == "reachable"
    # Bearer built from the env value, but the value never comes back.
    assert fake.last["headers"]["Authorization"] == "Bearer sk-test"
    assert "sk-test" not in resp.text


async def test_test_endpoint_secret_missing(client, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    created = (await client.post("/integrations/profiles", json=_profile())).json()
    resp = await client.post(f"/integrations/profiles/{created['id']}/test")
    assert resp.json()["state"] == "secret_missing"


async def test_test_endpoint_unreachable(client, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    created = (await client.post("/integrations/profiles", json=_profile())).json()
    fake = _FakeClient(exc=probes_mod.httpx.ConnectError("refused"))
    monkeypatch.setattr(probes_mod.httpx, "AsyncClient", lambda *a, **k: fake)
    resp = await client.post(f"/integrations/profiles/{created['id']}/test")
    assert resp.json()["state"] == "unreachable"


# ---------------------------------------------------------------------------
# Probe unit tests (no network)
# ---------------------------------------------------------------------------

async def test_probe_no_probe_for_bedrock() -> None:
    ad = adapter_by_id("llm_bedrock")
    res = await probe(ad, base_url=None, secrets={}, config={"region": "us-east-1"})
    assert res.state == "no_probe"


async def test_probe_key_present_for_voyage() -> None:
    ad = adapter_by_id("embed_voyage")
    assert (await probe(ad, base_url=None, secrets={})).state == "secret_missing"
    assert (await probe(ad, base_url=None, secrets={"api_key": "x"})).state == "reachable"


async def test_probe_postgres_secret_missing() -> None:
    ad = adapter_by_id("vdb_pgvector")
    res = await probe(ad, base_url=None, secrets={})
    assert res.state == "secret_missing"


async def test_probe_query_key_appends_param(monkeypatch) -> None:
    ad = adapter_by_id("llm_gemini")
    fake = _FakeClient(response=_FakeResponse(200))
    monkeypatch.setattr(probes_mod.httpx, "AsyncClient", lambda *a, **k: fake)
    res = await probe(ad, base_url=ad.base_url_default, secrets={"api_key": "K"})
    assert res.state == "reachable"
    assert "key=K" in fake.last["url"]


async def test_probe_basic_auth_sets_auth(monkeypatch) -> None:
    ad = adapter_by_id("vdb_opensearch")
    fake = _FakeClient(response=_FakeResponse(200))
    monkeypatch.setattr(probes_mod.httpx, "AsyncClient", lambda *a, **k: fake)
    res = await probe(ad, base_url=ad.base_url_default, secrets={"username": "u", "password": "p"})
    assert res.state == "reachable"
    assert fake.last["auth"] == ("u", "p")


async def test_probe_invalid_url() -> None:
    ad = adapter_by_id("vdb_chroma")
    res = await probe(ad, base_url="notaurl", secrets={})
    assert res.state == "invalid_url"


# ---------------------------------------------------------------------------
# Capability resolution / runtime exposure
# ---------------------------------------------------------------------------

async def test_capabilities_only_include_enabled(client) -> None:
    await client.post("/integrations/profiles", json=_profile(name="off", enabled=False))
    await client.post(
        "/integrations/profiles",
        json=_profile(name="on", adapter_id="vdb_qdrant", base_url="http://localhost:6333", secret_refs={}, enabled=True),
    )
    resp = await client.get("/integrations/capabilities")
    caps = resp.json()["capabilities"]
    provs = {c["provider"] for c in caps}
    assert "qdrant" in provs and "openai" not in provs


async def test_resolve_filters_by_template(client) -> None:
    await client.post(
        "/integrations/profiles",
        json=_profile(name="scoped", adapter_id="fw_langchain",
                      base_url="http://localhost:8100", secret_refs={},
                      template_ids=["llm_provider"], enabled=True),
    )
    # Global (no template_ids) profile is always served.
    await client.post(
        "/integrations/profiles",
        json=_profile(name="global", adapter_id="vdb_chroma",
                      base_url="http://localhost:8000", secret_refs={}, enabled=True),
    )
    scoped = await client.get("/integrations/resolve", params={"template_id": "llm_provider"})
    provs = {c["provider"] for c in scoped.json()["capabilities"]}
    assert {"langchain", "chroma"} <= provs

    other = await client.get("/integrations/resolve", params={"template_id": "other_card"})
    provs2 = {c["provider"] for c in other.json()["capabilities"]}
    assert "chroma" in provs2 and "langchain" not in provs2
