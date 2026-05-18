"""add policies, compliance frameworks/controls, ai chat

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enum types ────────────────────────────────────────────────────────────
    policystatus = sa.Enum("draft", "published", "archived", name="policystatus")
    policycategory = sa.Enum(
        "access_control", "data_protection", "incident_response",
        "acceptable_use", "remote_work",
        name="policycategory",
    )
    controlstatus = sa.Enum(
        "not_implemented", "partially_implemented", "implemented", "not_applicable",
        name="controlstatus",
    )
    messagerole = sa.Enum("user", "assistant", "system", name="messagerole")

    for enum in (policystatus, policycategory, controlstatus, messagerole):
        enum.create(op.get_bind(), checkfirst=True)

    # ── policies ──────────────────────────────────────────────────────────────
    op.create_table(
        "policies",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("status", sa.Enum("draft", "published", "archived", name="policystatus", create_type=False), nullable=False),
        sa.Column("category", sa.Enum("access_control", "data_protection", "incident_response", "acceptable_use", "remote_work", name="policycategory", create_type=False), nullable=False),
        sa.Column("requires_acknowledgment", sa.Boolean(), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── policy_acknowledgments ────────────────────────────────────────────────
    op.create_table(
        "policy_acknowledgments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("policy_id", sa.UUID(), nullable=False),
        sa.Column("employee_email", sa.String(255), nullable=False),
        sa.Column("employee_name", sa.String(255), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["policy_id"], ["policies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── compliance_frameworks ─────────────────────────────────────────────────
    op.create_table(
        "compliance_frameworks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("version", sa.String(50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    # ── compliance_controls ───────────────────────────────────────────────────
    op.create_table(
        "compliance_controls",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("framework_id", sa.UUID(), nullable=False),
        sa.Column("control_id", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(255), nullable=True),
        sa.Column("status", sa.Enum("not_implemented", "partially_implemented", "implemented", "not_applicable", name="controlstatus", create_type=False), nullable=False),
        sa.Column("evidence_url", sa.String(1024), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("assigned_to", sa.String(255), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["framework_id"], ["compliance_frameworks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── ai_chat_sessions ──────────────────────────────────────────────────────
    op.create_table(
        "ai_chat_sessions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── ai_chat_messages ──────────────────────────────────────────────────────
    op.create_table(
        "ai_chat_messages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.Enum("user", "assistant", "system", name="messagerole", create_type=False), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sources", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["ai_chat_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("ai_chat_messages")
    op.drop_table("ai_chat_sessions")
    op.drop_table("compliance_controls")
    op.drop_table("compliance_frameworks")
    op.drop_table("policy_acknowledgments")
    op.drop_table("policies")

    for name in ("messagerole", "controlstatus", "policycategory", "policystatus"):
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
