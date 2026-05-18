"""Policy API router."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.policy import Policy
from app.repositories.policy_repo import PolicyRepository
from app.schemas.policy import (
    PolicyCreate, PolicyUpdate, PolicyOut, PolicyListResponse,
    PolicyAcknowledgmentCreate, PolicyAcknowledgmentOut,
)

router = APIRouter(tags=["policies"])


@router.get("", response_model=PolicyListResponse)
async def list_policies(
    status: str | None = Query(None),
    category: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = PolicyRepository(db)
    items, total = await repo.list_by_filters(status=status, category=category, limit=limit, offset=offset)
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.post("", response_model=PolicyOut, status_code=201)
async def create_policy(payload: PolicyCreate, db: AsyncSession = Depends(get_db)):
    repo = PolicyRepository(db)
    policy = Policy(**payload.model_dump())
    return await repo.create(policy)


@router.get("/{policy_id}", response_model=PolicyOut)
async def get_policy(policy_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = PolicyRepository(db)
    policy = await repo.get_by_id(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.put("/{policy_id}", response_model=PolicyOut)
async def update_policy(
    policy_id: uuid.UUID,
    payload: PolicyUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = PolicyRepository(db)
    policy = await repo.get_by_id(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(policy, field, value)
    await db.commit()
    await db.refresh(policy)
    return policy


@router.delete("/{policy_id}", status_code=204)
async def delete_policy(policy_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = PolicyRepository(db)
    policy = await repo.get_by_id(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    await repo.delete(policy)
    return None


@router.post("/{policy_id}/acknowledge", response_model=PolicyAcknowledgmentOut, status_code=201)
async def acknowledge_policy(
    policy_id: uuid.UUID,
    payload: PolicyAcknowledgmentCreate,
    db: AsyncSession = Depends(get_db),
):
    repo = PolicyRepository(db)
    policy = await repo.get_by_id(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    if policy.status != "published":
        raise HTTPException(status_code=400, detail="Only published policies can be acknowledged")
    ack = await repo.acknowledge(
        policy_id=policy_id,
        employee_email=payload.employee_email,
        employee_name=payload.employee_name,
        ip_address=payload.ip_address,
    )
    return ack
