"""Asset repository."""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.models.asset import Asset
from app.repositories.base_repo import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Asset)

    async def list_by_filters(
        self,
        asset_type: str | None = None,
        environment: str | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Asset], int]:
        stmt = select(Asset)
        count_stmt = select(func.count()).select_from(Asset)

        if asset_type:
            stmt = stmt.where(Asset.asset_type == asset_type)
            count_stmt = count_stmt.where(Asset.asset_type == asset_type)
        if environment:
            stmt = stmt.where(Asset.environment == environment)
            count_stmt = count_stmt.where(Asset.environment == environment)
        if status:
            stmt = stmt.where(Asset.status == status)
            count_stmt = count_stmt.where(Asset.status == status)

        result = await self.db.execute(stmt.limit(limit).offset(offset))
        items = list(result.scalars().all())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        return items, total
