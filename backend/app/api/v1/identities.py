import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.utils import utc_now
from app.models.identity import BehaviorEvent, IdentityProfile
from app.repositories.identity_repo import BehaviorEventRepository, IdentityRepository
from app.schemas.identity import (
    BehaviorEventCreate,
    BehaviorEventOut,
    BehaviorListResponse,
    IdentityListResponse,
    IdentityProfileCreate,
    IdentityProfileOut,
    IdentityProfileUpdate,
)
from app.services.identity_service import analyze_identity_risk

router = APIRouter()


@router.get("", response_model=IdentityListResponse)
async def list_identities(
    department: str | None = Query(None),
    role: str | None = Query(None),
    min_risk_score: float | None = Query(None, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = IdentityRepository(db)
    items, total = await repo.list_by_filters(
        department=department, role=role, min_risk_score=min_risk_score, limit=limit, offset=offset
    )
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.post("", response_model=IdentityProfileOut, status_code=201)
async def create_identity(payload: IdentityProfileCreate, db: AsyncSession = Depends(get_db)):
    repo = IdentityRepository(db)
    existing = await repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="Identity with this email already exists")
    identity = IdentityProfile(**payload.model_dump())
    return await repo.create(identity)


@router.get("/risky", response_model=list[IdentityProfileOut])
async def get_risky_identities(
    threshold: float = Query(50.0, ge=0, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = IdentityRepository(db)
    return await repo.get_risky(threshold=threshold)


@router.get("/{identity_id}", response_model=IdentityProfileOut)
async def get_identity(identity_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = IdentityRepository(db)
    identity = await repo.get_by_id(identity_id)
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")
    return identity


@router.put("/{identity_id}", response_model=IdentityProfileOut)
async def update_identity(
    identity_id: uuid.UUID, payload: IdentityProfileUpdate, db: AsyncSession = Depends(get_db)
):
    repo = IdentityRepository(db)
    identity = await repo.get_by_id(identity_id)
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(identity, field, value)
    await db.commit()
    await db.refresh(identity)
    return identity


@router.post("/{identity_id}/events", response_model=BehaviorEventOut, status_code=201)
async def log_behavior(
    identity_id: uuid.UUID, payload: BehaviorEventCreate, db: AsyncSession = Depends(get_db)
):
    id_repo = IdentityRepository(db)
    identity = await id_repo.get_by_id(identity_id)
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")

    event = BehaviorEvent(identity_id=identity_id, **payload.model_dump())
    bev_repo = BehaviorEventRepository(db)
    event = await bev_repo.create(event)

    # Update last_seen and recalculate risk after new behavior
    identity.last_seen = utc_now()
    recent = await bev_repo.get_recent_for_identity(identity_id)
    score, analysis = await analyze_identity_risk(identity, recent)
    identity.risk_score = score
    identity.ai_analysis = analysis
    await db.commit()

    return event


@router.get("/{identity_id}/events", response_model=BehaviorListResponse)
async def list_behaviors(identity_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    id_repo = IdentityRepository(db)
    identity = await id_repo.get_by_id(identity_id)
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")
    bev_repo = BehaviorEventRepository(db)
    events = await bev_repo.list_for_identity(identity_id)
    return {"items": events, "total": len(events)}


@router.post("/{identity_id}/analyze", response_model=IdentityProfileOut)
async def analyze_identity(identity_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    id_repo = IdentityRepository(db)
    identity = await id_repo.get_by_id(identity_id)
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")

    bev_repo = BehaviorEventRepository(db)
    recent = await bev_repo.get_recent_for_identity(identity_id)
    score, analysis = await analyze_identity_risk(identity, recent)
    identity.risk_score = score
    identity.ai_analysis = analysis
    identity.last_seen = utc_now()
    await db.commit()
    await db.refresh(identity)
    return identity
