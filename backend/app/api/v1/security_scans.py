"""Security scan API router."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.security_scan import SecurityScan
from app.repositories.scan_repo import SecurityScanRepository
from app.repositories.asset_repo import AssetRepository
from app.schemas.security_scan import (
    SecurityScanCreate,
    SecurityScanUpdate,
    SecurityScanOut,
    SecurityScanListResponse,
)

router = APIRouter(tags=["security-scans"])


@router.get("", response_model=SecurityScanListResponse)
async def list_scans(
    target_asset_id: uuid.UUID | None = Query(None),
    scan_type: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = SecurityScanRepository(db)
    items, total = await repo.list_by_filters(
        target_asset_id=str(target_asset_id) if target_asset_id else None,
        scan_type=scan_type,
        status=status,
        limit=limit,
        offset=offset,
    )
    return {
        "items": items,
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.post("", response_model=SecurityScanOut, status_code=201)
async def create_scan(payload: SecurityScanCreate, db: AsyncSession = Depends(get_db)):
    asset_repo = AssetRepository(db)
    asset = await asset_repo.get_by_id(payload.target_asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    repo = SecurityScanRepository(db)
    scan = SecurityScan(**payload.model_dump())
    return await repo.create(scan)


@router.get("/{scan_id}", response_model=SecurityScanOut)
async def get_scan(scan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = SecurityScanRepository(db)
    scan = await repo.get_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.put("/{scan_id}", response_model=SecurityScanOut)
async def update_scan(
    scan_id: uuid.UUID,
    payload: SecurityScanUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = SecurityScanRepository(db)
    scan = await repo.get_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(scan, field, value)

    await db.commit()
    await db.refresh(scan)
    return scan


@router.delete("/{scan_id}", status_code=204)
async def delete_scan(scan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = SecurityScanRepository(db)
    scan = await repo.get_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    await repo.delete(scan)
    return None
