"""Add identity security tables

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    behavior_event_type_enum = sa.Enum(
        "login", "logout", "file_access", "api_call",
        "privilege_escalation", "data_export", "failed_auth",
        name="behavior_event_type",
    )
    behavior_event_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "identity_profiles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("role", sa.String(100), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_seen", sa.DateTime(), nullable=True),
        sa.Column("ai_analysis", sa.String(1024), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_identity_profiles_email", "identity_profiles", ["email"])
    op.create_index("ix_identity_profiles_risk_score", "identity_profiles", ["risk_score"])

    op.create_table(
        "behavior_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("identity_id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.Enum("login", "logout", "file_access", "api_call", "privilege_escalation", "data_export", "failed_auth", name="behavior_event_type", create_type=False), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("event_metadata", sa.JSON(), nullable=True),
        sa.Column("risk_contribution", sa.Float(), nullable=False, server_default="0"),
        sa.Column("is_flagged", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["identity_id"], ["identity_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_behavior_events_identity_id", "behavior_events", ["identity_id"])
    op.create_index("ix_behavior_events_occurred_at", "behavior_events", ["occurred_at"])


def downgrade() -> None:
    op.drop_index("ix_behavior_events_occurred_at", "behavior_events")
    op.drop_index("ix_behavior_events_identity_id", "behavior_events")
    op.drop_table("behavior_events")
    op.drop_index("ix_identity_profiles_risk_score", "identity_profiles")
    op.drop_index("ix_identity_profiles_email", "identity_profiles")
    op.drop_table("identity_profiles")
    sa.Enum(name="behavior_event_type").drop(op.get_bind(), checkfirst=True)
