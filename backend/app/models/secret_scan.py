"""SecretScanJob and SecretFinding models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.core.utils import utc_now


class ScanTargetType(StrEnum):
    filesystem = "filesystem"
    git_repo = "git_repo"
    config_file = "config_file"
    manual_input = "manual_input"


class SecretType(StrEnum):
    api_key = "api_key"
    password = "password"
    token = "token"
    certificate = "certificate"
    database_url = "database_url"
    private_key = "private_key"
    jwt_secret = "jwt_secret"
    other = "other"


class SecretScanStatus(StrEnum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class SecretScanJob(Base):
    __tablename__ = "secret_scan_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    scan_target: Mapped[str] = mapped_column(String(512), nullable=False)
    scan_type: Mapped[ScanTargetType] = mapped_column(
        Enum(ScanTargetType), nullable=False, default=ScanTargetType.manual_input
    )
    status: Mapped[SecretScanStatus] = mapped_column(
        Enum(SecretScanStatus), nullable=False, default=SecretScanStatus.completed
    )
    files_scanned: Mapped[int] = mapped_column(Integer, default=0)
    secrets_found: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    findings: Mapped[list["SecretFinding"]] = relationship(
        "SecretFinding",
        back_populates="job",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class SecretFinding(Base):
    __tablename__ = "secret_findings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("secret_scan_jobs.id", ondelete="CASCADE"), nullable=False
    )
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    secret_type: Mapped[SecretType] = mapped_column(
        Enum(SecretType), nullable=False
    )
    severity: Mapped[str] = mapped_column(String(50), default="high")
    masked_value: Mapped[str] = mapped_column(String(255), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    is_false_positive: Mapped[bool] = mapped_column(Boolean, default=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    job: Mapped["SecretScanJob"] = relationship(
        "SecretScanJob", back_populates="findings", lazy="selectin"
    )
