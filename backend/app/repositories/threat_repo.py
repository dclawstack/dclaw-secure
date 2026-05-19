"""Repositories for ThreatFeed and ThreatIOC models."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.threat_intel import IOCType, ThreatFeed, ThreatIOC
from app.repositories.base_repo import BaseRepository


class ThreatFeedRepository(BaseRepository[ThreatFeed]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ThreatFeed)


class ThreatIOCRepository(BaseRepository[ThreatIOC]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ThreatIOC)

    async def list_by_filters(
        self,
        ioc_type: IOCType | None = None,
        is_active: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ThreatIOC], int]:
        stmt = select(ThreatIOC).order_by(ThreatIOC.created_at.desc())
        count_stmt = select(func.count()).select_from(ThreatIOC)

        if ioc_type is not None:
            stmt = stmt.where(ThreatIOC.ioc_type == ioc_type)
            count_stmt = count_stmt.where(ThreatIOC.ioc_type == ioc_type)
        if is_active is not None:
            stmt = stmt.where(ThreatIOC.is_active == is_active)
            count_stmt = count_stmt.where(ThreatIOC.is_active == is_active)

        result = await self.db.execute(stmt.limit(limit).offset(offset))
        items = list(result.scalars().all())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        return items, total

    async def get_active(self) -> list[ThreatIOC]:
        result = await self.db.execute(
            select(ThreatIOC)
            .where(ThreatIOC.is_active == True)
            .order_by(ThreatIOC.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_value(self, value: str) -> ThreatIOC | None:
        result = await self.db.execute(
            select(ThreatIOC).where(ThreatIOC.value == value)
        )
        return result.scalar_one_or_none()
