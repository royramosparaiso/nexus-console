"""Ecosystem / capability registry.

A single, honest catalogue of the AI building blocks Nexus can plug into —
LLMs, frameworks, vector databases, data extraction, open-model access, text
embeddings, evaluation, plus the two local-first capabilities this repo
actually ships (browser LiteRT.js inference and the optional Voicebox voice
sidecar).

Design principles (deliberately *not* a wall of logos):

* Every entry declares an honest ``status``:
    - ``available``     — works today with what's in this repo, no extra setup.
    - ``configurable``  — supported, but the operator must supply an endpoint,
                          key, or enable a flag before it does anything.
    - ``experimental``  — real code exists but is early / behind a flag / not
                          hardened for production.
    - ``planned``       — a discoverable catalogue entry only. No integration
                          code yet; listed so the roadmap is explicit and the
                          setup requirements are stated up front.
* ``integration`` states *where* the code lives so we never imply we vendored
  something we didn't:
    - ``native``    — implemented inside Nexus (Console/Platform).
    - ``external``  — a separate process Nexus talks to (sidecar / local app).
    - ``catalog``   — listed for discovery; no integration yet (``planned``).
* ``requires`` spells out exactly what an operator must do to move an entry
  from its current state to working. Empty for ``available`` natives.

The registry is data, not behaviour. ``build_registry`` layers the few pieces
of *live* state we can cheaply know (is Voicebox configured? is the LiteRT
runtime present?) on top of the static seed so the UI can show real status
without pretending the planned rows are wired up.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from app.core.config import Settings
from app.services.integrations import ADAPTERS, Adapter


class Status(str, Enum):
    available = "available"
    configurable = "configurable"
    experimental = "experimental"
    planned = "planned"


class Integration(str, Enum):
    native = "native"
    external = "external"
    catalog = "catalog"


class Category(str, Enum):
    llm = "llm"
    framework = "framework"
    vector_db = "vector_db"
    data_extraction = "data_extraction"
    open_model_access = "open_model_access"
    embeddings = "embeddings"
    evaluation = "evaluation"
    voice = "voice"
    local_inference = "local_inference"


CATEGORY_LABELS: dict[Category, str] = {
    Category.llm: "LLMs",
    Category.framework: "Frameworks",
    Category.vector_db: "Vector Databases",
    Category.data_extraction: "Data Extraction",
    Category.open_model_access: "Open LLMs Access",
    Category.embeddings: "Text Embeddings",
    Category.evaluation: "Evaluation",
    Category.voice: "Voice",
    Category.local_inference: "Local Inference",
}

# Display order mirrors the reference ecosystem diagram, with the two
# capabilities this repo actually ships pulled to the top.
CATEGORY_ORDER: list[Category] = [
    Category.local_inference,
    Category.voice,
    Category.llm,
    Category.open_model_access,
    Category.embeddings,
    Category.vector_db,
    Category.framework,
    Category.data_extraction,
    Category.evaluation,
]


class EcosystemEntry(BaseModel):
    id: str
    name: str
    category: Category
    status: Status
    integration: Integration
    summary: str
    provider: str | None = None
    # Concrete steps to make this entry work. Empty ⇒ nothing to do.
    requires: list[str] = Field(default_factory=list)
    docs_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    # Soft link to an agent_templates catalogue card id, when one exists.
    template_id: str | None = None


class CategoryGroup(BaseModel):
    category: Category
    label: str
    entries: list[EcosystemEntry]


class EcosystemView(BaseModel):
    version: str
    counts: dict[str, int]
    groups: list[CategoryGroup]


# ---------------------------------------------------------------------------
# Static seed. Real, in-repo capabilities first; the reference-diagram
# ecosystem follows as honest ``planned`` catalogue rows.
# ---------------------------------------------------------------------------

def _integration_of(adapter: Adapter) -> Integration:
    return Integration.native if adapter.integration == "native" else Integration.external


def _requires_for(adapter: Adapter) -> list[str]:
    """Honest, concrete steps to make an adapter-backed entry work."""
    reqs: list[str] = ["Create + enable an integration profile (Ecosystem → Integrations)"]
    if any(f.key == "base_url" for f in adapter.fields):
        reqs.append(f"Point base_url at your {adapter.name} endpoint")
    required_envs = [s.env for s in adapter.secrets if s.required]
    if required_envs:
        reqs.append("Set " + ", ".join(required_envs))
    reqs.append("Run 'Test connection' to verify reachability")
    return reqs


def _entry_from_adapter(adapter: Adapter) -> EcosystemEntry:
    caps = ", ".join(adapter.capabilities)
    summary = f"{adapter.name}: {caps} via {adapter.provider}."
    if adapter.notes:
        summary += f" {adapter.notes}"
    return EcosystemEntry(
        id=adapter.id,
        name=adapter.name,
        category=Category(adapter.category),
        # A real config + health/probe path exists ⇒ configurable (never
        # ``available``, which requires an enabled, tested runtime path).
        status=Status.configurable,
        integration=_integration_of(adapter),
        summary=summary,
        provider=adapter.provider,
        requires=_requires_for(adapter),
        docs_url=adapter.docs_url,
        tags=adapter.tags,
        template_id=adapter.template_id,
    )


def _seed() -> list[EcosystemEntry]:
    entries: list[EcosystemEntry] = []

    # -- Local inference (real, native, experimental) -----------------------
    entries.append(
        EcosystemEntry(
            id="litertjs",
            name="LiteRT.js (WebGPU / WASM)",
            category=Category.local_inference,
            status=Status.experimental,
            integration=Integration.native,
            provider="google-ai-edge",
            summary=(
                "Run small .tflite models directly in the browser via "
                "@litertjs/core — WebGPU with deterministic CPU/WASM fallback. "
                "Backs the Silero VAD slice in the Voice cockpit."
            ),
            requires=[
                "Enable local_inference on the target instance",
                "Register the model in the local-model registry (url + sha256 + license)",
            ],
            docs_url="https://developers.googleblog.com/en/litertjs-googles-high-performance-web-ai-inference/",
            tags=["webgpu", "wasm", "tflite", "vad", "on-device"],
            template_id="local_inference",
        )
    )

    # -- Voice (real, external, configurable) -------------------------------
    entries.append(
        EcosystemEntry(
            id="voicebox",
            name="Voicebox (local TTS/STT)",
            category=Category.voice,
            status=Status.configurable,
            integration=Integration.external,
            provider="jamiepine/voicebox",
            summary=(
                "Optional local-first voice sidecar: TTS across many engines, "
                "Whisper dictation, and an HTTP MCP server. Runs as a separate "
                "local/self-hosted process; Nexus only talks to its REST API. "
                "No audio leaves the operator's Voicebox instance."
            ),
            requires=[
                "Run Voicebox locally or self-hosted",
                "Set CONSOLE_VOICEBOX_ENABLED=true and CONSOLE_VOICEBOX_BASE_URL",
                "Voice cloning is opt-in: set CONSOLE_VOICEBOX_VOICE_CLONING_CONSENT=true only for voices you own",
            ],
            docs_url="https://github.com/jamiepine/voicebox",
            tags=["tts", "stt", "whisper", "mcp", "local", "voice-cloning"],
            template_id="voicebox_tts",
        )
    )

    # -- Everything else is derived from the integration adapter registry.
    # Each adapter ships a real typed config + health/probe path, so its entry
    # is ``configurable`` — never ``planned`` (no more logo-only catalogue rows)
    # and never falsely ``available`` (that needs an enabled, tested runtime).
    for adapter in ADAPTERS:
        entries.append(_entry_from_adapter(adapter))

    return entries


def build_registry(settings: Settings) -> list[EcosystemEntry]:
    """Return the seed with cheap live-state overlaid.

    The only live signal we can know without a round-trip is whether Voicebox
    has been *configured* (enabled + base URL present). Everything else is
    static: the Providers page owns per-provider credential state, and LiteRT
    availability is a per-instance flag, not a global one.
    """
    entries = _seed()
    for e in entries:
        if e.id == "voicebox":
            if settings.voicebox_enabled and settings.voicebox_base_url:
                # Still "configurable" — configured but not health-verified
                # here. The /voicebox/status endpoint reports reachability.
                e.summary += " (configured — check health on the Voice/Ecosystem page)"
    return entries


def build_view(settings: Settings, version: str) -> EcosystemView:
    entries = build_registry(settings)
    counts: dict[str, int] = {s.value: 0 for s in Status}
    for e in entries:
        counts[e.status.value] += 1

    groups: list[CategoryGroup] = []
    for cat in CATEGORY_ORDER:
        cat_entries = [e for e in entries if e.category == cat]
        if not cat_entries:
            continue
        groups.append(
            CategoryGroup(
                category=cat,
                label=CATEGORY_LABELS[cat],
                entries=cat_entries,
            )
        )
    return EcosystemView(version=version, counts=counts, groups=groups)
