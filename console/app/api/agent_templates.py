"""Read-only endpoints exposing the agent-template catalogue to the frontend.

The catalogue itself is a bunch of markdown files under
``console/agent_templates/`` plus a generated ``catalog.json`` (produced by
``scripts/build_agent_templates_index.py``). We serve the JSON as-is and
provide a second endpoint for the raw markdown body of any card so the UI
can render detail views without shipping every card into the initial payload.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()

# console/app/api/agent_templates.py -> console/agent_templates/
_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "agent_templates"
_CATALOG_JSON = _TEMPLATES_DIR / "catalog.json"


@lru_cache(maxsize=1)
def _load_catalog() -> dict:
    if not _CATALOG_JSON.is_file():
        raise HTTPException(
            status_code=503,
            detail=(
                "catalog.json not found — regenerate with "
                "`python scripts/build_agent_templates_index.py`"
            ),
        )
    return json.loads(_CATALOG_JSON.read_text(encoding="utf-8"))


@router.get("")
async def list_agent_templates() -> dict:
    """Full catalogue payload: cards + indexes + enum vocab."""
    return _load_catalog()


@router.get("/{card_id}")
async def get_agent_template(card_id: str) -> dict:
    """Return the frontmatter + raw markdown body of a single card."""
    catalog = _load_catalog()
    match = next((c for c in catalog["cards"] if c["id"] == card_id), None)
    if match is None:
        raise HTTPException(status_code=404, detail=f"agent template {card_id!r} not found")

    path = _TEMPLATES_DIR / match["path"]
    if not path.is_file():
        raise HTTPException(status_code=500, detail=f"catalog path missing on disk: {match['path']}")

    body = path.read_text(encoding="utf-8")
    # Strip the YAML frontmatter — the JSON view already has it.
    if body.startswith("---\n"):
        end = body.find("\n---\n", 4)
        if end != -1:
            body = body[end + 5:]
    return {"card": match, "body": body.lstrip("\n")}
