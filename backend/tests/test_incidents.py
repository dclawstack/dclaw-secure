"""Tests for P1.4 Incident Response feature."""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_incident(client: AsyncClient):
    """Test creating an incident and verifying default status is open."""
    resp = await client.post("/api/v1/incidents", json={
        "title": "Suspicious Login Activity",
        "description": "Multiple failed login attempts detected from unknown IP.",
        "severity": "high",
        "incident_type": "breach",
        "affected_asset_ids": None,
        "assigned_to": "security@example.com",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Suspicious Login Activity"
    assert data["status"] == "open"
    assert data["severity"] == "high"
    assert data["incident_type"] == "breach"
    assert data["actions"] == []


@pytest.mark.asyncio
async def test_list_incidents_with_status_filter(client: AsyncClient):
    """Test listing incidents filtered by status."""
    # Create two incidents
    await client.post("/api/v1/incidents", json={
        "title": "Open Incident",
        "description": "An open incident.",
        "severity": "medium",
        "incident_type": "phishing",
    })
    incident_resp = await client.post("/api/v1/incidents", json={
        "title": "Phishing Campaign",
        "description": "Mass phishing emails detected.",
        "severity": "high",
        "incident_type": "phishing",
    })
    incident_id = incident_resp.json()["id"]

    # Update second incident to investigating
    await client.put(f"/api/v1/incidents/{incident_id}", json={"status": "investigating"})

    # Filter by open status
    resp = await client.get("/api/v1/incidents?status=open")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["status"] == "open"

    # Filter by investigating status
    resp2 = await client.get("/api/v1/incidents?status=investigating")
    assert resp2.status_code == 200
    assert resp2.json()["total"] >= 1
    for item in resp2.json()["items"]:
        assert item["status"] == "investigating"


@pytest.mark.asyncio
async def test_get_incident_404(client: AsyncClient):
    """Test 404 response for unknown incident id."""
    resp = await client.get("/api/v1/incidents/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_add_action_and_list_actions(client: AsyncClient):
    """Test adding an action to an incident and listing actions."""
    incident_resp = await client.post("/api/v1/incidents", json={
        "title": "Ransomware Attack",
        "description": "Ransomware detected on production servers.",
        "severity": "critical",
        "incident_type": "ransomware",
    })
    assert incident_resp.status_code == 201
    incident_id = incident_resp.json()["id"]

    # Add an action
    action_resp = await client.post(f"/api/v1/incidents/{incident_id}/actions", json={
        "action_type": "detected",
        "description": "Ransomware identified by EDR solution.",
        "performed_by": "soc@example.com",
    })
    assert action_resp.status_code == 201
    action = action_resp.json()
    assert action["action_type"] == "detected"
    assert action["incident_id"] == incident_id

    # Add a second action
    await client.post(f"/api/v1/incidents/{incident_id}/actions", json={
        "action_type": "contained",
        "description": "Isolated affected systems from the network.",
        "performed_by": "soc@example.com",
    })

    # List actions
    list_resp = await client.get(f"/api/v1/incidents/{incident_id}/actions")
    assert list_resp.status_code == 200
    actions = list_resp.json()
    assert len(actions) == 2
    action_types = {a["action_type"] for a in actions}
    assert "detected" in action_types
    assert "contained" in action_types


@pytest.mark.asyncio
async def test_generate_playbook(client: AsyncClient):
    """Test playbook generation via LLM (mocked) sets ai_playbook on the incident."""
    incident_resp = await client.post("/api/v1/incidents", json={
        "title": "DDoS Attack",
        "description": "Large-scale DDoS attack targeting our API gateway.",
        "severity": "critical",
        "incident_type": "ddos",
    })
    assert incident_resp.status_code == 201
    incident_id = incident_resp.json()["id"]

    mock_playbook = (
        "1. Enable rate limiting at edge. "
        "2. Block malicious IPs. "
        "3. Scale infrastructure. "
        "4. Notify ISP for upstream filtering. "
        "5. Document and review."
    )

    with patch(
        "app.services.incident_service._call_openrouter",
        new=AsyncMock(return_value=mock_playbook),
    ), patch(
        "app.services.incident_service._call_ollama",
        new=AsyncMock(return_value=mock_playbook),
    ):
        playbook_resp = await client.post(f"/api/v1/incidents/{incident_id}/generate-playbook")

    assert playbook_resp.status_code == 200
    data = playbook_resp.json()
    assert data["ai_playbook"] is not None
    assert len(data["ai_playbook"]) > 0


@pytest.mark.asyncio
async def test_update_incident_status(client: AsyncClient):
    """Test updating an incident's status to 'contained'."""
    incident_resp = await client.post("/api/v1/incidents", json={
        "title": "Insider Threat",
        "description": "Employee exfiltrating sensitive data.",
        "severity": "high",
        "incident_type": "insider_threat",
    })
    assert incident_resp.status_code == 201
    incident_id = incident_resp.json()["id"]
    assert incident_resp.json()["status"] == "open"

    update_resp = await client.put(f"/api/v1/incidents/{incident_id}", json={
        "status": "contained",
        "assigned_to": "ir-team@example.com",
    })
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["status"] == "contained"
    assert updated["assigned_to"] == "ir-team@example.com"
