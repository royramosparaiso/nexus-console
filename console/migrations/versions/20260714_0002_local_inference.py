"""local inference — agent_local_model table + instance.local_inference flag

Revision ID: 0002_local_inference
Revises: 0001_initial
Create Date: 2026-07-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_local_inference"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "instance",
        sa.Column(
            "local_inference",
            sa.Boolean,
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.create_table(
        "agent_local_model",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        # Soft reference to an agent_templates catalogue card id — not a FK,
        # because agents are markdown cards, not a SQL table.
        sa.Column("template_id", sa.String(128), nullable=False, index=True),
        sa.Column("model_url", sa.Text, nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.BigInteger, nullable=False),
        sa.Column("license", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("template_id", "model_url", name="uq_agent_local_model_template_url"),
        sa.CheckConstraint("length(sha256) = 64", name="ck_agent_local_model_sha256_len"),
        sa.CheckConstraint("size_bytes >= 0", name="ck_agent_local_model_size_nonneg"),
    )


def downgrade() -> None:
    op.drop_table("agent_local_model")
    op.drop_column("instance", "local_inference")
