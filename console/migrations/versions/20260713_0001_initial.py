"""initial schema — console_keypair + instance + notification

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "console_keypair",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("private_pem", sa.Text, nullable=False),
        sa.Column("public_pem", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "instance",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("persona_kind", sa.String(32), nullable=False),
        sa.Column("persona_display_name", sa.String(100), nullable=False),
        sa.Column("modality", sa.String(32), nullable=False),
        sa.Column("agent_runtime", sa.String(32), nullable=False, server_default="in_process"),
        sa.Column("auth_provider", sa.String(32), nullable=False, server_default="password_totp"),
        sa.Column("bootstrap_token", sa.Text, nullable=True),
        sa.Column("endpoint", sa.Text, nullable=True),
        sa.Column("platform_public_key_pem", sa.Text, nullable=True),
        sa.Column("platform_version", sa.String(16), nullable=True),
        sa.Column("compose_dir", sa.Text, nullable=True),
        sa.Column("yaml_path", sa.Text, nullable=True),
        sa.Column("manifest_json", sa.JSON, nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="bootstrap-pending"),
        sa.Column("error_detail", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("bootstrapped_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "notification",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True),
        sa.Column("instance_id", sa.String(36), nullable=True, index=True),
        sa.Column("kind", sa.String(64), nullable=False, index=True),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("verified", sa.Boolean, nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_table("notification")
    op.drop_table("instance")
    op.drop_table("console_keypair")
