"""Asset API router."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.asset import Asset
from app.repositories.asset_repo import AssetRepository
from app.schemas.asset import AssetCreate, AssetUpdate, AssetOut, AssetListResponse

router = APIRouter(tags=["assets"])


@router.get("", response_model=AssetListResponse)
async def list_assets(
    asset_type: str | None = Query(None),
    environment: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = AssetRepository(db)
    items, total = await repo.list_by_filters(
        asset_type=asset_type,
        environment=environment,
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


@router.post("", response_model=AssetOut, status_code=201)
async def create_asset(payload: AssetCreate, db: AsyncSession = Depends(get_db)):
    repo = AssetRepository(db)
    asset = Asset(**payload.model_dump())
    return await repo.create(asset)


@router.get("/{asset_id}", response_model=AssetOut)
async def get_asset(asset_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = AssetRepository(db)
    asset = await repo.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.put("/{asset_id}", response_model=AssetOut)
async def update_asset(
    asset_id: uuid.UUID,
    payload: AssetUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = AssetRepository(db)
    asset = await repo.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(asset, field, value)

    await db.commit()
    await db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(asset_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = AssetRepository(db)
    asset = await repo.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    await repo.delete(asset)
    return None
