"""SQLAlchemy ORM models for Console.

Just three tables at v0.6:
- console_keypair: singleton — the Console's Ed25519 keypair
- instance: registry of provisioned Platform instances
- notification: inbound events from Platforms
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import JSON, String, Text
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
    return datetime.now(timezone.utc)


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
    created_at: Mapped[datetime] = mapped_column(default=_now)
    bootstrapped_at: Mapped[datetime | None] = mapped_column(nullable=True)


class NotificationRow(Base):
    __tablename__ = "notification"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ts: Mapped[datetime] = mapped_column(default=_now, index=True)
    instance_id: Mapped[UUID | None] = mapped_column(_UUID(), nullable=True, index=True)
    kind: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    verified: Mapped[bool] = mapped_column(default=False)
