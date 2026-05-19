import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String, Text, UUID
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.utils import utc_now
from app.models.base import Base


class EventType(StrEnum):
    AUTHENTICATION = "authentication"
    NETWORK = "network"
    ENDPOINT = "endpoint"
    APPLICATION = "application"
    CLOUD = "cloud"
    THREAT = "threat"


class SiemSeverity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SiemEvent(Base):
    __tablename__ = "siem_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_system: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[EventType] = mapped_column(Enum(EventType, name="siem_event_type"), nullable=False)
    severity: Mapped[SiemSeverity] = mapped_column(Enum(SiemSeverity, name="siem_severity"), nullable=False, default=SiemSeverity.INFO)
    raw_event: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    normalized_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True)
    correlation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
