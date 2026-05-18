"""Tests for C2.2 compliance evidence collection."""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def framework_and_control(client: AsyncClient):
    fw = await client.post("/api/v1/frameworks", json={"name": "SOC2", "slug": "soc2"})
    fw_id = fw.json()["id"]
    ctrl = await client.post("/api/v1/controls", json={
        "framework_id": fw_id,
        "control_id": "CC6.1",
        "title": "Logical Access Controls",
    })
    return fw_id, ctrl.json()["id"]


@pytest.mark.asyncio
async def test_add_evidence(client: AsyncClient, framework_and_control):
    _, ctrl_id = framework_and_control
    resp = await client.post(f"/api/v1/controls/{ctrl_id}/evidence", json={
        "evidence_type": "screenshot",
        "description": "Screenshot of MFA enforcement screen",
        "artifact_url": "https://example.com/evidence/mfa.png",
        "collected_by": "alice@example.com",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["evidence_type"] == "screenshot"
    assert data["description"] == "Screenshot of MFA enforcement screen"
    assert data["control_id"] == ctrl_id


@pytest.mark.asyncio
async def test_list_evidence(client: AsyncClient, framework_and_control):
    _, ctrl_id = framework_and_control
    await client.post(f"/api/v1/controls/{ctrl_id}/evidence", json={
        "evidence_type": "manual",
        "description": "First piece of evidence",
    })
    await client.post(f"/api/v1/controls/{ctrl_id}/evidence", json={
        "evidence_type": "export",
        "description": "CSV export of user list",
    })
    resp = await client.get(f"/api/v1/controls/{ctrl_id}/evidence")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_delete_evidence(client: AsyncClient, framework_and_control):
    _, ctrl_id = framework_and_control
    ev_resp = await client.post(f"/api/v1/controls/{ctrl_id}/evidence", json={
        "evidence_type": "policy",
        "description": "Linked policy document",
    })
    ev_id = ev_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/evidence/{ev_id}")
    assert del_resp.status_code == 204

    list_resp = await client.get(f"/api/v1/controls/{ctrl_id}/evidence")
    assert list_resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_evidence_included_in_control_response(client: AsyncClient, framework_and_control):
    fw_id, ctrl_id = framework_and_control
    await client.post(f"/api/v1/controls/{ctrl_id}/evidence", json={
        "evidence_type": "scan_report",
        "description": "Nessus scan report",
    })
    ctrl_resp = await client.get(f"/api/v1/controls/{ctrl_id}")
    assert ctrl_resp.status_code == 200
    evidence = ctrl_resp.json()["evidence"]
    assert len(evidence) == 1
    assert evidence[0]["description"] == "Nessus scan report"


@pytest.mark.asyncio
async def test_add_evidence_control_not_found(client: AsyncClient):
    import uuid
    resp = await client.post(f"/api/v1/controls/{uuid.uuid4()}/evidence", json={
        "evidence_type": "manual",
        "description": "Test",
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_evidence_not_found(client: AsyncClient):
    import uuid
    resp = await client.delete(f"/api/v1/evidence/{uuid.uuid4()}")
    assert resp.status_code == 404
