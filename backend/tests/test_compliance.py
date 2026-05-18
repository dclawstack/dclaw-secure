import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_framework(client: AsyncClient):
    response = await client.post("/api/v1/frameworks", json={
        "name": "SOC2 Type II",
        "slug": "soc2",
        "version": "2017",
        "description": "Service Organization Controls",
        "is_active": True,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "SOC2 Type II"
    assert data["slug"] == "soc2"


@pytest.mark.asyncio
async def test_create_framework_duplicate_slug(client: AsyncClient):
    payload = {"name": "SOC2", "slug": "soc2-dup", "is_active": True}
    await client.post("/api/v1/frameworks", json=payload)
    response = await client.post("/api/v1/frameworks", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_frameworks(client: AsyncClient):
    await client.post("/api/v1/frameworks", json={"name": "ISO 27001", "slug": "iso27001", "is_active": True})
    response = await client.get("/api/v1/frameworks")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


@pytest.mark.asyncio
async def test_get_framework(client: AsyncClient):
    create = await client.post("/api/v1/frameworks", json={"name": "PCI-DSS", "slug": "pci-dss", "is_active": True})
    fw_id = create.json()["id"]
    response = await client.get(f"/api/v1/frameworks/{fw_id}")
    assert response.status_code == 200
    assert response.json()["slug"] == "pci-dss"


@pytest.mark.asyncio
async def test_update_framework(client: AsyncClient):
    create = await client.post("/api/v1/frameworks", json={"name": "GDPR", "slug": "gdpr", "is_active": True})
    fw_id = create.json()["id"]
    response = await client.put(f"/api/v1/frameworks/{fw_id}", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_delete_framework(client: AsyncClient):
    create = await client.post("/api/v1/frameworks", json={"name": "HIPAA", "slug": "hipaa", "is_active": True})
    fw_id = create.json()["id"]
    assert (await client.delete(f"/api/v1/frameworks/{fw_id}")).status_code == 204
    assert (await client.get(f"/api/v1/frameworks/{fw_id}")).status_code == 404


@pytest.mark.asyncio
async def test_create_control(client: AsyncClient):
    fw = (await client.post("/api/v1/frameworks", json={"name": "SOC2", "slug": "soc2-ctrl", "is_active": True})).json()
    response = await client.post("/api/v1/controls", json={
        "framework_id": fw["id"],
        "control_id": "CC6.1",
        "title": "Logical Access Controls",
        "description": "Access is restricted to authorized personnel.",
        "category": "Logical and Physical Access Controls",
        "status": "not_implemented",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["control_id"] == "CC6.1"
    assert data["status"] == "not_implemented"


@pytest.mark.asyncio
async def test_list_controls_by_framework(client: AsyncClient):
    fw = (await client.post("/api/v1/frameworks", json={"name": "NIST", "slug": "nist-list", "is_active": True})).json()
    for i in range(3):
        await client.post("/api/v1/controls", json={
            "framework_id": fw["id"],
            "control_id": f"AC-{i+1}",
            "title": f"Control {i+1}",
            "status": "not_implemented",
        })
    response = await client.get(f"/api/v1/frameworks/{fw['id']}/controls")
    assert response.status_code == 200
    assert response.json()["total"] == 3


@pytest.mark.asyncio
async def test_update_control_status(client: AsyncClient):
    fw = (await client.post("/api/v1/frameworks", json={"name": "CIS", "slug": "cis-upd", "is_active": True})).json()
    ctrl = (await client.post("/api/v1/controls", json={
        "framework_id": fw["id"], "control_id": "1.1",
        "title": "Patch Management", "status": "not_implemented",
    })).json()
    response = await client.put(f"/api/v1/controls/{ctrl['id']}", json={
        "status": "implemented",
        "evidence_url": "https://example.com/evidence.pdf",
        "notes": "Verified via automated scan.",
    })
    assert response.status_code == 200
    assert response.json()["status"] == "implemented"
    assert response.json()["evidence_url"] == "https://example.com/evidence.pdf"


@pytest.mark.asyncio
async def test_framework_posture(client: AsyncClient):
    fw = (await client.post("/api/v1/frameworks", json={"name": "Test FW", "slug": "test-posture", "is_active": True})).json()
    for status in ["implemented", "implemented", "not_implemented", "not_applicable"]:
        await client.post("/api/v1/controls", json={
            "framework_id": fw["id"], "control_id": f"T-{status[:3]}",
            "title": status, "status": status,
        })
    response = await client.get(f"/api/v1/frameworks/{fw['id']}/posture")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert data["implemented"] == 2
    assert data["compliance_pct"] == pytest.approx(66.7, abs=0.1)
