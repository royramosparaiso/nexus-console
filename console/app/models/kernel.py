"""Kernel services \u2014 the always-on core of Nexus.

Kernel services are not part of the stack catalogue. They ship with
every Nexus deployment. The operator cannot toggle them off; they can
only choose the *engine* that backs each one, and only when the choice
is meaningful for their tier.

Today the only kernel service is **Hermes** \u2014 the agent orchestrator.
It handles agent registration, durable job dispatch, hot-deploy of new
agents, and the pub/sub event bus between them.

Hermes is one contract with three engines:

  - ``in_process``       : embedded in nexus-platform. Uses Postgres
                           (LISTEN/NOTIFY + a jobs table) as the durable
                           queue. Zero extra infrastructure. Fine up
                           to a few thousand jobs/second.
  - ``temporal_cloud``   : Hermes delegates the durable queue to a
                           Temporal Cloud namespace. Managed retries,
                           timeouts and workflows. Recommended for
                           standard tier and above.
  - ``temporal_selfhost``: Temporal deployed and operated by the user.
                           Recommended for scale tier when the operator
                           wants full control.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

HermesEngine = Literal["in_process", "temporal_cloud", "temporal_selfhost"]

# Which engine we auto-pick for each stack tier when the operator
# doesn't override. In hobby and standard we stay embedded \u2014 the
# Postgres already in the stack is enough. In scale we push people
# to a managed cluster.
HERMES_ENGINE_BY_TIER: dict[str, HermesEngine] = {
    "free":     "in_process",
    "hobby":    "in_process",
    "standard": "in_process",
    "scale":    "temporal_cloud",
}


class HermesConfig(BaseModel):
    """How Hermes runs on this deployment."""

    engine: HermesEngine = "in_process"
    # Same contract every engine exposes.
    features: list[str] = Field(
        default_factory=lambda: [
            "agent_registry",
            "durable_job_dispatch",
            "hot_deploy_agents",
            "event_bus",
        ],
        description=(
            "The four kernel capabilities Hermes always provides. Do "
            "not remove entries \u2014 downstream code (platform, agents) "
            "assumes all four are available."
        ),
    )

    def required_secrets(self) -> list[str]:
        # Env vars needed to bring this engine online.
        if self.engine == "in_process":
            # Reuses the platform's DATABASE_URL \u2014 no extra secret.
            return []
        if self.engine == "temporal_cloud":
            return [
                "TEMPORAL_CLOUD_NAMESPACE",
                "TEMPORAL_CLOUD_API_KEY",
                "TEMPORAL_CLOUD_ADDRESS",
            ]
        # self-host
        return ["TEMPORAL_HOST", "TEMPORAL_NAMESPACE"]


class KernelServices(BaseModel):
    # Everything that ships with every Nexus deployment.
    #
    # Not configurable through the stack catalogue. The wizard surfaces
    # the engine choice for informational purposes and to shape the
    # handoff, but the *presence* of every field here is guaranteed.

    hermes: HermesConfig = Field(default_factory=HermesConfig)


def default_kernel_for_tier(tier: str) -> KernelServices:
    # Pick the sensible defaults for a given stack tier.
    engine = HERMES_ENGINE_BY_TIER.get(tier, "in_process")
    return KernelServices(hermes=HermesConfig(engine=engine))
