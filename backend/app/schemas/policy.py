"""Policy schemas."""

import uuid
from datetime import datetime, date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PolicyStatusLiteral = Literal["draft", "published", "archived"]
PolicyCategoryLiteral = Literal[
    "access_control", "data_protection", "incident_response",
    "acceptable_use", "remote_work",
]


class PolicyBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1, max_length=50)
    status: PolicyStatusLiteral = "draft"
    category: PolicyCategoryLiteral
    requires_acknowledgment: bool = True
    effective_date: date | None = None


class PolicyCreate(PolicyBase):
    pass


class PolicyUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    content: str | None = None
    version: str | None = Field(None, min_length=1, max_length=50)
    status: PolicyStatusLiteral | None = None
    category: PolicyCategoryLiteral | None = None
    requires_acknowledgment: bool | None = None
    effective_date: date | None = None


class PolicyAcknowledgmentOut(BaseModel):
    id: uuid.UUID
    policy_id: uuid.UUID
    employee_email: str
    employee_name: str | None
    acknowledged_at: datetime | None
    ip_address: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PolicyOut(PolicyBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    acknowledgments: list[PolicyAcknowledgmentOut] = []

    model_config = ConfigDict(from_attributes=True)


class PolicyListResponse(BaseModel):
    items: list[PolicyOut]
    total: int
    offset: int
    limit: int

    model_config = ConfigDict(from_attributes=True)


class PolicyAcknowledgmentCreate(BaseModel):
    employee_email: str = Field(..., min_length=1, max_length=255)
    employee_name: str | None = Field(None, max_length=255)
    ip_address: str | None = Field(None, max_length=50)
