"""Compliance framework, control and evidence router."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.compliance import ComplianceFramework, ComplianceControl, ComplianceEvidence
from app.models.compliance_scan import ComplianceScan
from app.repositories.compliance_repo import FrameworkRepository, ControlRepository, EvidenceRepository
from app.schemas.compliance import (
    FrameworkCreate, FrameworkUpdate, FrameworkOut, FrameworkListResponse,
    ControlCreate, ControlUpdate, ControlOut, ControlListResponse,
    EvidenceCreate, EvidenceOut, EvidenceListResponse,
)
from app.schemas.compliance_scan import ComplianceScanOut, ComplianceScanListResponse
from app.services.compliance_scanner import scan_framework, ScanTrigger

router = APIRouter(tags=["compliance"])


# ── Frameworks ────────────────────────────────────────────────────────────────

@router.get("/frameworks", response_model=FrameworkListResponse)
async def list_frameworks(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = FrameworkRepository(db)
    items, total = await repo.list_all(limit=limit, offset=offset)
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.post("/frameworks", response_model=FrameworkOut, status_code=201)
async def create_framework(payload: FrameworkCreate, db: AsyncSession = Depends(get_db)):
    repo = FrameworkRepository(db)
    existing = await repo.get_by_slug(payload.slug)
    if existing:
        raise HTTPException(status_code=409, detail=f"Framework with slug '{payload.slug}' already exists")
    framework = ComplianceFramework(**payload.model_dump())
    return await repo.create(framework)


@router.get("/frameworks/{framework_id}", response_model=FrameworkOut)
async def get_framework(framework_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = FrameworkRepository(db)
    fw = await repo.get_by_id(framework_id)
    if not fw:
        raise HTTPException(status_code=404, detail="Framework not found")
    return fw


@router.put("/frameworks/{framework_id}", response_model=FrameworkOut)
async def update_framework(
    framework_id: uuid.UUID,
    payload: FrameworkUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = FrameworkRepository(db)
    fw = await repo.get_by_id(framework_id)
    if not fw:
        raise HTTPException(status_code=404, detail="Framework not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(fw, field, value)
    await db.commit()
    await db.refresh(fw)
    return fw


@router.delete("/frameworks/{framework_id}", status_code=204)
async def delete_framework(framework_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = FrameworkRepository(db)
    fw = await repo.get_by_id(framework_id)
    if not fw:
        raise HTTPException(status_code=404, detail="Framework not found")
    await repo.delete(fw)
    return None


@router.get("/frameworks/{framework_id}/posture")
async def get_framework_posture(framework_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = FrameworkRepository(db)
    fw = await repo.get_by_id(framework_id)
    if not fw:
        raise HTTPException(status_code=404, detail="Framework not found")
    posture = await repo.get_posture(framework_id)
    return {"framework_id": framework_id, "framework_name": fw.name, **posture}


# ── Controls ──────────────────────────────────────────────────────────────────

@router.get("/frameworks/{framework_id}/controls", response_model=ControlListResponse)
async def list_controls(
    framework_id: uuid.UUID,
    status: str | None = Query(None),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    fw_repo = FrameworkRepository(db)
    if not await fw_repo.get_by_id(framework_id):
        raise HTTPException(status_code=404, detail="Framework not found")
    ctrl_repo = ControlRepository(db)
    items, total = await ctrl_repo.list_by_framework(framework_id=framework_id, status=status, limit=limit, offset=offset)
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.post("/controls", response_model=ControlOut, status_code=201)
async def create_control(payload: ControlCreate, db: AsyncSession = Depends(get_db)):
    fw_repo = FrameworkRepository(db)
    if not await fw_repo.get_by_id(payload.framework_id):
        raise HTTPException(status_code=404, detail="Framework not found")
    ctrl_repo = ControlRepository(db)
    control = ComplianceControl(**payload.model_dump())
    return await ctrl_repo.create(control)


@router.get("/controls/{control_id}", response_model=ControlOut)
async def get_control(control_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = ControlRepository(db)
    ctrl = await repo.get_by_id(control_id)
    if not ctrl:
        raise HTTPException(status_code=404, detail="Control not found")
    return ctrl


@router.put("/controls/{control_id}", response_model=ControlOut)
async def update_control(
    control_id: uuid.UUID,
    payload: ControlUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = ControlRepository(db)
    ctrl = await repo.get_by_id(control_id)
    if not ctrl:
        raise HTTPException(status_code=404, detail="Control not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ctrl, field, value)
    await db.commit()
    await db.refresh(ctrl)
    return ctrl


@router.delete("/controls/{control_id}", status_code=204)
async def delete_control(control_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = ControlRepository(db)
    ctrl = await repo.get_by_id(control_id)
    if not ctrl:
        raise HTTPException(status_code=404, detail="Control not found")
    await repo.delete(ctrl)
    return None


# ── Evidence ──────────────────────────────────────────────────────────────────

@router.get("/controls/{control_id}/evidence", response_model=EvidenceListResponse)
async def list_evidence(control_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    ctrl_repo = ControlRepository(db)
    if not await ctrl_repo.get_by_id(control_id):
        raise HTTPException(status_code=404, detail="Control not found")
    ev_repo = EvidenceRepository(db)
    items = await ev_repo.list_by_control(control_id)
    return {"items": items, "total": len(items)}


@router.post("/controls/{control_id}/evidence", response_model=EvidenceOut, status_code=201)
async def add_evidence(
    control_id: uuid.UUID,
    payload: EvidenceCreate,
    db: AsyncSession = Depends(get_db),
):
    ctrl_repo = ControlRepository(db)
    if not await ctrl_repo.get_by_id(control_id):
        raise HTTPException(status_code=404, detail="Control not found")
    ev_repo = EvidenceRepository(db)
    evidence = ComplianceEvidence(control_id=control_id, **payload.model_dump())
    return await ev_repo.create(evidence)


@router.delete("/evidence/{evidence_id}", status_code=204)
async def delete_evidence(evidence_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    ev_repo = EvidenceRepository(db)
    ev = await ev_repo.get_by_id(evidence_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    await ev_repo.delete(ev)
    return None


# ── Compliance Scans ──────────────────────────────────────────────────────────

@router.post("/frameworks/{framework_id}/scan", response_model=ComplianceScanOut, status_code=201)
async def trigger_scan(
    framework_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    fw_repo = FrameworkRepository(db)
    fw = await fw_repo.get_by_id(framework_id)
    if not fw:
        raise HTTPException(status_code=404, detail="Framework not found")
    try:
        scan = await scan_framework(
            framework_id=framework_id,
            db=db,
            triggered_by="api",
            scan_type=ScanTrigger.manual,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return scan


@router.get("/frameworks/{framework_id}/scans", response_model=ComplianceScanListResponse)
async def list_scans(
    framework_id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    fw_repo = FrameworkRepository(db)
    fw = await fw_repo.get_by_id(framework_id)
    if not fw:
        raise HTTPException(status_code=404, detail="Framework not found")

    result = await db.execute(
        select(ComplianceScan)
        .where(ComplianceScan.framework_id == framework_id)
        .order_by(ComplianceScan.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    items = list(result.scalars().all())

    count_result = await db.execute(
        select(func.count()).select_from(ComplianceScan)
        .where(ComplianceScan.framework_id == framework_id)
    )
    total = count_result.scalar() or 0
    return {"items": items, "total": total, "offset": offset, "limit": limit}
