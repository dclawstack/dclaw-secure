"""Compliance schemas."""

import uuid
from datetime import datetime, date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ControlStatusLiteral = Literal[
    "not_implemented", "partially_implemented", "implemented", "not_applicable"
]


class FrameworkBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9\-]+$")
    version: str | None = Field(None, max_length=50)
    description: str | None = None
    is_active: bool = True


class FrameworkCreate(FrameworkBase):
    pass


class FrameworkUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    version: str | None = Field(None, max_length=50)
    description: str | None = None
    is_active: bool | None = None


class ControlBase(BaseModel):
    control_id: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(None, max_length=255)
    status: ControlStatusLiteral = "not_implemented"
    evidence_url: str | None = Field(None, max_length=1024)
    notes: str | None = None
    assigned_to: str | None = Field(None, max_length=255)
    due_date: date | None = None


class ControlCreate(ControlBase):
    framework_id: uuid.UUID


class ControlUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = None
    status: ControlStatusLiteral | None = None
    evidence_url: str | None = None
    notes: str | None = None
    assigned_to: str | None = None
    due_date: date | None = None


class ControlOut(ControlBase):
    id: uuid.UUID
    framework_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FrameworkOut(FrameworkBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    controls: list[ControlOut] = []

    model_config = ConfigDict(from_attributes=True)


class FrameworkListResponse(BaseModel):
    items: list[FrameworkOut]
    total: int
    offset: int
    limit: int

    model_config = ConfigDict(from_attributes=True)


class ControlListResponse(BaseModel):
    items: list[ControlOut]
    total: int
    offset: int
    limit: int

    model_config = ConfigDict(from_attributes=True)
