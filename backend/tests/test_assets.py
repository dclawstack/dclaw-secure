import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_asset(client: AsyncClient):
    response = await client.post("/api/v1/assets", json={
        "name": "prod-web-01",
        "asset_type": "server",
        "environment": "production",
        "status": "active",
        "cloud_provider": "aws",
        "region": "us-east-1",
        "owner_email": "admin@example.com",
        "risk_score": 30,
        "description": "Primary web server",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "prod-web-01"
    assert data["asset_type"] == "server"
    assert data["risk_score"] == 30
    assert "id" in data


@pytest.mark.asyncio
async def test_list_assets(client: AsyncClient):
    # Create first
    await client.post("/api/v1/assets", json={
        "name": "staging-db-01",
        "asset_type": "database",
        "environment": "staging",
        "status": "active",
    })
    response = await client.get("/api/v1/assets")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_asset(client: AsyncClient):
    create_resp = await client.post("/api/v1/assets", json={
        "name": "test-asset",
        "asset_type": "api",
        "environment": "development",
    })
    asset_id = create_resp.json()["id"]
    response = await client.get(f"/api/v1/assets/{asset_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "test-asset"


@pytest.mark.asyncio
async def test_update_asset(client: AsyncClient):
    create_resp = await client.post("/api/v1/assets", json={
        "name": "old-name",
        "asset_type": "container",
        "environment": "production",
    })
    asset_id = create_resp.json()["id"]
    response = await client.put(f"/api/v1/assets/{asset_id}", json={
        "name": "new-name",
        "risk_score": 75,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "new-name"
    assert data["risk_score"] == 75


@pytest.mark.asyncio
async def test_delete_asset(client: AsyncClient):
    create_resp = await client.post("/api/v1/assets", json={
        "name": "to-delete",
        "asset_type": "workstation",
        "environment": "production",
    })
    asset_id = create_resp.json()["id"]
    response = await client.delete(f"/api/v1/assets/{asset_id}")
    assert response.status_code == 204
    get_resp = await client.get(f"/api/v1/assets/{asset_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_list_assets_with_filter(client: AsyncClient):
    await client.post("/api/v1/assets", json={
        "name": "prod-server",
        "asset_type": "server",
        "environment": "production",
    })
    await client.post("/api/v1/assets", json={
        "name": "dev-api",
        "asset_type": "api",
        "environment": "development",
    })
    response = await client.get("/api/v1/assets?environment=development")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["environment"] == "development"


@pytest.mark.asyncio
async def test_get_asset_not_found(client: AsyncClient):
    fake_id = "12345678-1234-5678-1234-567812345678"
    response = await client.get(f"/api/v1/assets/{fake_id}")
    assert response.status_code == 404
