"""Security scan schemas."""

import uuid
from datetime import datetime
from typing import Literal, Any

from pydantic import BaseModel, ConfigDict, Field

ScanTypeLiteral = Literal["vulnerability", "container", "api", "web", "compliance"]
ScanStatusLiteral = Literal["pending", "running", "completed", "failed"]


class SecurityScanBase(BaseModel):
    scan_type: ScanTypeLiteral
    status: ScanStatusLiteral = "pending"
    findings_count: int = Field(default=0, ge=0)
    risk_score: int | None = Field(None, ge=0, le=100)
    scan_metadata: dict[str, Any] | None = None


class SecurityScanCreate(SecurityScanBase):
    target_asset_id: uuid.UUID


class SecurityScanUpdate(BaseModel):
    status: ScanStatusLiteral | None = None
    findings_count: int | None = Field(None, ge=0)
    risk_score: int | None = Field(None, ge=0, le=100)
    completed_at: datetime | None = None
    scan_metadata: dict[str, Any] | None = None


class SecurityScanOut(SecurityScanBase):
    id: uuid.UUID
    target_asset_id: uuid.UUID
    started_at: datetime
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SecurityScanListResponse(BaseModel):
    items: list[SecurityScanOut]
    total: int
    offset: int
    limit: int

    model_config = ConfigDict(from_attributes=True)
