"""Tests for P2.1 Threat Intelligence feature."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_feed(client: AsyncClient):
    """Test creating a threat feed and verifying the response."""
    resp = await client.post("/api/v1/threat-intel/feeds", json={
        "name": "Emerging Threats IP Blocklist",
        "feed_type": "ip_blocklist",
        "source_url": "https://rules.emergingthreats.net/blocklists/compromised-ips.txt",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Emerging Threats IP Blocklist"
    assert data["feed_type"] == "ip_blocklist"
    assert data["is_active"] is True
    assert data["ioc_count"] == 0
    assert data["last_synced"] is None
    assert data["iocs"] == []


@pytest.mark.asyncio
async def test_sync_feed_creates_iocs(client: AsyncClient):
    """Test that syncing a feed generates IOC records and updates ioc_count."""
    feed_resp = await client.post("/api/v1/threat-intel/feeds", json={
        "name": "Domain Blocklist",
        "feed_type": "domain_blocklist",
        "source_url": "https://example.com/blocklist.txt",
    })
    assert feed_resp.status_code == 201
    feed_id = feed_resp.json()["id"]

    sync_resp = await client.post(f"/api/v1/threat-intel/feeds/{feed_id}/sync")
    assert sync_resp.status_code == 200
    data = sync_resp.json()
    assert data["ioc_count"] > 0
    assert data["last_synced"] is not None

    # Verify IOCs are listed
    iocs_resp = await client.get("/api/v1/threat-intel/iocs")
    assert iocs_resp.status_code == 200
    assert iocs_resp.json()["total"] >= data["ioc_count"]


@pytest.mark.asyncio
async def test_list_iocs_with_type_filter(client: AsyncClient):
    """Test listing IOCs filtered by ioc_type."""
    # Create an ip_blocklist feed and sync
    feed_resp = await client.post("/api/v1/threat-intel/feeds", json={
        "name": "IP Blocklist",
        "feed_type": "ip_blocklist",
    })
    feed_id = feed_resp.json()["id"]
    await client.post(f"/api/v1/threat-intel/feeds/{feed_id}/sync")

    # Create a hash_list feed and sync
    hash_feed_resp = await client.post("/api/v1/threat-intel/feeds", json={
        "name": "Malware Hash List",
        "feed_type": "hash_list",
    })
    hash_feed_id = hash_feed_resp.json()["id"]
    await client.post(f"/api/v1/threat-intel/feeds/{hash_feed_id}/sync")

    # Filter by ip type
    ip_resp = await client.get("/api/v1/threat-intel/iocs?ioc_type=ip")
    assert ip_resp.status_code == 200
    ip_data = ip_resp.json()
    assert ip_data["total"] > 0
    for ioc in ip_data["items"]:
        assert ioc["ioc_type"] == "ip"

    # Filter by hash type
    hash_resp = await client.get("/api/v1/threat-intel/iocs?ioc_type=hash")
    assert hash_resp.status_code == 200
    hash_data = hash_resp.json()
    assert hash_data["total"] > 0
    for ioc in hash_data["items"]:
        assert ioc["ioc_type"] == "hash"


@pytest.mark.asyncio
async def test_create_manual_ioc(client: AsyncClient):
    """Test creating a manual IOC without a feed."""
    resp = await client.post("/api/v1/threat-intel/iocs", json={
        "ioc_type": "ip",
        "value": "198.51.100.42",
        "threat_type": "c2",
        "confidence_score": 95.0,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["ioc_type"] == "ip"
    assert data["value"] == "198.51.100.42"
    assert data["threat_type"] == "c2"
    assert data["confidence_score"] == 95.0
    assert data["feed_id"] is None
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_check_asset_against_iocs(client: AsyncClient):
    """Test checking an asset against IOCs — should return matching IOCs."""
    # Create an asset first
    asset_resp = await client.post("/api/v1/assets", json={
        "name": "prod-web-server-01",
        "asset_type": "server",
        "environment": "production",
        "cloud_provider": "aws",
        "region": "us-east-1",
        "owner_email": "ops@example.com",
    })
    assert asset_resp.status_code == 201
    asset_id = asset_resp.json()["id"]

    # Create a feed and sync to get IOCs in the DB
    feed_resp = await client.post("/api/v1/threat-intel/feeds", json={
        "name": "Test IP Feed",
        "feed_type": "ip_blocklist",
    })
    feed_id = feed_resp.json()["id"]
    await client.post(f"/api/v1/threat-intel/feeds/{feed_id}/sync")

    # Check asset against IOCs
    check_resp = await client.get(f"/api/v1/threat-intel/iocs/check/{asset_id}")
    assert check_resp.status_code == 200
    matches = check_resp.json()
    # Demo fallback ensures up to 2 active IOCs are returned when they exist
    assert isinstance(matches, list)
    assert len(matches) <= 2
    # If IOCs were created, we should get matches
    iocs_resp = await client.get("/api/v1/threat-intel/iocs")
    if iocs_resp.json()["total"] > 0:
        assert len(matches) > 0
