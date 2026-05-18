"""initial schema: assets, vulnerabilities, security_scans

Revision ID: 0001
Revises:
Create Date: 2026-05-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enum types ────────────────────────────────────────────────────────────
    assettype = sa.Enum(
        "server", "container", "database", "s3_bucket",
        "api", "domain", "repository", "workstation",
        name="assettype",
    )
    environment = sa.Enum(
        "production", "staging", "development",
        name="environment",
    )
    assetstatus = sa.Enum(
        "active", "inactive", "decommissioned",
        name="assetstatus",
    )
    cloudprovider = sa.Enum(
        "aws", "azure", "gcp", "on_premise",
        name="cloudprovider",
    )
    vulnseverity = sa.Enum(
        "critical", "high", "medium", "low", "info",
        name="vulnseverity",
    )
    vulnstatus = sa.Enum(
        "open", "in_progress", "resolved", "accepted_risk",
        name="vulnstatus",
    )
    scantype = sa.Enum(
        "vulnerability", "container", "api", "web", "compliance",
        name="scantype",
    )
    scanstatus = sa.Enum(
        "pending", "running", "completed", "failed",
        name="scanstatus",
    )

    for enum in (assettype, environment, assetstatus, cloudprovider,
                 vulnseverity, vulnstatus, scantype, scanstatus):
        enum.create(op.get_bind(), checkfirst=True)

    # ── assets ────────────────────────────────────────────────────────────────
    op.create_table(
        "assets",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("asset_type", sa.Enum("server", "container", "database", "s3_bucket", "api", "domain", "repository", "workstation", name="assettype", create_type=False), nullable=False),
        sa.Column("environment", sa.Enum("production", "staging", "development", name="environment", create_type=False), nullable=False),
        sa.Column("status", sa.Enum("active", "inactive", "decommissioned", name="assetstatus", create_type=False), nullable=False),
        sa.Column("cloud_provider", sa.Enum("aws", "azure", "gcp", "on_premise", name="cloudprovider", create_type=False), nullable=True),
        sa.Column("region", sa.String(100), nullable=True),
        sa.Column("owner_email", sa.String(255), nullable=True),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── vulnerabilities ───────────────────────────────────────────────────────
    op.create_table(
        "vulnerabilities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("asset_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.Enum("critical", "high", "medium", "low", "info", name="vulnseverity", create_type=False), nullable=False),
        sa.Column("cvss_score", sa.Float(), nullable=True),
        sa.Column("cve_id", sa.String(50), nullable=True),
        sa.Column("status", sa.Enum("open", "in_progress", "resolved", "accepted_risk", name="vulnstatus", create_type=False), nullable=False),
        sa.Column("remediation", sa.Text(), nullable=True),
        sa.Column("discovered_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── security_scans ────────────────────────────────────────────────────────
    op.create_table(
        "security_scans",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("target_asset_id", sa.UUID(), nullable=False),
        sa.Column("scan_type", sa.Enum("vulnerability", "container", "api", "web", "compliance", name="scantype", create_type=False), nullable=False),
        sa.Column("status", sa.Enum("pending", "running", "completed", "failed", name="scanstatus", create_type=False), nullable=False),
        sa.Column("findings_count", sa.Integer(), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("scan_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["target_asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("security_scans")
    op.drop_table("vulnerabilities")
    op.drop_table("assets")

    for name in ("scanstatus", "scantype", "vulnstatus", "vulnseverity",
                 "cloudprovider", "assetstatus", "environment", "assettype"):
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
