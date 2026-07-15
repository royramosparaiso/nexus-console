"""Generic integration adapter layer.

Rather than vendoring dozens of brittle provider SDKs, Nexus models every
external AI building block as a *data descriptor* (an :class:`Adapter`) plus a
small set of reusable connection probes. An operator creates an
:class:`~app.models.db.IntegrationProfileRow` referencing an adapter, supplies
non-secret config and *env-var references* for secrets (never raw values), and
Nexus can then health-check the endpoint and resolve enabled capabilities for
agent/sidecar manifests.

See :mod:`app.services.integrations.registry` for the catalogue,
:mod:`app.services.integrations.probes` for the connection tests, and
:mod:`app.services.integrations.resolver` for capability resolution.
"""

from app.services.integrations.registry import (
    ADAPTERS,
    Adapter,
    FieldSpec,
    ProbeKind,
    SecretSpec,
    adapter_by_id,
    adapters_by_category,
)

__all__ = [
    "ADAPTERS",
    "Adapter",
    "FieldSpec",
    "ProbeKind",
    "SecretSpec",
    "adapter_by_id",
    "adapters_by_category",
]
