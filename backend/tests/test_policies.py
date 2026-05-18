import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_policy(client: AsyncClient):
    response = await client.post("/api/v1/policies", json={
        "title": "Acceptable Use Policy",
        "content": "# AUP\nAll users must follow these guidelines.",
        "version": "1.0.0",
        "status": "draft",
        "category": "acceptable_use",
        "requires_acknowledgment": True,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Acceptable Use Policy"
    assert data["status"] == "draft"
    assert data["category"] == "acceptable_use"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_policies(client: AsyncClient):
    await client.post("/api/v1/policies", json={
        "title": "Data Protection Policy",
        "content": "Protect all data.",
        "version": "1.0.0",
        "status": "published",
        "category": "data_protection",
    })
    response = await client.get("/api/v1/policies")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_list_policies_filter_by_status(client: AsyncClient):
    await client.post("/api/v1/policies", json={
        "title": "Draft Policy", "content": "...", "version": "1.0",
        "status": "draft", "category": "access_control",
    })
    await client.post("/api/v1/policies", json={
        "title": "Published Policy", "content": "...", "version": "1.0",
        "status": "published", "category": "access_control",
    })
    response = await client.get("/api/v1/policies?status=published")
    assert response.status_code == 200
    for item in response.json()["items"]:
        assert item["status"] == "published"


@pytest.mark.asyncio
async def test_get_policy(client: AsyncClient):
    create = await client.post("/api/v1/policies", json={
        "title": "IR Policy", "content": "Respond fast.", "version": "2.0",
        "status": "published", "category": "incident_response",
    })
    policy_id = create.json()["id"]
    response = await client.get(f"/api/v1/policies/{policy_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "IR Policy"


@pytest.mark.asyncio
async def test_update_policy(client: AsyncClient):
    create = await client.post("/api/v1/policies", json={
        "title": "Old Title", "content": "Old content.", "version": "1.0",
        "status": "draft", "category": "remote_work",
    })
    policy_id = create.json()["id"]
    response = await client.put(f"/api/v1/policies/{policy_id}", json={
        "title": "New Title", "status": "published",
    })
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"
    assert response.json()["status"] == "published"


@pytest.mark.asyncio
async def test_delete_policy(client: AsyncClient):
    create = await client.post("/api/v1/policies", json={
        "title": "To Delete", "content": "x", "version": "1.0",
        "status": "draft", "category": "data_protection",
    })
    policy_id = create.json()["id"]
    assert (await client.delete(f"/api/v1/policies/{policy_id}")).status_code == 204
    assert (await client.get(f"/api/v1/policies/{policy_id}")).status_code == 404


@pytest.mark.asyncio
async def test_acknowledge_policy(client: AsyncClient):
    create = await client.post("/api/v1/policies", json={
        "title": "Must Sign", "content": "Sign this.", "version": "1.0",
        "status": "published", "category": "acceptable_use",
        "requires_acknowledgment": True,
    })
    policy_id = create.json()["id"]
    response = await client.post(f"/api/v1/policies/{policy_id}/acknowledge", json={
        "employee_email": "alice@example.com",
        "employee_name": "Alice",
        "ip_address": "192.168.1.1",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["employee_email"] == "alice@example.com"
    assert data["acknowledged_at"] is not None


@pytest.mark.asyncio
async def test_acknowledge_draft_policy_rejected(client: AsyncClient):
    create = await client.post("/api/v1/policies", json={
        "title": "Draft Only", "content": "x", "version": "1.0",
        "status": "draft", "category": "access_control",
    })
    policy_id = create.json()["id"]
    response = await client.post(f"/api/v1/policies/{policy_id}/acknowledge", json={
        "employee_email": "bob@example.com",
    })
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_policy_not_found(client: AsyncClient):
    fake_id = "12345678-1234-5678-1234-567812345678"
    assert (await client.get(f"/api/v1/policies/{fake_id}")).status_code == 404
