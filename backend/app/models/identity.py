import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.utils import utc_now
from app.models.base import Base


class BehaviorEventType(StrEnum):
    LOGIN = "login"
    LOGOUT = "logout"
    FILE_ACCESS = "file_access"
    API_CALL = "api_call"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXPORT = "data_export"
    FAILED_AUTH = "failed_auth"


class IdentityProfile(Base):
    __tablename__ = "identity_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ai_analysis: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    behaviors: Mapped[list["BehaviorEvent"]] = relationship(
        "BehaviorEvent", back_populates="identity", lazy="selectin", cascade="all, delete-orphan"
    )


class BehaviorEvent(Base):
    __tablename__ = "behavior_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    identity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("identity_profiles.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[BehaviorEventType] = mapped_column(
        Enum(BehaviorEventType, name="behavior_event_type"), nullable=False
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    event_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    risk_contribution: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_flagged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)

    identity: Mapped["IdentityProfile"] = relationship("IdentityProfile", back_populates="behaviors", lazy="selectin")
