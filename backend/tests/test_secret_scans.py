"""Tests for P1.3 Secret Scanning."""

import pytest
from httpx import AsyncClient

# A realistic AWS access key for testing detection
AWS_KEY_CONTENT = """
# Configuration file
AWS_ACCESS_KEY_ID = AKIAIOSFODNN7EXAMPLE
AWS_REGION = us-east-1
"""

# Clean content with no secrets
CLEAN_CONTENT = """
# Application config
DEBUG = false
LOG_LEVEL = info
PORT = 8080
"""


@pytest.mark.asyncio
async def test_create_scan_with_aws_key_finds_secrets(client: AsyncClient):
    """Scanning content with an AWS access key should find at least one secret."""
    resp = await client.post("/api/v1/secret-scans", json={
        "scan_target": "config/app.env",
        "scan_type": "config_file",
        "content": AWS_KEY_CONTENT,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["scan_target"] == "config/app.env"
    assert data["scan_type"] == "config_file"
    assert data["status"] == "completed"
    assert data["secrets_found"] >= 1
    assert data["files_scanned"] == 1
    assert len(data["findings"]) >= 1
    # Verify masking
    finding = data["findings"][0]
    assert "..." in finding["masked_value"] or finding["masked_value"] == "****"
    assert finding["secret_type"] in ["api_key", "token", "password", "database_url", "private_key", "jwt_secret", "other"]


@pytest.mark.asyncio
async def test_create_scan_with_clean_content_finds_nothing(client: AsyncClient):
    """Scanning clean content should return 0 secrets found."""
    resp = await client.post("/api/v1/secret-scans", json={
        "scan_target": "config/clean.env",
        "scan_type": "config_file",
        "content": CLEAN_CONTENT,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["secrets_found"] == 0
    assert data["findings"] == []


@pytest.mark.asyncio
async def test_mark_finding_as_revoked(client: AsyncClient):
    """Marking a finding as revoked updates is_revoked=True."""
    scan_resp = await client.post("/api/v1/secret-scans", json={
        "scan_target": "src/config.py",
        "scan_type": "filesystem",
        "content": AWS_KEY_CONTENT,
    })
    assert scan_resp.status_code == 201
    findings = scan_resp.json()["findings"]
    assert len(findings) >= 1
    finding_id = findings[0]["id"]

    patch_resp = await client.patch(f"/api/v1/secret-findings/{finding_id}", json={
        "is_revoked": True,
    })
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["is_revoked"] is True
    assert data["is_false_positive"] is False


@pytest.mark.asyncio
async def test_mark_finding_as_false_positive(client: AsyncClient):
    """Marking a finding as false positive updates is_false_positive=True."""
    scan_resp = await client.post("/api/v1/secret-scans", json={
        "scan_target": "tests/fixtures.py",
        "scan_type": "filesystem",
        "content": AWS_KEY_CONTENT,
    })
    assert scan_resp.status_code == 201
    findings = scan_resp.json()["findings"]
    assert len(findings) >= 1
    finding_id = findings[0]["id"]

    patch_resp = await client.patch(f"/api/v1/secret-findings/{finding_id}", json={
        "is_false_positive": True,
    })
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["is_false_positive"] is True
    assert data["is_revoked"] is False


@pytest.mark.asyncio
async def test_list_scans(client: AsyncClient):
    """List scans returns all created scan jobs."""
    await client.post("/api/v1/secret-scans", json={
        "scan_target": "file1.env",
        "scan_type": "config_file",
        "content": CLEAN_CONTENT,
    })
    await client.post("/api/v1/secret-scans", json={
        "scan_target": "file2.env",
        "scan_type": "config_file",
        "content": AWS_KEY_CONTENT,
    })

    resp = await client.get("/api/v1/secret-scans")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
