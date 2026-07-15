"""SQLAlchemy ORM models for Console.

Just three tables at v0.6:
- console_keypair: singleton — the Console's Ed25519 keypair
- instance: registry of provisioned Platform instances
- notification: inbound events from Platforms
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON, BigInteger, CheckConstraint, String, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator, CHAR


class _UUID(TypeDecorator):
    """Portable UUID — postgres UUID in prod, CHAR(36) on sqlite."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, UUID):
            return value
        return UUID(value)


def _now() -> datetime:
    # DB columns are TIMESTAMP WITHOUT TIME ZONE; return naive UTC so
    # asyncpg doesn't reject tz-aware datetimes on Postgres.
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class ConsoleKeypairRow(Base):
    """Singleton — one Console = one keypair. Kid is always 'console'."""

    __tablename__ = "console_keypair"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    private_pem: Mapped[str] = mapped_column(Text)
    public_pem: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=_now)


class InstanceRow(Base):
    __tablename__ = "instance"

    id: Mapped[UUID] = mapped_column(_UUID(), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    persona_kind: Mapped[str] = mapped_column(String(32))
    persona_display_name: Mapped[str] = mapped_column(String(100))
    modality: Mapped[str] = mapped_column(String(32))
    agent_runtime: Mapped[str] = mapped_column(String(32), default="in_process")
    auth_provider: Mapped[str] = mapped_column(String(32), default="password_totp")

    # Bootstrap state
    bootstrap_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    endpoint: Mapped[str | None] = mapped_column(Text, nullable=True)
    platform_public_key_pem: Mapped[str | None] = mapped_column(Text, nullable=True)
    platform_version: Mapped[str | None] = mapped_column(String(16), nullable=True)

    # Deployment artefacts
    compose_dir: Mapped[str | None] = mapped_column(Text, nullable=True)
    yaml_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Full manifest as JSON (nexus_core.InstanceManifest.model_dump)
    manifest_json: Mapped[dict] = mapped_column(JSON)

    status: Mapped[str] = mapped_column(String(32), default="bootstrap-pending")
    error_detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Feature flag: when true this instance is allowed to serve browser-local
    # inference models (LiteRT.js) to its agents. Defaults off so existing
    # instances keep today's remote-only behaviour until explicitly enabled.
    local_inference: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=_now)
    bootstrapped_at: Mapped[datetime | None] = mapped_column(nullable=True)


class AgentLocalModelRow(Base):
    """Registry of browser-local inference models an agent template may load.

    Linkage note: the catalogue has no `agents` SQL table — agents are markdown
    cards in ``console/agent_templates/catalog.json`` keyed by a string ``id``.
    ``template_id`` is therefore a *soft* reference to that catalogue card id,
    not a foreign key. We deliberately avoid a fake FK to a non-table catalogue
    identifier; integrity of the reference is enforced at the API/service layer.

    Registering a model here is what lets the Platform decide which ``.tflite``
    a given agent is permitted to fetch and run via LiteRT.js — without it any
    agent could load an arbitrary model URL.
    """

    __tablename__ = "agent_local_model"
    __table_args__ = (
        # A given template references a given model URL at most once.
        UniqueConstraint("template_id", "model_url", name="uq_agent_local_model_template_url"),
        # sha256 is a hex digest — exactly 64 chars.
        CheckConstraint("length(sha256) = 64", name="ck_agent_local_model_sha256_len"),
        CheckConstraint("size_bytes >= 0", name="ck_agent_local_model_size_nonneg"),
    )

    id: Mapped[UUID] = mapped_column(_UUID(), primary_key=True, default=uuid4)
    # Soft reference to an agent_templates catalogue card id (e.g. "voice_vad").
    template_id: Mapped[str] = mapped_column(String(128), index=True)
    model_url: Mapped[str] = mapped_column(Text)
    sha256: Mapped[str] = mapped_column(String(64))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    license: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(default=_now)
    updated_at: Mapped[datetime] = mapped_column(default=_now, onupdate=_now)


class IntegrationProfileRow(Base):
    """An operator-configured instance of an integration adapter.

    Secrets are **never** stored here as plaintext. ``secret_refs`` maps an
    adapter's logical secret key (e.g. ``"api_key"``) to the *name* of the
    environment variable the value is read from at probe/resolve time. This is
    the documented limitation of the current model: without a dedicated vault,
    Nexus holds references, not values.

    ``adapter_id`` is a soft reference to an :class:`app.services.integrations`
    registry adapter (data, not a SQL table), validated at the API layer.
    """

    __tablename__ = "integration_profile"
    __table_args__ = (
        UniqueConstraint("adapter_id", "name", name="uq_integration_profile_adapter_name"),
    )

    id: Mapped[UUID] = mapped_column(_UUID(), primary_key=True, default=uuid4)
    adapter_id: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(120))
    base_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Non-secret config fields (e.g. region, model tag).
    config_json: Mapped[dict] = mapped_column(JSON, default=dict)
    # Logical secret key -> environment variable NAME (never a value).
    secret_refs_json: Mapped[dict] = mapped_column(JSON, default=dict)
    # Soft references to agent_templates catalogue card ids this profile serves.
    # Empty ⇒ available to every agent on the instance.
    template_ids_json: Mapped[list] = mapped_column(JSON, default=list)
    enabled: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=_now)
    updated_at: Mapped[datetime] = mapped_column(default=_now, onupdate=_now)


class NotificationRow(Base):
    __tablename__ = "notification"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ts: Mapped[datetime] = mapped_column(default=_now, index=True)
    instance_id: Mapped[UUID | None] = mapped_column(_UUID(), nullable=True, index=True)
    kind: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    verified: Mapped[bool] = mapped_column(default=False)


class CommandLogRow(Base):
    """Audit + status tracking for commands sent to Platform instances.

    Each row represents a signed command envelope. Status transitions:
        queued → in_progress → applied | failed | rejected

    The Console sets `queued` on insert, `in_progress` right before POSTing
    to the Platform, and then whatever the Platform returns. This lets the
    UI poll for progress on commands that would otherwise look synchronous.
    """

    __tablename__ = "command_log"

    cmd_id: Mapped[UUID] = mapped_column(_UUID(), primary_key=True)
    instance_id: Mapped[UUID] = mapped_column(_UUID(), index=True)
    kind: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(default=_now)
    applied_at: Mapped[datetime | None] = mapped_column(nullable=True)
