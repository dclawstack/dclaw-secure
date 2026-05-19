"""Add secret_scan_jobs and secret_findings tables

Revision ID: 0008
Revises: 0007
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    scan_target_type_enum = sa.Enum(
        "filesystem", "git_repo", "config_file", "manual_input",
        name="scan_target_type",
    )
    scan_target_type_enum.create(op.get_bind(), checkfirst=True)

    secret_type_enum = sa.Enum(
        "api_key", "password", "token", "certificate", "database_url",
        "private_key", "jwt_secret", "other",
        name="secret_type",
    )
    secret_type_enum.create(op.get_bind(), checkfirst=True)

    secret_scan_status_enum = sa.Enum(
        "pending", "running", "completed", "failed",
        name="secret_scan_status",
    )
    secret_scan_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "secret_scan_jobs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("scan_target", sa.String(512), nullable=False),
        sa.Column(
            "scan_type",
            sa.Enum(
                "filesystem", "git_repo", "config_file", "manual_input",
                name="scan_target_type", create_type=False,
            ),
            nullable=False,
            server_default="manual_input",
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "running", "completed", "failed", name="secret_scan_status", create_type=False),
            nullable=False,
            server_default="completed",
        ),
        sa.Column("files_scanned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("secrets_found", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_secret_scan_jobs_created_at", "secret_scan_jobs", ["created_at"])

    op.create_table(
        "secret_findings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("job_id", sa.UUID(), nullable=False),
        sa.Column("file_path", sa.String(512), nullable=True),
        sa.Column("line_number", sa.Integer(), nullable=True),
        sa.Column(
            "secret_type",
            sa.Enum(
                "api_key", "password", "token", "certificate", "database_url",
                "private_key", "jwt_secret", "other",
                name="secret_type", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("severity", sa.String(50), nullable=False, server_default="high"),
        sa.Column("masked_value", sa.String(255), nullable=False),
        sa.Column("is_revoked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_false_positive", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("detected_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["secret_scan_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_secret_findings_job_id", "secret_findings", ["job_id"])
    op.create_index("ix_secret_findings_secret_type", "secret_findings", ["secret_type"])


def downgrade() -> None:
    op.drop_index("ix_secret_findings_secret_type", "secret_findings")
    op.drop_index("ix_secret_findings_job_id", "secret_findings")
    op.drop_table("secret_findings")
    op.drop_index("ix_secret_scan_jobs_created_at", "secret_scan_jobs")
    op.drop_table("secret_scan_jobs")
    sa.Enum(name="secret_scan_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="secret_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="scan_target_type").drop(op.get_bind(), checkfirst=True)
