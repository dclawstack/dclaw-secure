import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.identity import IdentityProfile, BehaviorEvent
from app.repositories.base_repo import BaseRepository


class IdentityRepository(BaseRepository[IdentityProfile]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, IdentityProfile)

    async def get_by_email(self, email: str) -> IdentityProfile | None:
        result = await self.db.execute(
            select(IdentityProfile).where(IdentityProfile.email == email)
        )
        return result.scalar_one_or_none()

    async def list_by_filters(
        self,
        department: str | None = None,
        role: str | None = None,
        min_risk_score: float | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[IdentityProfile], int]:
        stmt = select(IdentityProfile).order_by(IdentityProfile.risk_score.desc())
        count_stmt = select(func.count()).select_from(IdentityProfile)

        if department:
            stmt = stmt.where(IdentityProfile.department == department)
            count_stmt = count_stmt.where(IdentityProfile.department == department)
        if role:
            stmt = stmt.where(IdentityProfile.role == role)
            count_stmt = count_stmt.where(IdentityProfile.role == role)
        if min_risk_score is not None:
            stmt = stmt.where(IdentityProfile.risk_score >= min_risk_score)
            count_stmt = count_stmt.where(IdentityProfile.risk_score >= min_risk_score)

        result = await self.db.execute(stmt.limit(limit).offset(offset))
        items = list(result.scalars().all())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        return items, total

    async def get_risky(self, threshold: float = 50.0, limit: int = 10) -> list[IdentityProfile]:
        result = await self.db.execute(
            select(IdentityProfile)
            .where(IdentityProfile.risk_score >= threshold)
            .order_by(IdentityProfile.risk_score.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


class BehaviorEventRepository(BaseRepository[BehaviorEvent]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, BehaviorEvent)

    async def list_for_identity(self, identity_id: uuid.UUID, limit: int = 50) -> list[BehaviorEvent]:
        result = await self.db.execute(
            select(BehaviorEvent)
            .where(BehaviorEvent.identity_id == identity_id)
            .order_by(BehaviorEvent.occurred_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_recent_for_identity(self, identity_id: uuid.UUID, limit: int = 20) -> list[BehaviorEvent]:
        return await self.list_for_identity(identity_id, limit)
