"""LLM providers management — will migrate the admin panel from ironbat-jarvis."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class ProviderStatus(BaseModel):
    provider: str
    configured: bool
    models: list[str] = Field(default_factory=list)


# Stub — will replace with real secret sync via Console → Platform commands
_PROVIDERS: list[ProviderStatus] = [
    ProviderStatus(provider="anthropic", configured=False, models=["claude-sonnet-4-6", "claude-opus-4-8"]),
    ProviderStatus(provider="openai", configured=False, models=["gpt-5", "gpt-5-mini"]),
    ProviderStatus(provider="openrouter", configured=False, models=[]),
    ProviderStatus(provider="perplexity", configured=False, models=[]),
    ProviderStatus(provider="groq", configured=False, models=[]),
    ProviderStatus(provider="together", configured=False, models=[]),
    ProviderStatus(provider="mistral", configured=False, models=[]),
    ProviderStatus(provider="ollama", configured=False, models=[]),
]


@router.get("", response_model=list[ProviderStatus])
async def list_providers():
    return _PROVIDERS


@router.post("/{provider}/configure")
async def configure_provider(provider: str, body: dict):
    # TODO: store secret in Console vault, dispatch set_llm_provider to relevant instances
    return {"provider": provider, "status": "pending", "note": "stub — will dispatch to instances"}
