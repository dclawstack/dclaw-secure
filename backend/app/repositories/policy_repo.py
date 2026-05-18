"""Policy repository."""

import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.policy import Policy, PolicyAcknowledgment
from app.repositories.base_repo import BaseRepository
from app.core.utils import utc_now


class PolicyRepository(BaseRepository[Policy]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Policy)

    async def list_by_filters(
        self,
        status: str | None = None,
        category: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Policy], int]:
        stmt = select(Policy)
        count_stmt = select(func.count()).select_from(Policy)

        if status:
            stmt = stmt.where(Policy.status == status)
            count_stmt = count_stmt.where(Policy.status == status)
        if category:
            stmt = stmt.where(Policy.category == category)
            count_stmt = count_stmt.where(Policy.category == category)

        result = await self.db.execute(stmt.order_by(Policy.created_at.desc()).limit(limit).offset(offset))
        items = list(result.scalars().all())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        return items, total

    async def acknowledge(
        self,
        policy_id: uuid.UUID,
        employee_email: str,
        employee_name: str | None,
        ip_address: str | None,
    ) -> PolicyAcknowledgment:
        ack = PolicyAcknowledgment(
            policy_id=policy_id,
            employee_email=employee_email,
            employee_name=employee_name,
            acknowledged_at=utc_now(),
            ip_address=ip_address,
        )
        self.db.add(ack)
        await self.db.commit()
        await self.db.refresh(ack)
        return ack

    async def get_acknowledgment_stats(self, policy_id: uuid.UUID) -> dict:
        total_result = await self.db.execute(
            select(func.count()).select_from(PolicyAcknowledgment)
            .where(PolicyAcknowledgment.policy_id == policy_id)
        )
        total = total_result.scalar() or 0

        acked_result = await self.db.execute(
            select(func.count()).select_from(PolicyAcknowledgment)
            .where(
                PolicyAcknowledgment.policy_id == policy_id,
                PolicyAcknowledgment.acknowledged_at.isnot(None),
            )
        )
        acknowledged = acked_result.scalar() or 0
        return {"total": total, "acknowledged": acknowledged}
