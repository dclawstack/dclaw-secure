import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_stats_empty(client: AsyncClient):
    response = await client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_assets"] == 0
    assert data["total_vulnerabilities"] == 0
    assert data["critical_vulnerabilities"] == 0
    assert data["open_vulnerabilities"] == 0
    assert data["total_scans"] == 0
    assert data["published_policies_requiring_ack"] == 0
    assert data["total_acknowledgments"] == 0
    assert data["compliance_posture"] == []


@pytest.mark.asyncio
async def test_dashboard_stats_with_data(client: AsyncClient):
    # Create assets in different environments
    await client.post("/api/v1/assets", json={
        "name": "prod-server",
        "asset_type": "server",
        "environment": "production",
    })
    asset2 = await client.post("/api/v1/assets", json={
        "name": "staging-api",
        "asset_type": "api",
        "environment": "staging",
    })
    asset2_id = asset2.json()["id"]

    # Create vulnerabilities
    await client.post("/api/v1/vulnerabilities", json={
        "asset_id": asset2_id,
        "title": "Crit",
        "description": "desc",
        "severity": "critical",
    })
    await client.post("/api/v1/vulnerabilities", json={
        "asset_id": asset2_id,
        "title": "Med",
        "description": "desc",
        "severity": "medium",
        "status": "resolved",
    })

    # Create scan
    await client.post("/api/v1/scans", json={
        "target_asset_id": asset2_id,
        "scan_type": "vulnerability",
        "status": "completed",
        "findings_count": 2,
    })

    response = await client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_assets"] == 2
    assert data["total_vulnerabilities"] == 2
    assert data["critical_vulnerabilities"] == 1
    assert data["open_vulnerabilities"] == 1
    assert data["total_scans"] == 1
    assert data["assets_by_environment"]["production"] == 1
    assert data["assets_by_environment"]["staging"] == 1
    assert data["vulnerabilities_by_severity"]["critical"] == 1
    assert data["vulnerabilities_by_severity"]["medium"] == 1
