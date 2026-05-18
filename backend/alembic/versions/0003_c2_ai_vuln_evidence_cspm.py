"""C2: AI vuln prioritization fields, compliance evidence table

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── C2.1: AI prioritization columns on vulnerabilities ────────────────────
    op.add_column("vulnerabilities", sa.Column("business_impact_score", sa.Float(), nullable=True))
    op.add_column("vulnerabilities", sa.Column("ai_priority_reason", sa.Text(), nullable=True))

    # ── C2.2: Compliance evidence table ───────────────────────────────────────
    evidencetype = sa.Enum(
        "screenshot", "export", "policy", "scan_report", "manual",
        name="evidencetype",
    )
    evidencetype.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "compliance_evidence",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("control_id", sa.UUID(), nullable=False),
        sa.Column(
            "evidence_type",
            sa.Enum("screenshot", "export", "policy", "scan_report", "manual",
                    name="evidencetype", create_type=False),
            nullable=False,
        ),
        sa.Column("description", sa.String(512), nullable=False),
        sa.Column("artifact_url", sa.String(1024), nullable=True),
        sa.Column("artifact_data", sa.JSON(), nullable=True),
        sa.Column("collected_by", sa.String(255), nullable=True),
        sa.Column("collected_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["control_id"], ["compliance_controls.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("compliance_evidence")
    sa.Enum(name="evidencetype").drop(op.get_bind(), checkfirst=True)
    op.drop_column("vulnerabilities", "ai_priority_reason")
    op.drop_column("vulnerabilities", "business_impact_score")
