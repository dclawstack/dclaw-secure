"""Add incident response tables

Revision ID: 0009
Revises: 0008
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    incident_type_enum = sa.Enum(
        "breach", "phishing", "ransomware", "insider_threat",
        "ddos", "vulnerability_exploit", "other",
        name="incident_type_enum",
    )
    incident_type_enum.create(op.get_bind(), checkfirst=True)

    incident_status_enum = sa.Enum(
        "open", "investigating", "contained", "resolved", "closed",
        name="incident_status_enum",
    )
    incident_status_enum.create(op.get_bind(), checkfirst=True)

    action_type_enum = sa.Enum(
        "detected", "escalated", "contained", "notified",
        "remediated", "closed", "custom",
        name="action_type_enum",
    )
    action_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "incidents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(50), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "open", "investigating", "contained", "resolved", "closed",
                name="incident_status_enum",
                create_type=False,
            ),
            nullable=False,
            server_default="open",
        ),
        sa.Column(
            "incident_type",
            sa.Enum(
                "breach", "phishing", "ransomware", "insider_threat",
                "ddos", "vulnerability_exploit", "other",
                name="incident_type_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("affected_asset_ids", sa.JSON(), nullable=True),
        sa.Column("assigned_to", sa.String(255), nullable=True),
        sa.Column("detected_at", sa.DateTime(), nullable=False),
        sa.Column("contained_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("ai_playbook", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_incidents_status", "incidents", ["status"])
    op.create_index("ix_incidents_incident_type", "incidents", ["incident_type"])
    op.create_index("ix_incidents_severity", "incidents", ["severity"])
    op.create_index("ix_incidents_created_at", "incidents", ["created_at"])

    op.create_table(
        "incident_actions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("incident_id", sa.UUID(), nullable=False),
        sa.Column(
            "action_type",
            sa.Enum(
                "detected", "escalated", "contained", "notified",
                "remediated", "closed", "custom",
                name="action_type_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("performed_by", sa.String(255), nullable=True),
        sa.Column("performed_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_incident_actions_incident_id", "incident_actions", ["incident_id"])


def downgrade() -> None:
    op.drop_index("ix_incident_actions_incident_id", "incident_actions")
    op.drop_table("incident_actions")
    op.drop_index("ix_incidents_created_at", "incidents")
    op.drop_index("ix_incidents_severity", "incidents")
    op.drop_index("ix_incidents_incident_type", "incidents")
    op.drop_index("ix_incidents_status", "incidents")
    op.drop_table("incidents")
    sa.Enum(name="action_type_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="incident_status_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="incident_type_enum").drop(op.get_bind(), checkfirst=True)
