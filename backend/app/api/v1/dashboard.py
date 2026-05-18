"""Dashboard stats aggregation."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.core.database import get_db
from app.models.asset import Asset
from app.models.vulnerability import Vulnerability
from app.models.security_scan import SecurityScan
from app.models.policy import Policy, PolicyAcknowledgment, PolicyStatus
from app.models.compliance import ComplianceFramework, ComplianceControl, ControlStatus

router = APIRouter(prefix="/stats", tags=["dashboard"])


@router.get("")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Return aggregated security posture statistics."""
    # Assets
    total_assets = (await db.execute(select(func.count()).select_from(Asset))).scalar() or 0

    # Vulnerabilities
    total_vulnerabilities = (await db.execute(select(func.count()).select_from(Vulnerability))).scalar() or 0
    critical_vulnerabilities = (
        await db.execute(select(func.count()).select_from(Vulnerability).where(Vulnerability.severity == "critical"))
    ).scalar() or 0
    open_vulnerabilities = (
        await db.execute(select(func.count()).select_from(Vulnerability).where(Vulnerability.status == "open"))
    ).scalar() or 0

    # Scans
    total_scans = (await db.execute(select(func.count()).select_from(SecurityScan))).scalar() or 0

    # Assets by environment
    env_rows = (await db.execute(select(Asset.environment, func.count()).group_by(Asset.environment))).all()
    assets_by_environment = {env: count for env, count in env_rows}

    # Vulnerabilities by severity
    sev_rows = (await db.execute(select(Vulnerability.severity, func.count()).group_by(Vulnerability.severity))).all()
    vulnerabilities_by_severity = {sev: count for sev, count in sev_rows}

    # Recent scans (last 5)
    recent_scans = list(
        (await db.execute(select(SecurityScan).order_by(SecurityScan.created_at.desc()).limit(5))).scalars().all()
    )

    # Policy acknowledgment stats
    published_requiring_ack = (
        await db.execute(
            select(func.count()).select_from(Policy)
            .where(Policy.status == PolicyStatus.PUBLISHED, Policy.requires_acknowledgment == True)
        )
    ).scalar() or 0
    total_acknowledgments = (
        await db.execute(
            select(func.count()).select_from(PolicyAcknowledgment)
            .where(PolicyAcknowledgment.acknowledged_at.isnot(None))
        )
    ).scalar() or 0

    # Compliance posture per active framework
    fw_rows = list(
        (await db.execute(select(ComplianceFramework).where(ComplianceFramework.is_active == True))).scalars().all()
    )
    compliance_posture = []
    for fw in fw_rows:
        total_ctrl = (
            await db.execute(select(func.count()).select_from(ComplianceControl).where(ComplianceControl.framework_id == fw.id))
        ).scalar() or 0
        impl_ctrl = (
            await db.execute(
                select(func.count()).select_from(ComplianceControl)
                .where(ComplianceControl.framework_id == fw.id, ComplianceControl.status == ControlStatus.IMPLEMENTED)
            )
        ).scalar() or 0
        na_ctrl = (
            await db.execute(
                select(func.count()).select_from(ComplianceControl)
                .where(ComplianceControl.framework_id == fw.id, ComplianceControl.status == ControlStatus.NOT_APPLICABLE)
            )
        ).scalar() or 0
        applicable = total_ctrl - na_ctrl
        pct = round(impl_ctrl / applicable * 100, 1) if applicable > 0 else 0.0
        compliance_posture.append({
            "framework_id": str(fw.id),
            "framework_name": fw.name,
            "slug": fw.slug,
            "total_controls": total_ctrl,
            "implemented_controls": impl_ctrl,
            "compliance_pct": pct,
        })

    return {
        "total_assets": total_assets,
        "total_vulnerabilities": total_vulnerabilities,
        "critical_vulnerabilities": critical_vulnerabilities,
        "open_vulnerabilities": open_vulnerabilities,
        "total_scans": total_scans,
        "assets_by_environment": assets_by_environment,
        "vulnerabilities_by_severity": vulnerabilities_by_severity,
        "recent_scans": recent_scans,
        "published_policies_requiring_ack": published_requiring_ack,
        "total_acknowledgments": total_acknowledgments,
        "compliance_posture": compliance_posture,
    }
