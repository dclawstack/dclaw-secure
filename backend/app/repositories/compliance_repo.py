"""Compliance repository."""

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.compliance import ComplianceFramework, ComplianceControl, ComplianceEvidence, ControlStatus
from app.repositories.base_repo import BaseRepository


class FrameworkRepository(BaseRepository[ComplianceFramework]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ComplianceFramework)

    async def get_by_slug(self, slug: str) -> ComplianceFramework | None:
        result = await self.db.execute(
            select(ComplianceFramework).where(ComplianceFramework.slug == slug)
        )
        return result.scalar_one_or_none()

    async def list_active(self, limit: int = 20, offset: int = 0) -> tuple[list[ComplianceFramework], int]:
        stmt = select(ComplianceFramework).where(ComplianceFramework.is_active == True)
        count_stmt = select(func.count()).select_from(ComplianceFramework).where(ComplianceFramework.is_active == True)
        result = await self.db.execute(stmt.order_by(ComplianceFramework.name).limit(limit).offset(offset))
        items = list(result.scalars().all())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        return items, total

    async def get_posture(self, framework_id: uuid.UUID) -> dict:
        result = await self.db.execute(
            select(ComplianceControl.status, func.count())
            .where(ComplianceControl.framework_id == framework_id)
            .group_by(ComplianceControl.status)
        )
        rows = result.all()
        counts = {row[0]: row[1] for row in rows}
        total = sum(counts.values())
        implemented = counts.get(ControlStatus.IMPLEMENTED, 0)
        partial = counts.get(ControlStatus.PARTIALLY_IMPLEMENTED, 0)
        not_applicable = counts.get(ControlStatus.NOT_APPLICABLE, 0)
        applicable = total - not_applicable
        pct = round((implemented / applicable * 100) if applicable > 0 else 0, 1)
        return {
            "total": total,
            "implemented": implemented,
            "partial": partial,
            "not_applicable": not_applicable,
            "compliance_pct": pct,
        }


class ControlRepository(BaseRepository[ComplianceControl]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ComplianceControl)

    async def list_by_framework(
        self,
        framework_id: uuid.UUID,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[ComplianceControl], int]:
        stmt = select(ComplianceControl).where(ComplianceControl.framework_id == framework_id)
        count_stmt = select(func.count()).select_from(ComplianceControl).where(ComplianceControl.framework_id == framework_id)

        if status:
            stmt = stmt.where(ComplianceControl.status == status)
            count_stmt = count_stmt.where(ComplianceControl.status == status)

        result = await self.db.execute(stmt.order_by(ComplianceControl.control_id).limit(limit).offset(offset))
        items = list(result.scalars().all())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        return items, total


class EvidenceRepository(BaseRepository[ComplianceEvidence]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ComplianceEvidence)

    async def list_by_control(self, control_id: uuid.UUID) -> list[ComplianceEvidence]:
        result = await self.db.execute(
            select(ComplianceEvidence)
            .where(ComplianceEvidence.control_id == control_id)
            .order_by(ComplianceEvidence.collected_at)
        )
        return list(result.scalars().all())
