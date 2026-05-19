"""Add SIEM events table

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    event_type_enum = sa.Enum(
        "authentication", "network", "endpoint", "application", "cloud", "threat",
        name="siem_event_type",
    )
    event_type_enum.create(op.get_bind(), checkfirst=True)

    siem_severity_enum = sa.Enum(
        "critical", "high", "medium", "low", "info",
        name="siem_severity",
    )
    siem_severity_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "siem_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source_system", sa.String(255), nullable=False),
        sa.Column("event_type", sa.Enum("authentication", "network", "endpoint", "application", "cloud", "threat", name="siem_event_type", create_type=False), nullable=False),
        sa.Column("severity", sa.Enum("critical", "high", "medium", "low", "info", name="siem_severity", create_type=False), nullable=False, server_default="info"),
        sa.Column("raw_event", sa.JSON(), nullable=True),
        sa.Column("normalized_data", sa.JSON(), nullable=True),
        sa.Column("asset_id", sa.UUID(), nullable=True),
        sa.Column("correlation_id", sa.UUID(), nullable=True),
        sa.Column("is_anomaly", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("ai_analysis", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_siem_events_event_type", "siem_events", ["event_type"])
    op.create_index("ix_siem_events_is_anomaly", "siem_events", ["is_anomaly"])
    op.create_index("ix_siem_events_occurred_at", "siem_events", ["occurred_at"])


def downgrade() -> None:
    op.drop_index("ix_siem_events_occurred_at", "siem_events")
    op.drop_index("ix_siem_events_is_anomaly", "siem_events")
    op.drop_index("ix_siem_events_event_type", "siem_events")
    op.drop_table("siem_events")
    sa.Enum(name="siem_event_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="siem_severity").drop(op.get_bind(), checkfirst=True)
