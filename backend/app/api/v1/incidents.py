"""Incident Response API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.incident import Incident, IncidentAction, IncidentStatus, IncidentType
from app.repositories.incident_repo import IncidentActionRepository, IncidentRepository
from app.schemas.incident import (
    IncidentActionCreate,
    IncidentActionOut,
    IncidentCreate,
    IncidentListResponse,
    IncidentOut,
    IncidentUpdate,
)
from app.services.incident_service import generate_playbook

router = APIRouter()


@router.get("", response_model=IncidentListResponse)
async def list_incidents(
    status: str | None = Query(None),
    incident_type: str | None = Query(None),
    severity: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = IncidentRepository(db)
    status_enum = IncidentStatus(status) if status else None
    type_enum = IncidentType(incident_type) if incident_type else None
    items, total = await repo.list_by_filters(
        status=status_enum,
        incident_type=type_enum,
        severity=severity,
        limit=limit,
        offset=offset,
    )
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.post("", response_model=IncidentOut, status_code=201)
async def create_incident(payload: IncidentCreate, db: AsyncSession = Depends(get_db)):
    repo = IncidentRepository(db)
    incident = Incident(**payload.model_dump())
    return await repo.create(incident)


@router.get("/{incident_id}", response_model=IncidentOut)
async def get_incident(incident_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = IncidentRepository(db)
    incident = await repo.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.put("/{incident_id}", response_model=IncidentOut)
async def update_incident(
    incident_id: uuid.UUID,
    payload: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = IncidentRepository(db)
    incident = await repo.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(incident, field, value)
    await db.commit()
    await db.refresh(incident)
    return incident


@router.post("/{incident_id}/actions", response_model=IncidentActionOut, status_code=201)
async def add_action(
    incident_id: uuid.UUID,
    payload: IncidentActionCreate,
    db: AsyncSession = Depends(get_db),
):
    inc_repo = IncidentRepository(db)
    incident = await inc_repo.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    action = IncidentAction(incident_id=incident_id, **payload.model_dump())
    action_repo = IncidentActionRepository(db)
    return await action_repo.create(action)


@router.get("/{incident_id}/actions", response_model=list[IncidentActionOut])
async def list_actions(incident_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    inc_repo = IncidentRepository(db)
    incident = await inc_repo.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    action_repo = IncidentActionRepository(db)
    actions = await action_repo.list_for_incident(incident_id)
    return actions


@router.post("/{incident_id}/generate-playbook", response_model=IncidentOut)
async def generate_incident_playbook(
    incident_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    repo = IncidentRepository(db)
    incident = await repo.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    playbook = await generate_playbook(incident)
    incident.ai_playbook = playbook
    await db.commit()
    await db.refresh(incident)
    return incident
