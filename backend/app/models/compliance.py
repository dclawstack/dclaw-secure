"""ComplianceFramework and ComplianceControl models."""

import uuid
from datetime import datetime, date
from enum import StrEnum

from sqlalchemy import String, Text, Boolean, Date, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.core.utils import utc_now


class ControlStatus(StrEnum):
    NOT_IMPLEMENTED = "not_implemented"
    PARTIALLY_IMPLEMENTED = "partially_implemented"
    IMPLEMENTED = "implemented"
    NOT_APPLICABLE = "not_applicable"


class ComplianceFramework(Base):
    __tablename__ = "compliance_frameworks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)

    controls: Mapped[list["ComplianceControl"]] = relationship(
        "ComplianceControl", back_populates="framework", lazy="selectin"
    )


class ComplianceControl(Base):
    __tablename__ = "compliance_controls"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    framework_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("compliance_frameworks.id", ondelete="CASCADE"), nullable=False
    )
    control_id: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[ControlStatus] = mapped_column(
        Enum(ControlStatus), nullable=False, default=ControlStatus.NOT_IMPLEMENTED
    )
    evidence_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)

    framework: Mapped["ComplianceFramework"] = relationship(
        "ComplianceFramework", back_populates="controls", lazy="selectin"
    )
