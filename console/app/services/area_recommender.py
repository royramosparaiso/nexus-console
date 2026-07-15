"""Deterministic area/department recommendations for agent deployment.

When an operator selects one or more agent templates to deploy, Console
proposes the most appropriate *area* (department) for each one. The mapping
is metadata-driven and fully deterministic — no LLM calls — so it is cheap,
testable, and reusable by any future agent/sidecar/skill deployment flow.

The canonical list of areas is ``app.models.wizard.AVAILABLE_AREAS`` (the same
areas the instance wizard offers). Recommendations are derived from the
canonical agent-template metadata (``recommended_area`` if present, otherwise
capability tags, otherwise the ops ``domain`` / project ``category``). If
nothing matches, the recommendation is left unassigned and the operator picks
manually.

Priority order (first match wins):

  1. ``template_default`` — the card frontmatter carries an explicit, valid
     ``recommended_area`` slug.
  2. ``tag_match`` — a high-precision capability tag maps to an area.
  3. ``domain_match`` — the ops ``domain`` (or project ``category``) maps to
     an area.
  4. ``fallback`` — no metadata match; ``area`` is ``None`` (unassigned).
"""

from __future__ import annotations

from typing import Iterable, Literal, Optional

from pydantic import BaseModel, Field

from app.models.wizard import AVAILABLE_AREAS

RecommendationSource = Literal[
    "template_default", "tag_match", "domain_match", "fallback"
]

_AREA_LABELS: dict[str, str] = {a["slug"]: a["label"] for a in AVAILABLE_AREAS}
_VALID_AREA_SLUGS: frozenset[str] = frozenset(_AREA_LABELS)

# Ops domain → area. Covers the seven ops domains in the catalogue.
_DOMAIN_AREA_MAP: dict[str, str] = {
    "sales": "sales",
    "deals": "sales",
    "marketing": "brand",
    "operations": "operations",
    "intelligence": "operations",
    "customer": "comms",
    "back-office": "operations",
}

# Project/lifecycle category → area, for cards without an ops domain.
_CATEGORY_AREA_MAP: dict[str, str] = {
    "finance": "finance_personal",
    "investor-deliverable": "finance_personal",
    "market-research": "operations",
    "intake": "operations",
    "mvs": "dev",
    "validation": "product",
    "scaling": "operations",
    "sales": "sales",
    "deals": "sales",
    "marketing": "brand",
    "operations": "operations",
    "intelligence": "operations",
    "customer": "comms",
    "back-office": "operations",
    "verticals": "operations",
}

# Ordered, highest-precision-first capability-tag rules. The first rule whose
# tag set intersects the card's tags wins. Order matters: a card tagged both
# "legal" and "crm" resolves to legal (a compliance concern trumps the CRM
# capability). Each entry: (area_slug, {tags}).
_TAG_RULES: tuple[tuple[str, frozenset[str]], ...] = (
    (
        "legal",
        frozenset({
            "legal", "compliance", "contract", "gdpr", "dpa", "ip",
            "trademark", "incorporation", "terms", "rbac", "permissions",
            "iam", "signoff",
        }),
    ),
    (
        "finance_personal",
        frozenset({
            "finance", "accounting", "invoice", "billing", "revenue",
            "budget", "burn", "cash-flow", "treasury", "banking", "payments",
            "reconciliation", "financials", "valuation", "fundraising",
            "cap-table", "unit-economics", "collections", "ar", "expense",
            "finops", "spend",
        }),
    ),
    (
        "dev",
        frozenset({
            "architecture", "tech-stack", "api", "schema", "data-model",
            "adr", "scaffolding", "provisioning", "migration", "etl",
            "integration", "sre", "alerting",
        }),
    ),
    (
        "product",
        frozenset({
            "roadmap", "features", "user-stories", "personas",
            "functional-spec", "ux", "information-architecture", "acceptance",
            "product",
        }),
    ),
    (
        "meetings",
        frozenset({"meeting", "meetings", "calendar", "qbr", "kickoff"}),
    ),
    (
        "brand",
        frozenset({
            "brand", "marketing", "creative", "copy", "seo", "ads", "content",
            "social", "campaign", "pr", "influencer", "positioning", "naming",
            "logo",
        }),
    ),
    (
        "sales",
        frozenset({
            "sales", "pipeline", "lead", "deal", "outbound", "prospecting",
            "cold-call", "sdr", "quota", "crm", "closing", "proposal", "quote",
            "objection", "qualification", "forecast",
        }),
    ),
    (
        "comms",
        frozenset({
            "comms", "email", "inbox", "reply", "engagement", "ticket",
            "escalation", "helpdesk", "cx", "customer", "community",
            "moderation", "client-comms",
        }),
    ),
)


class AreaRecommendation(BaseModel):
    """A single proposed area for one selected template."""

    template_id: str
    artifact_type: Optional[str] = None
    area_slug: Optional[str] = Field(
        None, description="Recommended area slug, or None when unassigned."
    )
    area_label: Optional[str] = None
    source: RecommendationSource
    rationale: str
    candidates: list[str] = Field(
        default_factory=list,
        description="Other plausible area slugs, most-relevant first, "
        "excluding the chosen one. Useful when a template fits several areas.",
    )


class AreaOption(BaseModel):
    """One selectable area, mirrored from the canonical wizard catalogue."""

    slug: str
    label: str
    tier: str


class RecommendationResult(BaseModel):
    """Batch response: one recommendation per resolved template + the areas."""

    recommendations: list[AreaRecommendation]
    areas: list[AreaOption]
    unknown_template_ids: list[str] = Field(default_factory=list)


def area_options() -> list[AreaOption]:
    return [
        AreaOption(slug=a["slug"], label=a["label"], tier=a["tier"])
        for a in AVAILABLE_AREAS
    ]


def is_valid_area(slug: str) -> bool:
    return slug in _VALID_AREA_SLUGS


def _tag_matches(tags: Iterable[str]) -> list[tuple[str, str]]:
    """Return [(area_slug, matched_tag)] for every tag rule that fires, in
    priority order."""
    tagset = {str(t).lower() for t in tags}
    out: list[tuple[str, str]] = []
    for area, rule_tags in _TAG_RULES:
        hit = tagset & rule_tags
        if hit:
            out.append((area, sorted(hit)[0]))
    return out


def recommend_area_for_card(card: dict) -> AreaRecommendation:
    """Compute the best area for a single template card (metadata dict)."""
    template_id = card.get("id") or card.get("name") or "unknown"
    artifact_type = card.get("artifact_type")

    # Collect every plausible area for the candidates list, in priority order.
    ordered: list[str] = []

    def _add(slug: Optional[str]) -> None:
        if slug and slug in _VALID_AREA_SLUGS and slug not in ordered:
            ordered.append(slug)

    tag_hits = _tag_matches(card.get("tags") or [])
    domain = card.get("domain")
    category = card.get("category")
    domain_area = _DOMAIN_AREA_MAP.get(str(domain)) if domain else None
    category_area = _CATEGORY_AREA_MAP.get(str(category)) if category else None

    explicit = card.get("recommended_area")
    if explicit and explicit in _VALID_AREA_SLUGS:
        _add(explicit)
    for area, _tag in tag_hits:
        _add(area)
    _add(domain_area)
    _add(category_area)

    def _build(slug: Optional[str], source: RecommendationSource, rationale: str) -> AreaRecommendation:
        candidates = [s for s in ordered if s != slug]
        return AreaRecommendation(
            template_id=template_id,
            artifact_type=artifact_type,
            area_slug=slug,
            area_label=_AREA_LABELS.get(slug) if slug else None,
            source=source,
            rationale=rationale,
            candidates=candidates,
        )

    if explicit and explicit in _VALID_AREA_SLUGS:
        return _build(
            explicit,
            "template_default",
            f"Template default area '{_AREA_LABELS[explicit]}'.",
        )

    if tag_hits:
        area, tag = tag_hits[0]
        return _build(
            area,
            "tag_match",
            f"Capability tag '{tag}' → {_AREA_LABELS[area]}.",
        )

    if domain_area:
        return _build(
            domain_area,
            "domain_match",
            f"Domain '{domain}' → {_AREA_LABELS[domain_area]}.",
        )

    if category_area:
        return _build(
            category_area,
            "domain_match",
            f"Category '{category}' → {_AREA_LABELS[category_area]}.",
        )

    return _build(
        None,
        "fallback",
        "No metadata match — assign an area manually.",
    )


def recommend_areas(cards: Iterable[dict]) -> list[AreaRecommendation]:
    """Compute recommendations for a batch of cards, preserving input order."""
    return [recommend_area_for_card(c) for c in cards]
