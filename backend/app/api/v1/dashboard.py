"""Dashboard stats aggregation."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.core.database import get_db
from app.models.asset import Asset
from app.models.vulnerability import Vulnerability
from app.models.security_scan import SecurityScan

router = APIRouter(prefix="/stats", tags=["dashboard"])


@router.get("")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Return aggregated security posture statistics."""
    # Total assets
    total_assets_result = await db.execute(select(func.count()).select_from(Asset))
    total_assets = total_assets_result.scalar() or 0

    # Total vulnerabilities
    total_vulns_result = await db.execute(
        select(func.count()).select_from(Vulnerability)
    )
    total_vulnerabilities = total_vulns_result.scalar() or 0

    # Critical vulnerabilities
    critical_vulns_result = await db.execute(
        select(func.count())
        .select_from(Vulnerability)
        .where(Vulnerability.severity == "critical")
    )
    critical_vulnerabilities = critical_vulns_result.scalar() or 0

    # Open vulnerabilities
    open_vulns_result = await db.execute(
        select(func.count())
        .select_from(Vulnerability)
        .where(Vulnerability.status == "open")
    )
    open_vulnerabilities = open_vulns_result.scalar() or 0

    # Total scans
    total_scans_result = await db.execute(
        select(func.count()).select_from(SecurityScan)
    )
    total_scans = total_scans_result.scalar() or 0

    # Assets by environment
    env_counts_result = await db.execute(
        select(Asset.environment, func.count())
        .group_by(Asset.environment)
    )
    assets_by_environment = {
        env: count for env, count in env_counts_result.all()
    }

    # Vulnerabilities by severity
    severity_counts_result = await db.execute(
        select(Vulnerability.severity, func.count())
        .group_by(Vulnerability.severity)
    )
    vulnerabilities_by_severity = {
        sev: count for sev, count in severity_counts_result.all()
    }

    # Recent scans (last 5)
    recent_scans_result = await db.execute(
        select(SecurityScan)
        .order_by(SecurityScan.created_at.desc())
        .limit(5)
    )
    recent_scans = list(recent_scans_result.scalars().all())

    return {
        "total_assets": total_assets,
        "total_vulnerabilities": total_vulnerabilities,
        "critical_vulnerabilities": critical_vulnerabilities,
        "open_vulnerabilities": open_vulnerabilities,
        "total_scans": total_scans,
        "assets_by_environment": assets_by_environment,
        "vulnerabilities_by_severity": vulnerabilities_by_severity,
        "recent_scans": recent_scans,
    }
