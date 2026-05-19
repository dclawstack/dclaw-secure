import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.siem_event import SiemEvent
from app.repositories.base_repo import BaseRepository


class SiemEventRepository(BaseRepository[SiemEvent]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, SiemEvent)

    async def list_by_filters(
        self,
        source_system: str | None = None,
        event_type: str | None = None,
        severity: str | None = None,
        is_anomaly: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[SiemEvent], int]:
        stmt = select(SiemEvent).order_by(SiemEvent.occurred_at.desc())
        count_stmt = select(func.count()).select_from(SiemEvent)

        if source_system:
            stmt = stmt.where(SiemEvent.source_system == source_system)
            count_stmt = count_stmt.where(SiemEvent.source_system == source_system)
        if event_type:
            stmt = stmt.where(SiemEvent.event_type == event_type)
            count_stmt = count_stmt.where(SiemEvent.event_type == event_type)
        if severity:
            stmt = stmt.where(SiemEvent.severity == severity)
            count_stmt = count_stmt.where(SiemEvent.severity == severity)
        if is_anomaly is not None:
            stmt = stmt.where(SiemEvent.is_anomaly == is_anomaly)
            count_stmt = count_stmt.where(SiemEvent.is_anomaly == is_anomaly)

        result = await self.db.execute(stmt.limit(limit).offset(offset))
        items = list(result.scalars().all())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        return items, total

    async def get_recent(self, limit: int = 50) -> list[SiemEvent]:
        result = await self.db.execute(
            select(SiemEvent).order_by(SiemEvent.occurred_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_recent_anomalies(self, limit: int = 5) -> list[SiemEvent]:
        result = await self.db.execute(
            select(SiemEvent)
            .where(SiemEvent.is_anomaly == True)
            .order_by(SiemEvent.occurred_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_field(self, field_name: str) -> dict[str, int]:
        field = getattr(SiemEvent, field_name)
        result = await self.db.execute(
            select(field, func.count(SiemEvent.id)).group_by(field)
        )
        return {str(row[0]): row[1] for row in result.all()}
