"""Compliance scan schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ComplianceScanOut(BaseModel):
    id: uuid.UUID
    framework_id: uuid.UUID
    triggered_by: str | None
    scan_type: str
    status: str
    controls_checked: int
    controls_passed: int
    controls_failed: int
    gap_analysis: str | None
    recommendations: dict[str, Any] | None
    started_at: datetime
    completed_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComplianceScanListResponse(BaseModel):
    items: list[ComplianceScanOut]
    total: int
    offset: int
    limit: int

    model_config = ConfigDict(from_attributes=True)
