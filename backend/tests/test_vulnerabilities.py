import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_vulnerability(client: AsyncClient):
    # Create asset first
    asset_resp = await client.post("/api/v1/assets", json={
        "name": "vuln-test-server",
        "asset_type": "server",
        "environment": "production",
    })
    asset_id = asset_resp.json()["id"]

    response = await client.post("/api/v1/vulnerabilities", json={
        "asset_id": asset_id,
        "title": "Critical SQL Injection",
        "description": "SQL injection in login endpoint",
        "severity": "critical",
        "cvss_score": 9.8,
        "cve_id": "CVE-2024-1234",
        "status": "open",
        "remediation": "Use parameterized queries",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Critical SQL Injection"
    assert data["severity"] == "critical"
    assert data["cvss_score"] == 9.8
    assert data["asset_id"] == asset_id


@pytest.mark.asyncio
async def test_create_vulnerability_missing_asset(client: AsyncClient):
    fake_asset = "12345678-1234-5678-1234-567812345678"
    response = await client.post("/api/v1/vulnerabilities", json={
        "asset_id": fake_asset,
        "title": "Fake Vuln",
        "description": "desc",
        "severity": "high",
    })
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_vulnerabilities(client: AsyncClient):
    asset_resp = await client.post("/api/v1/assets", json={
        "name": "list-test-server",
        "asset_type": "server",
        "environment": "production",
    })
    asset_id = asset_resp.json()["id"]

    await client.post("/api/v1/vulnerabilities", json={
        "asset_id": asset_id,
        "title": "Vuln One",
        "description": "desc one",
        "severity": "high",
    })
    await client.post("/api/v1/vulnerabilities", json={
        "asset_id": asset_id,
        "title": "Vuln Two",
        "description": "desc two",
        "severity": "medium",
    })

    response = await client.get("/api/v1/vulnerabilities")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_list_vulnerabilities_filtered_by_severity(client: AsyncClient):
    asset_resp = await client.post("/api/v1/assets", json={
        "name": "filter-test-server",
        "asset_type": "server",
        "environment": "production",
    })
    asset_id = asset_resp.json()["id"]

    await client.post("/api/v1/vulnerabilities", json={
        "asset_id": asset_id,
        "title": "Critical Vuln",
        "description": "desc",
        "severity": "critical",
    })
    await client.post("/api/v1/vulnerabilities", json={
        "asset_id": asset_id,
        "title": "Low Vuln",
        "description": "desc",
        "severity": "low",
    })

    response = await client.get("/api/v1/vulnerabilities?severity=critical")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["severity"] == "critical"


@pytest.mark.asyncio
async def test_get_vulnerability(client: AsyncClient):
    asset_resp = await client.post("/api/v1/assets", json={
        "name": "get-test-server",
        "asset_type": "server",
        "environment": "production",
    })
    asset_id = asset_resp.json()["id"]

    create_resp = await client.post("/api/v1/vulnerabilities", json={
        "asset_id": asset_id,
        "title": "Get Me",
        "description": "desc",
        "severity": "high",
    })
    vuln_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/vulnerabilities/{vuln_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Get Me"


@pytest.mark.asyncio
async def test_update_vulnerability_status(client: AsyncClient):
    asset_resp = await client.post("/api/v1/assets", json={
        "name": "update-test-server",
        "asset_type": "server",
        "environment": "production",
    })
    asset_id = asset_resp.json()["id"]

    create_resp = await client.post("/api/v1/vulnerabilities", json={
        "asset_id": asset_id,
        "title": "Update Me",
        "description": "desc",
        "severity": "high",
    })
    vuln_id = create_resp.json()["id"]

    response = await client.put(f"/api/v1/vulnerabilities/{vuln_id}", json={
        "status": "resolved",
    })
    assert response.status_code == 200
    assert response.json()["status"] == "resolved"


@pytest.mark.asyncio
async def test_delete_vulnerability(client: AsyncClient):
    asset_resp = await client.post("/api/v1/assets", json={
        "name": "delete-test-server",
        "asset_type": "server",
        "environment": "production",
    })
    asset_id = asset_resp.json()["id"]

    create_resp = await client.post("/api/v1/vulnerabilities", json={
        "asset_id": asset_id,
        "title": "Delete Me",
        "description": "desc",
        "severity": "low",
    })
    vuln_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/vulnerabilities/{vuln_id}")
    assert response.status_code == 204
    get_resp = await client.get(f"/api/v1/vulnerabilities/{vuln_id}")
    assert get_resp.status_code == 404
