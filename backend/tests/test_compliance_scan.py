"""Tests for P1.1 Compliance Scanning Enhancement."""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient


async def _create_framework(client: AsyncClient, slug: str = "test-fw") -> dict:
    resp = await client.post("/api/v1/frameworks", json={
        "name": "Test Framework",
        "slug": slug,
        "version": "1.0",
        "is_active": True,
    })
    assert resp.status_code == 201
    return resp.json()


async def _create_control(client: AsyncClient, framework_id: str, control_id: str, title: str, status: str) -> dict:
    resp = await client.post("/api/v1/controls", json={
        "framework_id": framework_id,
        "control_id": control_id,
        "title": title,
        "status": status,
    })
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_trigger_scan_creates_scan_record(client: AsyncClient):
    """Trigger a scan on a framework with controls; verify scan record is created."""
    fw = await _create_framework(client, slug="scan-fw-1")
    fw_id = fw["id"]

    # Create controls: 1 not_implemented (will fail), 1 implemented without evidence (neutral)
    await _create_control(client, fw_id, "C-1", "MFA Required", "not_implemented")
    await _create_control(client, fw_id, "C-2", "Encryption at Rest", "implemented")

    mock_reply = "Gap analysis: MFA is not implemented and poses significant risk."
    with patch("app.services.compliance_scanner._call_openrouter", new=AsyncMock(return_value=mock_reply)), \
         patch("app.services.compliance_scanner._call_ollama", new=AsyncMock(return_value=mock_reply)):
        resp = await client.post(f"/api/v1/frameworks/{fw_id}/scan")

    assert resp.status_code == 201
    data = resp.json()
    assert data["framework_id"] == fw_id
    assert data["controls_checked"] == 2
    assert data["controls_failed"] == 1
    assert data["controls_passed"] == 0  # no evidence on implemented control
    assert data["status"] == "completed"
    assert data["gap_analysis"] is not None


@pytest.mark.asyncio
async def test_list_scans_for_framework(client: AsyncClient):
    """After triggering two scans, list should return both."""
    fw = await _create_framework(client, slug="scan-fw-2")
    fw_id = fw["id"]
    await _create_control(client, fw_id, "C-1", "Patch Management", "not_implemented")

    mock_reply = "Heuristic fallback gap analysis."
    with patch("app.services.compliance_scanner._call_openrouter", new=AsyncMock(side_effect=Exception("no api key"))), \
         patch("app.services.compliance_scanner._call_ollama", new=AsyncMock(side_effect=Exception("no ollama"))):
        await client.post(f"/api/v1/frameworks/{fw_id}/scan")
        await client.post(f"/api/v1/frameworks/{fw_id}/scan")

    resp = await client.get(f"/api/v1/frameworks/{fw_id}/scans")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_trigger_scan_404_on_bad_framework_id(client: AsyncClient):
    """Triggering a scan for a non-existent framework returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = await client.post(f"/api/v1/frameworks/{fake_id}/scan")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_scan_includes_gap_analysis_from_mocked_llm(client: AsyncClient):
    """Scan gap_analysis is populated from the mocked LLM response."""
    fw = await _create_framework(client, slug="scan-fw-3")
    fw_id = fw["id"]
    await _create_control(client, fw_id, "C-1", "Access Control", "not_implemented")
    await _create_control(client, fw_id, "C-2", "Logging", "not_implemented")

    expected_analysis = "Two critical controls are missing: access control and logging. Immediate action required."
    with patch("app.services.compliance_scanner._call_openrouter", new=AsyncMock(return_value=expected_analysis)), \
         patch("app.services.compliance_scanner._call_ollama", new=AsyncMock(return_value=expected_analysis)):
        resp = await client.post(f"/api/v1/frameworks/{fw_id}/scan")

    assert resp.status_code == 201
    data = resp.json()
    assert data["gap_analysis"] == expected_analysis
    assert data["controls_failed"] == 2
