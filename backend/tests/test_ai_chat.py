"""AI chat tests using mocked LLM calls."""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_creates_session(client: AsyncClient):
    with patch("app.services.ai_service.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = ("You have 0 critical vulnerabilities.", {"asset_count": 0})
        response = await client.post("/api/v1/ai/chat", json={
            "message": "What are my critical vulnerabilities?",
        })
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert data["message"]["role"] == "assistant"
    assert "critical" in data["message"]["content"].lower()


@pytest.mark.asyncio
async def test_chat_continues_existing_session(client: AsyncClient):
    with patch("app.services.ai_service.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = ("First response.", {})
        first = await client.post("/api/v1/ai/chat", json={"message": "Hello"})
    session_id = first.json()["session_id"]

    with patch("app.services.ai_service.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = ("Follow-up response.", {})
        second = await client.post("/api/v1/ai/chat", json={
            "message": "Tell me more",
            "session_id": session_id,
        })
    assert second.status_code == 201
    assert second.json()["session_id"] == session_id


@pytest.mark.asyncio
async def test_chat_invalid_session(client: AsyncClient):
    fake_id = "12345678-1234-5678-1234-567812345678"
    response = await client.post("/api/v1/ai/chat", json={
        "message": "Hello",
        "session_id": fake_id,
    })
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_sessions(client: AsyncClient):
    with patch("app.services.ai_service.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = ("Response.", {})
        await client.post("/api/v1/ai/chat", json={"message": "Test session"})
    response = await client.get("/api/v1/ai/sessions")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


@pytest.mark.asyncio
async def test_get_session(client: AsyncClient):
    with patch("app.services.ai_service.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = ("Hello.", {})
        created = await client.post("/api/v1/ai/chat", json={"message": "Hi"})
    session_id = created.json()["session_id"]
    response = await client.get(f"/api/v1/ai/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert len(data["messages"]) == 2  # user + assistant


@pytest.mark.asyncio
async def test_delete_session(client: AsyncClient):
    with patch("app.services.ai_service.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = ("Bye.", {})
        created = await client.post("/api/v1/ai/chat", json={"message": "Delete me"})
    session_id = created.json()["session_id"]
    assert (await client.delete(f"/api/v1/ai/sessions/{session_id}")).status_code == 204
    assert (await client.get(f"/api/v1/ai/sessions/{session_id}")).status_code == 404
