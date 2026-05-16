"""Security scan repository."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.security_scan import SecurityScan
from app.repositories.base_repo import BaseRepository


class SecurityScanRepository(BaseRepository[SecurityScan]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, SecurityScan)

    async def list_by_filters(
        self,
        target_asset_id: str | None = None,
        scan_type: str | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[SecurityScan], int]:
        stmt = select(SecurityScan)
        count_stmt = select(func.count()).select_from(SecurityScan)

        if target_asset_id:
            stmt = stmt.where(SecurityScan.target_asset_id == target_asset_id)
            count_stmt = count_stmt.where(SecurityScan.target_asset_id == target_asset_id)
        if scan_type:
            stmt = stmt.where(SecurityScan.scan_type == scan_type)
            count_stmt = count_stmt.where(SecurityScan.scan_type == scan_type)
        if status:
            stmt = stmt.where(SecurityScan.status == status)
            count_stmt = count_stmt.where(SecurityScan.status == status)

        result = await self.db.execute(stmt.limit(limit).offset(offset))
        items = list(result.scalars().all())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        return items, total
