"""Add threat intelligence tables

Revision ID: 0010
Revises: 0009
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    feed_type_enum = sa.Enum(
        "ip_blocklist", "domain_blocklist", "hash_list", "cve_feed", "custom",
        name="feed_type_enum",
    )
    feed_type_enum.create(op.get_bind(), checkfirst=True)

    ioc_type_enum = sa.Enum(
        "ip", "domain", "hash", "url", "email", "cve",
        name="ioc_type_enum",
    )
    ioc_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "threat_feeds",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "feed_type",
            sa.Enum(
                "ip_blocklist", "domain_blocklist", "hash_list", "cve_feed", "custom",
                name="feed_type_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("source_url", sa.String(1024), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_synced", sa.DateTime(), nullable=True),
        sa.Column("ioc_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_threat_feeds_feed_type", "threat_feeds", ["feed_type"])

    op.create_table(
        "threat_iocs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("feed_id", sa.UUID(), nullable=True),
        sa.Column(
            "ioc_type",
            sa.Enum(
                "ip", "domain", "hash", "url", "email", "cve",
                name="ioc_type_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("value", sa.String(512), nullable=False),
        sa.Column("threat_type", sa.String(100), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("first_seen", sa.DateTime(), nullable=False),
        sa.Column("last_seen", sa.DateTime(), nullable=True),
        sa.Column("ioc_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["feed_id"], ["threat_feeds.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_threat_iocs_feed_id", "threat_iocs", ["feed_id"])
    op.create_index("ix_threat_iocs_ioc_type", "threat_iocs", ["ioc_type"])
    op.create_index("ix_threat_iocs_is_active", "threat_iocs", ["is_active"])
    op.create_index("ix_threat_iocs_value", "threat_iocs", ["value"])


def downgrade() -> None:
    op.drop_index("ix_threat_iocs_value", "threat_iocs")
    op.drop_index("ix_threat_iocs_is_active", "threat_iocs")
    op.drop_index("ix_threat_iocs_ioc_type", "threat_iocs")
    op.drop_index("ix_threat_iocs_feed_id", "threat_iocs")
    op.drop_table("threat_iocs")
    op.drop_index("ix_threat_feeds_feed_type", "threat_feeds")
    op.drop_table("threat_feeds")
    sa.Enum(name="ioc_type_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="feed_type_enum").drop(op.get_bind(), checkfirst=True)
