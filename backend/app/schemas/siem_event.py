import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EventTypeLiteral = Literal["authentication", "network", "endpoint", "application", "cloud", "threat"]
SiemSeverityLiteral = Literal["critical", "high", "medium", "low", "info"]


class SiemEventCreate(BaseModel):
    source_system: str = Field(..., min_length=1, max_length=255)
    event_type: EventTypeLiteral
    severity: SiemSeverityLiteral = "info"
    raw_event: dict | None = None
    normalized_data: dict | None = None
    asset_id: uuid.UUID | None = None
    occurred_at: datetime | None = None


class SiemEventOut(BaseModel):
    id: uuid.UUID
    source_system: str
    event_type: str
    severity: str
    raw_event: dict | None
    normalized_data: dict | None
    asset_id: uuid.UUID | None
    correlation_id: uuid.UUID | None
    is_anomaly: bool
    risk_score: float | None
    ai_analysis: str | None
    occurred_at: datetime
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SiemEventListResponse(BaseModel):
    items: list[SiemEventOut]
    total: int
    offset: int
    limit: int
    model_config = ConfigDict(from_attributes=True)


class SiemSummaryResponse(BaseModel):
    total_events: int
    anomalies: int
    by_event_type: dict[str, int]
    by_severity: dict[str, int]
    recent_anomalies: list[SiemEventOut]
    model_config = ConfigDict(from_attributes=True)
