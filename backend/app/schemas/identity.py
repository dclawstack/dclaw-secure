import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

BehaviorEventTypeLiteral = Literal[
    "login", "logout", "file_access", "api_call",
    "privilege_escalation", "data_export", "failed_auth"
]


class BehaviorEventCreate(BaseModel):
    event_type: BehaviorEventTypeLiteral
    ip_address: str | None = Field(None, max_length=45)
    user_agent: str | None = Field(None, max_length=512)
    location: str | None = Field(None, max_length=255)
    event_metadata: dict | None = None


class BehaviorEventOut(BaseModel):
    id: uuid.UUID
    identity_id: uuid.UUID
    event_type: str
    ip_address: str | None
    user_agent: str | None
    location: str | None
    event_metadata: dict | None
    risk_contribution: float
    is_flagged: bool
    occurred_at: datetime
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BehaviorListResponse(BaseModel):
    items: list[BehaviorEventOut]
    total: int
    model_config = ConfigDict(from_attributes=True)


class IdentityProfileCreate(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    display_name: str | None = Field(None, max_length=255)
    department: str | None = Field(None, max_length=100)
    role: str | None = Field(None, max_length=100)


class IdentityProfileUpdate(BaseModel):
    display_name: str | None = Field(None, max_length=255)
    department: str | None = Field(None, max_length=100)
    role: str | None = Field(None, max_length=100)
    is_active: bool | None = None


class IdentityProfileOut(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str | None
    department: str | None
    role: str | None
    risk_score: float
    is_active: bool
    last_seen: datetime | None
    ai_analysis: str | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class IdentityListResponse(BaseModel):
    items: list[IdentityProfileOut]
    total: int
    offset: int
    limit: int
    model_config = ConfigDict(from_attributes=True)
