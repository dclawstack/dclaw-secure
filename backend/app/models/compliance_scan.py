"""ComplianceScan model for tracking automated scan results."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.core.utils import utc_now


class ScanTrigger(StrEnum):
    manual = "manual"
    scheduled = "scheduled"
    automated = "automated"


class ComplianceScanStatus(StrEnum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class ComplianceScan(Base):
    __tablename__ = "compliance_scans"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    framework_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("compliance_frameworks.id", ondelete="CASCADE"), nullable=False
    )
    triggered_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    scan_type: Mapped[ScanTrigger] = mapped_column(
        Enum(ScanTrigger), nullable=False, default=ScanTrigger.manual
    )
    status: Mapped[ComplianceScanStatus] = mapped_column(
        Enum(ComplianceScanStatus), nullable=False, default=ComplianceScanStatus.completed
    )
    controls_checked: Mapped[int] = mapped_column(Integer, default=0)
    controls_passed: Mapped[int] = mapped_column(Integer, default=0)
    controls_failed: Mapped[int] = mapped_column(Integer, default=0)
    gap_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
