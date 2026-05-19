"""Threat Intelligence API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.utils import utc_now
from app.models.threat_intel import IOCType, ThreatFeed, ThreatIOC
from app.repositories.threat_repo import ThreatFeedRepository, ThreatIOCRepository
from app.schemas.threat_intel import (
    ThreatFeedCreate,
    ThreatFeedListResponse,
    ThreatFeedOut,
    ThreatFeedUpdate,
    ThreatIOCCreate,
    ThreatIOCListResponse,
    ThreatIOCOut,
)
from app.services.threat_service import check_asset_against_iocs, mock_sync_feed

router = APIRouter()


# ─── Feed endpoints ──────────────────────────────────────────────────────────

@router.get("/feeds", response_model=ThreatFeedListResponse)
async def list_feeds(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = ThreatFeedRepository(db)
    items, total = await repo.list_all(limit=limit, offset=offset)
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.post("/feeds", response_model=ThreatFeedOut, status_code=201)
async def create_feed(payload: ThreatFeedCreate, db: AsyncSession = Depends(get_db)):
    repo = ThreatFeedRepository(db)
    feed = ThreatFeed(**payload.model_dump())
    return await repo.create(feed)


@router.get("/feeds/{feed_id}", response_model=ThreatFeedOut)
async def get_feed(feed_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = ThreatFeedRepository(db)
    feed = await repo.get_by_id(feed_id)
    if not feed:
        raise HTTPException(status_code=404, detail="Threat feed not found")
    return feed


@router.put("/feeds/{feed_id}", response_model=ThreatFeedOut)
async def update_feed(
    feed_id: uuid.UUID,
    payload: ThreatFeedUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = ThreatFeedRepository(db)
    feed = await repo.get_by_id(feed_id)
    if not feed:
        raise HTTPException(status_code=404, detail="Threat feed not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(feed, field, value)
    await db.commit()
    await db.refresh(feed)
    return feed


@router.post("/feeds/{feed_id}/sync", response_model=ThreatFeedOut)
async def sync_feed(feed_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    feed_repo = ThreatFeedRepository(db)
    feed = await feed_repo.get_by_id(feed_id)
    if not feed:
        raise HTTPException(status_code=404, detail="Threat feed not found")

    ioc_repo = ThreatIOCRepository(db)
    generated = mock_sync_feed(feed)

    new_count = 0
    for ioc_data in generated:
        # Idempotent by value — skip if already exists
        existing = await ioc_repo.get_by_value(ioc_data["value"])
        if existing:
            continue
        ioc = ThreatIOC(feed_id=feed.id, **ioc_data)
        db.add(ioc)
        new_count += 1

    feed.last_synced = utc_now()
    # Update ioc_count to total active IOCs for this feed
    await db.flush()

    # Recount after flush so new IOCs are visible
    from sqlalchemy import select, func
    count_result = await db.execute(
        select(func.count()).select_from(ThreatIOC).where(ThreatIOC.feed_id == feed.id)
    )
    feed.ioc_count = count_result.scalar() or 0

    await db.commit()
    # Re-fetch to get fully refreshed state with relationships
    refreshed = await feed_repo.get_by_id(feed.id)
    return refreshed


# ─── IOC endpoints ────────────────────────────────────────────────────────────

@router.get("/iocs", response_model=ThreatIOCListResponse)
async def list_iocs(
    ioc_type: str | None = Query(None),
    is_active: bool | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = ThreatIOCRepository(db)
    type_enum = IOCType(ioc_type) if ioc_type else None
    items, total = await repo.list_by_filters(
        ioc_type=type_enum,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.post("/iocs", response_model=ThreatIOCOut, status_code=201)
async def create_ioc(payload: ThreatIOCCreate, db: AsyncSession = Depends(get_db)):
    repo = ThreatIOCRepository(db)
    ioc = ThreatIOC(**payload.model_dump())
    return await repo.create(ioc)


@router.get("/iocs/check/{asset_id}", response_model=list[ThreatIOCOut])
async def check_asset_iocs(asset_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    matches = await check_asset_against_iocs(asset_id, db)
    return matches
