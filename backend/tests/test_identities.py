"""Tests for P0.4 Identity Security and behavioral analytics."""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_identity(client: AsyncClient):
    resp = await client.post("/api/v1/identities", json={
        "email": "alice@example.com",
        "display_name": "Alice Smith",
        "department": "Engineering",
        "role": "Developer",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "alice@example.com"
    assert data["risk_score"] == 0.0
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_identity_duplicate_email(client: AsyncClient):
    await client.post("/api/v1/identities", json={"email": "bob@example.com"})
    resp = await client.post("/api/v1/identities", json={"email": "bob@example.com"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_identities(client: AsyncClient):
    await client.post("/api/v1/identities", json={"email": "user1@example.com", "department": "Engineering"})
    await client.post("/api/v1/identities", json={"email": "user2@example.com", "department": "Finance"})

    resp = await client.get("/api/v1/identities")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 2

    resp2 = await client.get("/api/v1/identities?department=Finance")
    assert resp2.status_code == 200
    assert all(i["department"] == "Finance" for i in resp2.json()["items"])


@pytest.mark.asyncio
async def test_log_behavior_and_risk_update(client: AsyncClient):
    identity = await client.post("/api/v1/identities", json={"email": "dave@example.com"})
    identity_id = identity.json()["id"]

    mock_reply = "RISK_SCORE: 30\nANALYSIS: Low risk activity observed."
    with patch("app.services.identity_service._call_openrouter", new=AsyncMock(return_value=mock_reply)), \
         patch("app.services.identity_service._call_ollama", new=AsyncMock(return_value=mock_reply)):
        event_resp = await client.post(f"/api/v1/identities/{identity_id}/events", json={
            "event_type": "login",
            "ip_address": "192.168.1.1",
            "location": "New York, US",
        })
    assert event_resp.status_code == 201
    assert event_resp.json()["event_type"] == "login"

    identity_after = await client.get(f"/api/v1/identities/{identity_id}")
    assert identity_after.json()["last_seen"] is not None


@pytest.mark.asyncio
async def test_analyze_identity(client: AsyncClient):
    identity = await client.post("/api/v1/identities", json={"email": "risky@example.com", "role": "Admin"})
    identity_id = identity.json()["id"]

    mock_reply = "RISK_SCORE: 75\nANALYSIS: Admin account shows unusual data export patterns."
    with patch("app.services.identity_service._call_openrouter", new=AsyncMock(return_value=mock_reply)), \
         patch("app.services.identity_service._call_ollama", new=AsyncMock(return_value=mock_reply)):
        resp = await client.post(f"/api/v1/identities/{identity_id}/analyze")

    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_score"] == 75.0
    assert "Admin" in data["ai_analysis"] or "data export" in data["ai_analysis"]


@pytest.mark.asyncio
async def test_risky_identities_endpoint(client: AsyncClient):
    i1 = await client.post("/api/v1/identities", json={"email": "safe@example.com"})
    i2 = await client.post("/api/v1/identities", json={"email": "danger@example.com"})
    identity_id = i2.json()["id"]

    mock_reply = "RISK_SCORE: 80\nANALYSIS: High risk."
    with patch("app.services.identity_service._call_openrouter", new=AsyncMock(return_value=mock_reply)), \
         patch("app.services.identity_service._call_ollama", new=AsyncMock(return_value=mock_reply)):
        await client.post(f"/api/v1/identities/{identity_id}/analyze")

    risky = await client.get("/api/v1/identities/risky?threshold=50")
    assert risky.status_code == 200
    emails = [i["email"] for i in risky.json()]
    assert "danger@example.com" in emails
    assert "safe@example.com" not in emails


@pytest.mark.asyncio
async def test_identity_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/identities/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_behavior_events(client: AsyncClient):
    identity = await client.post("/api/v1/identities", json={"email": "eve@example.com"})
    identity_id = identity.json()["id"]

    mock_reply = "RISK_SCORE: 10\nANALYSIS: Low risk."
    with patch("app.services.identity_service._call_openrouter", new=AsyncMock(return_value=mock_reply)), \
         patch("app.services.identity_service._call_ollama", new=AsyncMock(return_value=mock_reply)):
        await client.post(f"/api/v1/identities/{identity_id}/events", json={"event_type": "login"})
        await client.post(f"/api/v1/identities/{identity_id}/events", json={"event_type": "api_call"})

    events_resp = await client.get(f"/api/v1/identities/{identity_id}/events")
    assert events_resp.status_code == 200
    assert events_resp.json()["total"] == 2
