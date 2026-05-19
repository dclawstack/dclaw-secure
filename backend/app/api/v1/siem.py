import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.utils import utc_now
from app.models.siem_event import SiemEvent
from app.repositories.siem_repo import SiemEventRepository
from app.schemas.siem_event import (
    SiemEventCreate,
    SiemEventListResponse,
    SiemEventOut,
    SiemSummaryResponse,
)
from app.services.siem_service import correlate_event

router = APIRouter()


@router.get("/events", response_model=SiemEventListResponse)
async def list_events(
    source_system: str | None = Query(None),
    event_type: str | None = Query(None),
    severity: str | None = Query(None),
    is_anomaly: bool | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = SiemEventRepository(db)
    items, total = await repo.list_by_filters(
        source_system=source_system,
        event_type=event_type,
        severity=severity,
        is_anomaly=is_anomaly,
        limit=limit,
        offset=offset,
    )
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.post("/events", response_model=SiemEventOut, status_code=201)
async def create_event(
    payload: SiemEventCreate,
    analyze: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    repo = SiemEventRepository(db)
    data = payload.model_dump()
    if data.get("occurred_at") is None:
        data["occurred_at"] = utc_now()

    event = SiemEvent(**data)
    event = await repo.create(event)

    if analyze:
        recent = await repo.get_recent(50)
        is_anomaly, risk_score, analysis = await correlate_event(event, recent)
        event.is_anomaly = is_anomaly
        event.risk_score = risk_score
        event.ai_analysis = analysis
        await db.commit()
        await db.refresh(event)

    return event


@router.get("/events/summary", response_model=SiemSummaryResponse)
async def get_summary(db: AsyncSession = Depends(get_db)):
    repo = SiemEventRepository(db)
    total = await repo.count()
    by_type = await repo.count_by_field("event_type")
    by_severity = await repo.count_by_field("severity")
    anomalies_list = await repo.get_recent_anomalies(5)
    anomaly_count_result = await repo.list_by_filters(is_anomaly=True, limit=1)
    return {
        "total_events": total,
        "anomalies": anomaly_count_result[1],
        "by_event_type": by_type,
        "by_severity": by_severity,
        "recent_anomalies": anomalies_list,
    }


@router.get("/events/{event_id}", response_model=SiemEventOut)
async def get_event(event_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = SiemEventRepository(db)
    event = await repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/events/{event_id}/analyze", response_model=SiemEventOut)
async def analyze_event(event_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = SiemEventRepository(db)
    event = await repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    recent = await repo.get_recent(50)
    is_anomaly, risk_score, analysis = await correlate_event(event, recent)
    event.is_anomaly = is_anomaly
    event.risk_score = risk_score
    event.ai_analysis = analysis
    await db.commit()
    await db.refresh(event)
    return event
