"""Vulnerability API router."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.vulnerability import Vulnerability
from app.repositories.vuln_repo import VulnerabilityRepository
from app.repositories.asset_repo import AssetRepository
from app.schemas.vulnerability import (
    VulnerabilityCreate,
    VulnerabilityUpdate,
    VulnerabilityOut,
    VulnerabilityListResponse,
)

router = APIRouter(tags=["vulnerabilities"])


@router.get("", response_model=VulnerabilityListResponse)
async def list_vulnerabilities(
    asset_id: uuid.UUID | None = Query(None),
    severity: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = VulnerabilityRepository(db)
    items, total = await repo.list_by_filters(
        asset_id=str(asset_id) if asset_id else None,
        severity=severity,
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


@router.post("", response_model=VulnerabilityOut, status_code=201)
async def create_vulnerability(
    payload: VulnerabilityCreate, db: AsyncSession = Depends(get_db)
):
    # Validate asset exists
    asset_repo = AssetRepository(db)
    asset = await asset_repo.get_by_id(payload.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    repo = VulnerabilityRepository(db)
    vuln = Vulnerability(**payload.model_dump())
    return await repo.create(vuln)


@router.get("/{vuln_id}", response_model=VulnerabilityOut)
async def get_vulnerability(vuln_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = VulnerabilityRepository(db)
    vuln = await repo.get_by_id(vuln_id)
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return vuln


@router.put("/{vuln_id}", response_model=VulnerabilityOut)
async def update_vulnerability(
    vuln_id: uuid.UUID,
    payload: VulnerabilityUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = VulnerabilityRepository(db)
    vuln = await repo.get_by_id(vuln_id)
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vuln, field, value)

    await db.commit()
    await db.refresh(vuln)
    return vuln


@router.delete("/{vuln_id}", status_code=204)
async def delete_vulnerability(vuln_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = VulnerabilityRepository(db)
    vuln = await repo.get_by_id(vuln_id)
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    await repo.delete(vuln)
    return None
