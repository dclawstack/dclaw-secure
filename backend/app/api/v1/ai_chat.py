"""AI Security Copilot router."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.ai_chat import AIChatSession, MessageRole
from app.repositories.ai_chat_repo import ChatSessionRepository
from app.schemas.ai_chat import (
    ChatRequest, ChatResponse, ChatSessionOut, ChatSessionListResponse,
)
from app.services import ai_service

router = APIRouter(tags=["ai"])


@router.post("/chat", response_model=ChatResponse, status_code=201)
async def chat(payload: ChatRequest, db: AsyncSession = Depends(get_db)):
    repo = ChatSessionRepository(db)

    # Resolve or create session
    if payload.session_id:
        session = await repo.get_by_id(payload.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        session = AIChatSession(title=payload.message[:60])
        session = await repo.create(session)

    # Build history for context (last 10 messages)
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in (session.messages or [])[-10:]
    ]

    # Store user message
    await repo.add_message(session.id, MessageRole.USER, payload.message)

    # Generate AI response
    reply, sources = await ai_service.generate_response(db, payload.message, history)

    # Store assistant message
    assistant_msg = await repo.add_message(session.id, MessageRole.ASSISTANT, reply, sources)

    return {"session_id": session.id, "message": assistant_msg, "sources": sources}


@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_sessions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = ChatSessionRepository(db)
    items, total = await repo.list_sessions(limit=limit, offset=offset)
    return {"items": items, "total": total}


@router.get("/sessions/{session_id}", response_model=ChatSessionOut)
async def get_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = ChatSessionRepository(db)
    session = await repo.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = ChatSessionRepository(db)
    session = await repo.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    await repo.delete(session)
    return None
