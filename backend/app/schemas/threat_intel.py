"""Pydantic schemas for Threat Intelligence."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

FeedTypeLiteral = Literal["ip_blocklist", "domain_blocklist", "hash_list", "cve_feed", "custom"]
IOCTypeLiteral = Literal["ip", "domain", "hash", "url", "email", "cve"]


class ThreatFeedCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    feed_type: FeedTypeLiteral
    source_url: str | None = Field(None, max_length=1024)


class ThreatFeedUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    feed_type: FeedTypeLiteral | None = None
    source_url: str | None = Field(None, max_length=1024)
    is_active: bool | None = None


class ThreatIOCOut(BaseModel):
    id: uuid.UUID
    feed_id: uuid.UUID | None
    ioc_type: str
    value: str
    threat_type: str | None
    confidence_score: float | None
    is_active: bool
    first_seen: datetime
    last_seen: datetime | None
    ioc_metadata: dict | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ThreatFeedOut(BaseModel):
    id: uuid.UUID
    name: str
    feed_type: str
    source_url: str | None
    is_active: bool
    last_synced: datetime | None
    ioc_count: int
    created_at: datetime
    updated_at: datetime
    iocs: list[ThreatIOCOut] = []
    model_config = ConfigDict(from_attributes=True)


class ThreatFeedListResponse(BaseModel):
    items: list[ThreatFeedOut]
    total: int
    offset: int
    limit: int
    model_config = ConfigDict(from_attributes=True)


class ThreatIOCCreate(BaseModel):
    ioc_type: IOCTypeLiteral
    value: str = Field(..., min_length=1, max_length=512)
    threat_type: str | None = Field(None, max_length=100)
    confidence_score: float | None = Field(None, ge=0, le=100)
    feed_id: uuid.UUID | None = None
    ioc_metadata: dict | None = None


class ThreatIOCListResponse(BaseModel):
    items: list[ThreatIOCOut]
    total: int
    offset: int
    limit: int
    model_config = ConfigDict(from_attributes=True)
