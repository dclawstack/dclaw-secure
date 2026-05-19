"""Add compliance_scans table

Revision ID: 0006
Revises: 0005
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    scan_trigger_enum = sa.Enum(
        "manual", "scheduled", "automated",
        name="scan_trigger_type",
    )
    scan_trigger_enum.create(op.get_bind(), checkfirst=True)

    compliance_scan_status_enum = sa.Enum(
        "pending", "running", "completed", "failed",
        name="compliance_scan_status",
    )
    compliance_scan_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "compliance_scans",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("framework_id", sa.UUID(), nullable=False),
        sa.Column("triggered_by", sa.String(255), nullable=True),
        sa.Column(
            "scan_type",
            sa.Enum("manual", "scheduled", "automated", name="scan_trigger_type", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "running", "completed", "failed", name="compliance_scan_status", create_type=False),
            nullable=False,
            server_default="completed",
        ),
        sa.Column("controls_checked", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("controls_passed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("controls_failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("gap_analysis", sa.Text(), nullable=True),
        sa.Column("recommendations", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["framework_id"], ["compliance_frameworks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_compliance_scans_framework_id", "compliance_scans", ["framework_id"])


def downgrade() -> None:
    op.drop_index("ix_compliance_scans_framework_id", "compliance_scans")
    op.drop_table("compliance_scans")
    sa.Enum(name="compliance_scan_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="scan_trigger_type").drop(op.get_bind(), checkfirst=True)
