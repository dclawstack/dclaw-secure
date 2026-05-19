"""Threat Intelligence service — feed sync and IOC matching."""

import random
import secrets
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.threat_intel import FeedType, IOCType, ThreatFeed, ThreatIOC
from app.models.asset import Asset


def _random_ip() -> str:
    """Generate a random IP address (mix of RFC1918 and public)."""
    choice = random.randint(0, 2)
    if choice == 0:
        return f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    elif choice == 1:
        return f"192.168.{random.randint(0,255)}.{random.randint(1,254)}"
    else:
        return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"


def _random_domain() -> str:
    """Generate a realistic-looking malicious domain."""
    prefixes = ["secure", "update", "cdn", "login", "auth", "pay", "support", "download"]
    tlds = [".ru", ".cn", ".tk", ".xyz", ".top", ".pw", ".cc"]
    mid = secrets.token_hex(4)
    return f"{random.choice(prefixes)}-{mid}{random.choice(tlds)}"


def _random_sha256() -> str:
    """Generate a fake SHA256 hash (64 hex chars)."""
    return secrets.token_hex(32)


def _random_cve() -> str:
    """Generate a realistic CVE ID."""
    year = random.choice([2023, 2024, 2025])
    num = random.randint(1000, 59999)
    return f"CVE-{year}-{num}"


_THREAT_TYPES_IP = ["botnet", "c2", "scanner"]
_THREAT_TYPES_DOMAIN = ["malware", "phishing", "c2"]
_THREAT_TYPES_HASH = ["ransomware", "trojan", "spyware"]


def mock_sync_feed(feed: ThreatFeed) -> list[dict]:
    """Generate 5–15 realistic IOCs for the given feed type."""
    count = random.randint(5, 15)
    iocs: list[dict] = []

    if feed.feed_type == FeedType.ip_blocklist:
        for _ in range(count):
            iocs.append({
                "ioc_type": IOCType.ip,
                "value": _random_ip(),
                "threat_type": random.choice(_THREAT_TYPES_IP),
                "confidence_score": round(random.uniform(50, 99), 1),
            })

    elif feed.feed_type == FeedType.domain_blocklist:
        for _ in range(count):
            iocs.append({
                "ioc_type": IOCType.domain,
                "value": _random_domain(),
                "threat_type": random.choice(_THREAT_TYPES_DOMAIN),
                "confidence_score": round(random.uniform(60, 99), 1),
            })

    elif feed.feed_type == FeedType.hash_list:
        for _ in range(count):
            iocs.append({
                "ioc_type": IOCType.hash,
                "value": _random_sha256(),
                "threat_type": random.choice(_THREAT_TYPES_HASH),
                "confidence_score": round(random.uniform(70, 99), 1),
            })

    elif feed.feed_type == FeedType.cve_feed:
        for _ in range(count):
            iocs.append({
                "ioc_type": IOCType.cve,
                "value": _random_cve(),
                "threat_type": "vulnerability",
                "confidence_score": round(random.uniform(80, 99), 1),
            })

    else:  # custom — mix of types
        generators = [
            lambda: {"ioc_type": IOCType.ip, "value": _random_ip(), "threat_type": random.choice(_THREAT_TYPES_IP)},
            lambda: {"ioc_type": IOCType.domain, "value": _random_domain(), "threat_type": random.choice(_THREAT_TYPES_DOMAIN)},
            lambda: {"ioc_type": IOCType.hash, "value": _random_sha256(), "threat_type": random.choice(_THREAT_TYPES_HASH)},
        ]
        for _ in range(count):
            entry = random.choice(generators)()
            entry["confidence_score"] = round(random.uniform(50, 99), 1)
            iocs.append(entry)

    return iocs


async def check_asset_against_iocs(asset_id: uuid.UUID, db: AsyncSession) -> list[ThreatIOC]:
    """Check an asset against active IOCs and return matches.

    For demo purposes: always return the first 2 active IOCs if they exist,
    plus any explicit field matches (domain or email).
    """
    # Load the asset
    asset_result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = asset_result.scalar_one_or_none()
    if not asset:
        return []

    # Load all active IOCs
    ioc_result = await db.execute(
        select(ThreatIOC).where(ThreatIOC.is_active == True)
    )
    active_iocs: list[ThreatIOC] = list(ioc_result.scalars().all())

    matches: list[ThreatIOC] = []
    matched_ids: set[uuid.UUID] = set()

    # Check for explicit field matches
    for ioc in active_iocs:
        if ioc.id in matched_ids:
            continue
        # Domain matches: asset name or region vs domain IOC
        if ioc.ioc_type == IOCType.domain:
            asset_name_lower = (asset.name or "").lower()
            region_lower = (asset.region or "").lower()
            ioc_val = ioc.value.lower()
            if ioc_val in asset_name_lower or ioc_val in region_lower:
                matches.append(ioc)
                matched_ids.add(ioc.id)
                continue
        # Email matches: owner_email vs email IOC
        if ioc.ioc_type == IOCType.email and asset.owner_email:
            if ioc.value.lower() == asset.owner_email.lower():
                matches.append(ioc)
                matched_ids.add(ioc.id)
                continue

    # Demo fallback: always return first 2 active IOCs for any asset
    for ioc in active_iocs:
        if len(matches) >= 2:
            break
        if ioc.id not in matched_ids:
            matches.append(ioc)
            matched_ids.add(ioc.id)

    return matches[:2]
