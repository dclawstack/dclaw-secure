"""Repositories for Incident and IncidentAction models."""

import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident, IncidentAction, IncidentStatus, IncidentType
from app.repositories.base_repo import BaseRepository


class IncidentRepository(BaseRepository[Incident]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Incident)

    async def list_by_filters(
        self,
        status: IncidentStatus | None = None,
        incident_type: IncidentType | None = None,
        severity: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Incident], int]:
        stmt = select(Incident).order_by(Incident.created_at.desc())
        count_stmt = select(func.count()).select_from(Incident)

        if status is not None:
            stmt = stmt.where(Incident.status == status)
            count_stmt = count_stmt.where(Incident.status == status)
        if incident_type is not None:
            stmt = stmt.where(Incident.incident_type == incident_type)
            count_stmt = count_stmt.where(Incident.incident_type == incident_type)
        if severity is not None:
            stmt = stmt.where(Incident.severity == severity)
            count_stmt = count_stmt.where(Incident.severity == severity)

        result = await self.db.execute(stmt.limit(limit).offset(offset))
        items = list(result.scalars().all())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        return items, total


class IncidentActionRepository(BaseRepository[IncidentAction]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, IncidentAction)

    async def list_for_incident(
        self, incident_id: uuid.UUID, limit: int = 100, offset: int = 0
    ) -> list[IncidentAction]:
        result = await self.db.execute(
            select(IncidentAction)
            .where(IncidentAction.incident_id == incident_id)
            .order_by(IncidentAction.performed_at.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
