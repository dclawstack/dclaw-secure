"""Vulnerability repository."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.vulnerability import Vulnerability
from app.repositories.base_repo import BaseRepository


class VulnerabilityRepository(BaseRepository[Vulnerability]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Vulnerability)

    async def list_by_filters(
        self,
        asset_id: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Vulnerability], int]:
        stmt = select(Vulnerability)
        count_stmt = select(func.count()).select_from(Vulnerability)

        if asset_id:
            stmt = stmt.where(Vulnerability.asset_id == asset_id)
            count_stmt = count_stmt.where(Vulnerability.asset_id == asset_id)
        if severity:
            stmt = stmt.where(Vulnerability.severity == severity)
            count_stmt = count_stmt.where(Vulnerability.severity == severity)
        if status:
            stmt = stmt.where(Vulnerability.status == status)
            count_stmt = count_stmt.where(Vulnerability.status == status)

        result = await self.db.execute(stmt.limit(limit).offset(offset))
        items = list(result.scalars().all())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        return items, total
