"""AI chat repository."""

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.ai_chat import AIChatSession, AIChatMessage, MessageRole
from app.repositories.base_repo import BaseRepository


class ChatSessionRepository(BaseRepository[AIChatSession]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AIChatSession)

    async def list_sessions(self, limit: int = 20, offset: int = 0) -> tuple[list[AIChatSession], int]:
        stmt = select(AIChatSession).order_by(AIChatSession.updated_at.desc())
        count_stmt = select(func.count()).select_from(AIChatSession)
        result = await self.db.execute(stmt.limit(limit).offset(offset))
        items = list(result.scalars().all())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        return items, total

    async def add_message(
        self,
        session_id: uuid.UUID,
        role: MessageRole,
        content: str,
        sources: dict | None = None,
    ) -> AIChatMessage:
        msg = AIChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            sources=sources,
        )
        self.db.add(msg)
        await self.db.commit()
        await self.db.refresh(msg)
        return msg
