"""Secret scan repositories."""

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.secret_scan import SecretScanJob, SecretFinding
from app.repositories.base_repo import BaseRepository


class SecretScanRepository(BaseRepository[SecretScanJob]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, SecretScanJob)

    async def list_all(self, limit: int = 20, offset: int = 0) -> tuple[list[SecretScanJob], int]:
        result = await self.db.execute(
            select(SecretScanJob).order_by(SecretScanJob.created_at.desc()).limit(limit).offset(offset)
        )
        items = list(result.scalars().all())
        count_result = await self.db.execute(select(func.count()).select_from(SecretScanJob))
        total = count_result.scalar() or 0
        return items, total


class SecretFindingRepository(BaseRepository[SecretFinding]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, SecretFinding)

    async def list_by_job(
        self,
        job_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[SecretFinding], int]:
        result = await self.db.execute(
            select(SecretFinding)
            .where(SecretFinding.job_id == job_id)
            .order_by(SecretFinding.detected_at.desc())
            .limit(limit)
            .offset(offset)
        )
        items = list(result.scalars().all())
        count_result = await self.db.execute(
            select(func.count()).select_from(SecretFinding).where(SecretFinding.job_id == job_id)
        )
        total = count_result.scalar() or 0
        return items, total
