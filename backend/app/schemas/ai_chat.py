"""AI chat schemas."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

MessageRoleLiteral = Literal["user", "assistant", "system"]


class ChatMessageOut(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: MessageRoleLiteral
    content: str
    sources: dict[str, Any] | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatSessionOut(BaseModel):
    id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageOut] = []

    model_config = ConfigDict(from_attributes=True)


class ChatSessionListResponse(BaseModel):
    items: list[ChatSessionOut]
    total: int

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: uuid.UUID | None = None


class ChatResponse(BaseModel):
    session_id: uuid.UUID
    message: ChatMessageOut
    sources: dict[str, Any] | None = None
