"""integration profiles — integration_profile table

Revision ID: 0003_integration_profiles
Revises: 0002_local_inference
Create Date: 2026-07-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_integration_profiles"
down_revision = "0002_local_inference"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "integration_profile",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("adapter_id", sa.String(64), nullable=False, index=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("base_url", sa.Text, nullable=True),
        sa.Column("config_json", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("secret_refs_json", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("template_ids_json", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("adapter_id", "name", name="uq_integration_profile_adapter_name"),
    )


def downgrade() -> None:
    op.drop_table("integration_profile")
