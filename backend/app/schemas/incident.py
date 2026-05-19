"""Pydantic schemas for Incident Response."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

IncidentTypeLiteral = Literal[
    "breach", "phishing", "ransomware", "insider_threat",
    "ddos", "vulnerability_exploit", "other"
]
IncidentStatusLiteral = Literal[
    "open", "investigating", "contained", "resolved", "closed"
]
ActionTypeLiteral = Literal[
    "detected", "escalated", "contained", "notified", "remediated", "closed", "custom"
]
SeverityLiteral = Literal["critical", "high", "medium", "low"]


class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    severity: SeverityLiteral
    incident_type: IncidentTypeLiteral
    affected_asset_ids: list[str] | None = None
    assigned_to: str | None = Field(None, max_length=255)


class IncidentUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    severity: SeverityLiteral | None = None
    incident_type: IncidentTypeLiteral | None = None
    status: IncidentStatusLiteral | None = None
    affected_asset_ids: list[str] | None = None
    assigned_to: str | None = Field(None, max_length=255)
    contained_at: datetime | None = None
    resolved_at: datetime | None = None
    ai_playbook: str | None = None


class IncidentActionCreate(BaseModel):
    action_type: ActionTypeLiteral
    description: str = Field(..., min_length=1)
    performed_by: str | None = Field(None, max_length=255)


class IncidentActionOut(BaseModel):
    id: uuid.UUID
    incident_id: uuid.UUID
    action_type: str
    description: str
    performed_by: str | None
    performed_at: datetime
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class IncidentOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    severity: str
    status: str
    incident_type: str
    affected_asset_ids: list | None
    assigned_to: str | None
    detected_at: datetime
    contained_at: datetime | None
    resolved_at: datetime | None
    ai_playbook: str | None
    created_at: datetime
    updated_at: datetime
    actions: list[IncidentActionOut] = []
    model_config = ConfigDict(from_attributes=True)


class IncidentListResponse(BaseModel):
    items: list[IncidentOut]
    total: int
    offset: int
    limit: int
    model_config = ConfigDict(from_attributes=True)
