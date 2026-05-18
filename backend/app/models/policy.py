"""Policy and PolicyAcknowledgment models."""

import uuid
from datetime import datetime, date
from enum import StrEnum

from sqlalchemy import String, Text, Boolean, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.core.utils import utc_now


class PolicyStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PolicyCategory(StrEnum):
    ACCESS_CONTROL = "access_control"
    DATA_PROTECTION = "data_protection"
    INCIDENT_RESPONSE = "incident_response"
    ACCEPTABLE_USE = "acceptable_use"
    REMOTE_WORK = "remote_work"


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[PolicyStatus] = mapped_column(
        Enum(PolicyStatus), nullable=False, default=PolicyStatus.DRAFT
    )
    category: Mapped[PolicyCategory] = mapped_column(Enum(PolicyCategory), nullable=False)
    requires_acknowledgment: Mapped[bool] = mapped_column(Boolean, default=True)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)

    acknowledgments: Mapped[list["PolicyAcknowledgment"]] = relationship(
        "PolicyAcknowledgment", back_populates="policy", lazy="selectin"
    )


class PolicyAcknowledgment(Base):
    __tablename__ = "policy_acknowledgments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    policy_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("policies.id", ondelete="CASCADE"), nullable=False
    )
    employee_email: Mapped[str] = mapped_column(String(255), nullable=False)
    employee_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)

    policy: Mapped["Policy"] = relationship("Policy", back_populates="acknowledgments", lazy="selectin")
