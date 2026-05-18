"""Tests for C2.1 AI vulnerability prioritization."""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_prioritize_returns_score(client: AsyncClient):
    asset = await client.post("/api/v1/assets", json={
        "name": "prod-server",
        "asset_type": "server",
        "environment": "production",
    })
    asset_id = asset.json()["id"]

    vuln = await client.post("/api/v1/vulnerabilities", json={
        "asset_id": asset_id,
        "title": "Remote Code Execution",
        "description": "Unauthenticated RCE via deserialization",
        "severity": "critical",
        "cvss_score": 9.8,
    })
    vuln_id = vuln.json()["id"]

    mock_reply = "SCORE: 92\nREASON: Critical RCE on production server with high CVSS represents catastrophic risk."

    with patch("app.services.ai_service._call_openrouter", new=AsyncMock(return_value=mock_reply)):
        resp = await client.post(f"/api/v1/vulnerabilities/{vuln_id}/prioritize")

    assert resp.status_code == 200
    data = resp.json()
    assert data["business_impact_score"] == 92.0
    assert "RCE" in data["ai_priority_reason"] or "catastrophic" in data["ai_priority_reason"]


@pytest.mark.asyncio
async def test_prioritize_heuristic_fallback(client: AsyncClient):
    """When LLM raises, falls back to heuristic score."""
    asset = await client.post("/api/v1/assets", json={
        "name": "staging-api",
        "asset_type": "api",
        "environment": "staging",
    })
    asset_id = asset.json()["id"]

    vuln = await client.post("/api/v1/vulnerabilities", json={
        "asset_id": asset_id,
        "title": "SQL Injection",
        "description": "Classic SQL injection in login form",
        "severity": "high",
    })
    vuln_id = vuln.json()["id"]

    with patch("app.services.ai_service._call_openrouter", new=AsyncMock(side_effect=Exception("LLM unavailable"))):
        resp = await client.post(f"/api/v1/vulnerabilities/{vuln_id}/prioritize")

    assert resp.status_code == 200
    data = resp.json()
    assert data["business_impact_score"] is not None
    assert data["ai_priority_reason"] is not None


@pytest.mark.asyncio
async def test_prioritize_vuln_not_found(client: AsyncClient):
    import uuid
    resp = await client.post(f"/api/v1/vulnerabilities/{uuid.uuid4()}/prioritize")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_prioritize_persists_score(client: AsyncClient):
    """Score persists after a GET."""
    asset = await client.post("/api/v1/assets", json={
        "name": "db-prod",
        "asset_type": "database",
        "environment": "production",
    })
    asset_id = asset.json()["id"]
    vuln = await client.post("/api/v1/vulnerabilities", json={
        "asset_id": asset_id,
        "title": "Privilege escalation",
        "description": "Allows user to gain DBA privileges",
        "severity": "critical",
    })
    vuln_id = vuln.json()["id"]

    with patch("app.services.ai_service._call_openrouter", new=AsyncMock(return_value="SCORE: 78\nREASON: DB exploit.")):
        await client.post(f"/api/v1/vulnerabilities/{vuln_id}/prioritize")

    get_resp = await client.get(f"/api/v1/vulnerabilities/{vuln_id}")
    assert get_resp.json()["business_impact_score"] == 78.0
