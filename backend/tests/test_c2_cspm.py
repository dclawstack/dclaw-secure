"""Tests for C2.3 CSPM mock integration."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cspm_scan_empty_inventory(client: AsyncClient):
    resp = await client.post("/api/v1/cspm/scan", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["scanned_assets"] == 0
    assert data["new_findings"] == 0


@pytest.mark.asyncio
async def test_cspm_creates_findings_for_unowned_production_asset(client: AsyncClient):
    await client.post("/api/v1/assets", json={
        "name": "prod-web-server",
        "asset_type": "server",
        "environment": "production",
        # no owner_email — triggers CSPM-001
    })
    resp = await client.post("/api/v1/cspm/scan", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["new_findings"] >= 1
    rule_ids = [f["rule_id"] for f in data["findings"] if f["created"]]
    assert "001" in rule_ids


@pytest.mark.asyncio
async def test_cspm_idempotent_no_duplicate_findings(client: AsyncClient):
    await client.post("/api/v1/assets", json={
        "name": "prod-db",
        "asset_type": "database",
        "environment": "production",
    })
    first = await client.post("/api/v1/cspm/scan", json={})
    second = await client.post("/api/v1/cspm/scan", json={})

    first_new = first.json()["new_findings"]
    assert second.json()["new_findings"] == 0
    assert second.json()["skipped_duplicates"] == first_new


@pytest.mark.asyncio
async def test_cspm_dev_asset_not_triggered_by_prod_rules(client: AsyncClient):
    await client.post("/api/v1/assets", json={
        "name": "dev-server",
        "asset_type": "server",
        "environment": "development",
        # no owner_email — but CSPM-001 only fires for production
    })
    resp = await client.post("/api/v1/cspm/scan", json={})
    data = resp.json()
    # CSPM-001 should NOT trigger for dev
    dev_001_findings = [f for f in data["findings"] if f["rule_id"] == "001" and f["asset_name"] == "dev-server"]
    assert len(dev_001_findings) == 0


@pytest.mark.asyncio
async def test_cspm_high_risk_score_triggers_finding(client: AsyncClient):
    await client.post("/api/v1/assets", json={
        "name": "legacy-prod-server",
        "asset_type": "server",
        "environment": "production",
        "risk_score": 80,
        "owner_email": "ops@example.com",
    })
    resp = await client.post("/api/v1/cspm/scan", json={})
    data = resp.json()
    rule_ids = [f["rule_id"] for f in data["findings"] if f["created"]]
    assert "004" in rule_ids


@pytest.mark.asyncio
async def test_cspm_findings_appear_in_vulnerabilities(client: AsyncClient):
    await client.post("/api/v1/assets", json={
        "name": "unowned-prod-api",
        "asset_type": "api",
        "environment": "production",
        # no owner → CSPM-001; no description → CSPM-005
    })
    scan_resp = await client.post("/api/v1/cspm/scan", json={})
    assert scan_resp.json()["new_findings"] >= 1

    vuln_resp = await client.get("/api/v1/vulnerabilities")
    cve_ids = [v["cve_id"] for v in vuln_resp.json()["items"]]
    assert any(cid and cid.startswith("CSPM-") for cid in cve_ids)


@pytest.mark.asyncio
async def test_cspm_scan_specific_asset_ids(client: AsyncClient):
    a1 = await client.post("/api/v1/assets", json={
        "name": "prod-target",
        "asset_type": "server",
        "environment": "production",
    })
    a1_id = a1.json()["id"]
    await client.post("/api/v1/assets", json={
        "name": "prod-other",
        "asset_type": "server",
        "environment": "production",
    })
    resp = await client.post("/api/v1/cspm/scan", json={"asset_ids": [a1_id]})
    data = resp.json()
    assert data["scanned_assets"] == 1
    for finding in data["findings"]:
        assert finding["asset_id"] == a1_id
