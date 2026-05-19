"""Secret scanning router."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.secret_scan import SecretScanJob, SecretFinding
from app.repositories.secret_scan_repo import SecretScanRepository, SecretFindingRepository
from app.schemas.secret_scan import (
    SecretScanCreate, SecretScanOut, SecretFindingOut, SecretFindingUpdate, SecretScanListResponse,
)
from app.services.secret_scanner import run_scan_job
from app.core.utils import utc_now

router = APIRouter()
findings_router = APIRouter()


# ── Secret Scan Jobs ──────────────────────────────────────────────────────────

@router.post("/secret-scans", response_model=SecretScanOut, status_code=201)
async def create_scan(
    payload: SecretScanCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a scan job and immediately run the scan on the provided content."""
    job = SecretScanJob(
        id=uuid.uuid4(),
        scan_target=payload.scan_target,
        scan_type=payload.scan_type,
        status="running",
        files_scanned=0,
        secrets_found=0,
        started_at=utc_now(),
        created_at=utc_now(),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    job = await run_scan_job(job, payload.content, db)
    return job


@router.get("/secret-scans", response_model=SecretScanListResponse)
async def list_scans(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = SecretScanRepository(db)
    items, total = await repo.list_all(limit=limit, offset=offset)
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.get("/secret-scans/{job_id}", response_model=SecretScanOut)
async def get_scan(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = SecretScanRepository(db)
    job = await repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Scan job not found")
    return job


@router.get("/secret-scans/{job_id}/findings", response_model=list[SecretFindingOut])
async def list_findings(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    scan_repo = SecretScanRepository(db)
    if not await scan_repo.get_by_id(job_id):
        raise HTTPException(status_code=404, detail="Scan job not found")
    finding_repo = SecretFindingRepository(db)
    items, _ = await finding_repo.list_by_job(job_id)
    return items


@router.patch("/secret-findings/{finding_id}", response_model=SecretFindingOut)
async def update_finding(
    finding_id: uuid.UUID,
    payload: SecretFindingUpdate,
    db: AsyncSession = Depends(get_db),
):
    finding_repo = SecretFindingRepository(db)
    finding = await finding_repo.get_by_id(finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(finding, field, value)
    await db.commit()
    await db.refresh(finding)
    return finding
