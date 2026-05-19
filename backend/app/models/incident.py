"""Incident response model."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.utils import utc_now
from app.models.base import Base


class IncidentType(StrEnum):
    breach = "breach"
    phishing = "phishing"
    ransomware = "ransomware"
    insider_threat = "insider_threat"
    ddos = "ddos"
    vulnerability_exploit = "vulnerability_exploit"
    other = "other"


class IncidentStatus(StrEnum):
    open = "open"
    investigating = "investigating"
    contained = "contained"
    resolved = "resolved"
    closed = "closed"


class ActionType(StrEnum):
    detected = "detected"
    escalated = "escalated"
    contained = "contained"
    notified = "notified"
    remediated = "remediated"
    closed = "closed"
    custom = "custom"


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus, name="incident_status_enum"),
        nullable=False,
        default=IncidentStatus.open,
    )
    incident_type: Mapped[IncidentType] = mapped_column(
        Enum(IncidentType, name="incident_type_enum"), nullable=False
    )
    affected_asset_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    contained_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ai_playbook: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now, onupdate=utc_now
    )

    actions: Mapped[list["IncidentAction"]] = relationship(
        "IncidentAction",
        back_populates="incident",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class IncidentAction(Base):
    __tablename__ = "incident_actions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False
    )
    action_type: Mapped[ActionType] = mapped_column(
        Enum(ActionType, name="action_type_enum"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    performed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    performed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)

    incident: Mapped["Incident"] = relationship(
        "Incident", back_populates="actions", lazy="selectin"
    )
