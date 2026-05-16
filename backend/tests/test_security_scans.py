import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_scan(client: AsyncClient):
    asset_resp = await client.post("/api/v1/assets", json={
        "name": "scan-test-server",
        "asset_type": "server",
        "environment": "production",
    })
    asset_id = asset_resp.json()["id"]

    response = await client.post("/api/v1/scans", json={
        "target_asset_id": asset_id,
        "scan_type": "vulnerability",
        "status": "pending",
        "findings_count": 0,
        "scan_metadata": {"scanner": "trivy", "version": "0.50.0"},
    })
    assert response.status_code == 201
    data = response.json()
    assert data["scan_type"] == "vulnerability"
    assert data["status"] == "pending"
    assert data["target_asset_id"] == asset_id


@pytest.mark.asyncio
async def test_create_scan_missing_asset(client: AsyncClient):
    fake_asset = "12345678-1234-5678-1234-567812345678"
    response = await client.post("/api/v1/scans", json={
        "target_asset_id": fake_asset,
        "scan_type": "web",
    })
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_scans(client: AsyncClient):
    asset_resp = await client.post("/api/v1/assets", json={
        "name": "list-scan-server",
        "asset_type": "server",
        "environment": "production",
    })
    asset_id = asset_resp.json()["id"]

    await client.post("/api/v1/scans", json={
        "target_asset_id": asset_id,
        "scan_type": "vulnerability",
        "status": "completed",
    })
    await client.post("/api/v1/scans", json={
        "target_asset_id": asset_id,
        "scan_type": "container",
        "status": "pending",
    })

    response = await client.get("/api/v1/scans")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_list_scans_filtered_by_type(client: AsyncClient):
    asset_resp = await client.post("/api/v1/assets", json={
        "name": "filter-scan-server",
        "asset_type": "server",
        "environment": "production",
    })
    asset_id = asset_resp.json()["id"]

    await client.post("/api/v1/scans", json={
        "target_asset_id": asset_id,
        "scan_type": "vulnerability",
    })
    await client.post("/api/v1/scans", json={
        "target_asset_id": asset_id,
        "scan_type": "compliance",
    })

    response = await client.get("/api/v1/scans?scan_type=vulnerability")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["scan_type"] == "vulnerability"


@pytest.mark.asyncio
async def test_update_scan_status(client: AsyncClient):
    asset_resp = await client.post("/api/v1/assets", json={
        "name": "update-scan-server",
        "asset_type": "server",
        "environment": "production",
    })
    asset_id = asset_resp.json()["id"]

    create_resp = await client.post("/api/v1/scans", json={
        "target_asset_id": asset_id,
        "scan_type": "api",
        "status": "running",
    })
    scan_id = create_resp.json()["id"]

    response = await client.put(f"/api/v1/scans/{scan_id}", json={
        "status": "completed",
        "findings_count": 12,
        "risk_score": 65,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["findings_count"] == 12
    assert data["risk_score"] == 65


@pytest.mark.asyncio
async def test_delete_scan(client: AsyncClient):
    asset_resp = await client.post("/api/v1/assets", json={
        "name": "delete-scan-server",
        "asset_type": "server",
        "environment": "production",
    })
    asset_id = asset_resp.json()["id"]

    create_resp = await client.post("/api/v1/scans", json={
        "target_asset_id": asset_id,
        "scan_type": "web",
    })
    scan_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/scans/{scan_id}")
    assert response.status_code == 204
    get_resp = await client.get(f"/api/v1/scans/{scan_id}")
    assert get_resp.status_code == 404
