"""Threat Intelligence models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.utils import utc_now
from app.models.base import Base


class FeedType(StrEnum):
    ip_blocklist = "ip_blocklist"
    domain_blocklist = "domain_blocklist"
    hash_list = "hash_list"
    cve_feed = "cve_feed"
    custom = "custom"


class IOCType(StrEnum):
    ip = "ip"
    domain = "domain"
    hash = "hash"
    url = "url"
    email = "email"
    cve = "cve"


class ThreatFeed(Base):
    __tablename__ = "threat_feeds"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    feed_type: Mapped[FeedType] = mapped_column(
        Enum(FeedType, name="feed_type_enum"), nullable=False
    )
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_synced: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ioc_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now, onupdate=utc_now
    )

    iocs: Mapped[list["ThreatIOC"]] = relationship(
        "ThreatIOC",
        back_populates="feed",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class ThreatIOC(Base):
    __tablename__ = "threat_iocs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    feed_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("threat_feeds.id", ondelete="SET NULL"), nullable=True
    )
    ioc_type: Mapped[IOCType] = mapped_column(
        Enum(IOCType, name="ioc_type_enum"), nullable=False
    )
    value: Mapped[str] = mapped_column(String(512), nullable=False)
    threat_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ioc_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)

    feed: Mapped["ThreatFeed | None"] = relationship(
        "ThreatFeed", back_populates="iocs", lazy="selectin"
    )
