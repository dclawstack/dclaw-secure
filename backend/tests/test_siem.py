"""Tests for P0.3 SIEM event ingestion and AI correlation."""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_siem_event(client: AsyncClient):
    resp = await client.post("/api/v1/siem/events", json={
        "source_system": "cloudtrail",
        "event_type": "authentication",
        "severity": "high",
        "normalized_data": {"user": "alice@example.com", "action": "ConsoleLogin", "success": False},
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["source_system"] == "cloudtrail"
    assert data["event_type"] == "authentication"
    assert data["severity"] == "high"
    assert data["is_anomaly"] is False
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_list_siem_events_with_filters(client: AsyncClient):
    await client.post("/api/v1/siem/events", json={
        "source_system": "firewall",
        "event_type": "network",
        "severity": "medium",
    })
    await client.post("/api/v1/siem/events", json={
        "source_system": "edr",
        "event_type": "endpoint",
        "severity": "critical",
    })

    resp = await client.get("/api/v1/siem/events?event_type=network")
    assert resp.status_code == 200
    data = resp.json()
    assert all(e["event_type"] == "network" for e in data["items"])

    resp2 = await client.get("/api/v1/siem/events?severity=critical")
    assert resp2.status_code == 200
    assert all(e["severity"] == "critical" for e in resp2.json()["items"])


@pytest.mark.asyncio
async def test_get_siem_event_404(client: AsyncClient):
    resp = await client.get("/api/v1/siem/events/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_analyze_event_with_mocked_llm(client: AsyncClient):
    event = await client.post("/api/v1/siem/events", json={
        "source_system": "ids",
        "event_type": "threat",
        "severity": "critical",
        "normalized_data": {"attack_type": "port_scan", "target": "10.0.0.5"},
    })
    event_id = event.json()["id"]

    mock_reply = "ANOMALY: yes\nRISK_SCORE: 88\nANALYSIS: Active threat detected — port scan indicates reconnaissance activity."
    with patch("app.services.siem_service._call_openrouter", new=AsyncMock(return_value=mock_reply)), \
         patch("app.services.siem_service._call_ollama", new=AsyncMock(return_value=mock_reply)):
        resp = await client.post(f"/api/v1/siem/events/{event_id}/analyze")

    assert resp.status_code == 200
    data = resp.json()
    assert data["is_anomaly"] is True
    assert data["risk_score"] == 88.0
    assert "reconnaissance" in data["ai_analysis"]


@pytest.mark.asyncio
async def test_summary_stats(client: AsyncClient):
    await client.post("/api/v1/siem/events", json={"source_system": "s1", "event_type": "cloud", "severity": "low"})
    await client.post("/api/v1/siem/events", json={"source_system": "s2", "event_type": "cloud", "severity": "medium"})
    await client.post("/api/v1/siem/events", json={"source_system": "s3", "event_type": "network", "severity": "high"})

    resp = await client.get("/api/v1/siem/events/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_events"] >= 3
    assert "cloud" in data["by_event_type"]
    assert "network" in data["by_event_type"]
    assert "by_severity" in data


@pytest.mark.asyncio
async def test_heuristic_anomaly_detection(client: AsyncClient):
    # Threat events should always be flagged as anomaly by heuristic
    mock_reply = "ANOMALY: yes\nRISK_SCORE: 90\nANALYSIS: Threat event."
    with patch("app.services.siem_service._call_openrouter", new=AsyncMock(return_value=mock_reply)), \
         patch("app.services.siem_service._call_ollama", new=AsyncMock(return_value=mock_reply)):
        event = await client.post("/api/v1/siem/events?analyze=true", json={
            "source_system": "threat-feed",
            "event_type": "threat",
            "severity": "critical",
        })
    assert event.status_code == 201
    assert event.json()["is_anomaly"] is True


@pytest.mark.asyncio
async def test_create_event_with_asset_link(client: AsyncClient):
    asset = await client.post("/api/v1/assets", json={
        "name": "web-server",
        "asset_type": "server",
        "environment": "production",
    })
    asset_id = asset.json()["id"]

    resp = await client.post("/api/v1/siem/events", json={
        "source_system": "waf",
        "event_type": "application",
        "severity": "high",
        "asset_id": asset_id,
    })
    assert resp.status_code == 201
    assert resp.json()["asset_id"] == asset_id
