"""Asset schemas for API request/response validation."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

AssetTypeLiteral = Literal[
    "server", "container", "database", "s3_bucket", "api",
    "domain", "repository", "workstation",
]

EnvironmentLiteral = Literal["production", "staging", "development"]

AssetStatusLiteral = Literal["active", "inactive", "decommissioned"]

CloudProviderLiteral = Literal["aws", "azure", "gcp", "on_premise"]


class AssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    asset_type: AssetTypeLiteral
    environment: EnvironmentLiteral = "production"
    status: AssetStatusLiteral = "active"
    cloud_provider: CloudProviderLiteral | None = None
    region: str | None = Field(None, max_length=100)
    owner_email: str | None = Field(None, max_length=255)
    risk_score: int = Field(default=0, ge=0, le=100)
    description: str | None = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    asset_type: AssetTypeLiteral | None = None
    environment: EnvironmentLiteral | None = None
    status: AssetStatusLiteral | None = None
    cloud_provider: CloudProviderLiteral | None = None
    region: str | None = Field(None, max_length=100)
    owner_email: str | None = Field(None, max_length=255)
    risk_score: int | None = Field(None, ge=0, le=100)
    description: str | None = None


class AssetOut(AssetBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssetListResponse(BaseModel):
    items: list[AssetOut]
    total: int
    offset: int
    limit: int

    model_config = ConfigDict(from_attributes=True)
