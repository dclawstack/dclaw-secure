"""Security scan model for scan records."""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.core.utils import utc_now


class ScanType(StrEnum):
    VULNERABILITY = "vulnerability"
    CONTAINER = "container"
    API = "api"
    WEB = "web"
    COMPLIANCE = "compliance"


class ScanStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SecurityScan(Base):
    """Record of a security scan run against an asset."""

    __tablename__ = "security_scans"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    target_asset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=False
    )
    scan_type: Mapped[ScanType] = mapped_column(Enum(ScanType), nullable=False)
    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus), nullable=False, default=ScanStatus.PENDING
    )
    findings_count: Mapped[int] = mapped_column(Integer, default=0)
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(default=utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    scan_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        default=utc_now, onupdate=utc_now
    )

    target_asset: Mapped["Asset"] = relationship("Asset", lazy="selectin")

    def __repr__(self) -> str:
        return f"<SecurityScan {self.scan_type.value} on {self.target_asset_id} ({self.status.value})>"
