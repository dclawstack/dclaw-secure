"""Secret scan schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SecretScanCreate(BaseModel):
    scan_target: str
    scan_type: str = "manual_input"
    content: str  # The text to scan


class SecretFindingOut(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    file_path: str | None
    line_number: int | None
    secret_type: str
    severity: str
    masked_value: str
    is_revoked: bool
    is_false_positive: bool
    detected_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SecretFindingUpdate(BaseModel):
    is_revoked: bool | None = None
    is_false_positive: bool | None = None


class SecretScanOut(BaseModel):
    id: uuid.UUID
    scan_target: str
    scan_type: str
    status: str
    files_scanned: int
    secrets_found: int
    started_at: datetime
    completed_at: datetime | None
    created_at: datetime
    findings: list[SecretFindingOut] = []

    model_config = ConfigDict(from_attributes=True)


class SecretScanListResponse(BaseModel):
    items: list[SecretScanOut]
    total: int
    offset: int
    limit: int

    model_config = ConfigDict(from_attributes=True)
