"""CSPM mock scan router."""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.vulnerability import Vulnerability, VulnSeverity, VulnStatus
from app.models.asset import Asset
from app.repositories.asset_repo import AssetRepository
from app.services.cspm_service import evaluate_asset

router = APIRouter(tags=["cspm"])


class CspmScanRequest(BaseModel):
    asset_ids: list[uuid.UUID] | None = None  # None = scan all assets


class CspmFindingResult(BaseModel):
    asset_id: uuid.UUID
    asset_name: str
    rule_id: str
    cve_id: str
    title: str
    severity: str
    created: bool  # False if the finding already existed


class CspmScanResponse(BaseModel):
    scanned_assets: int
    new_findings: int
    skipped_duplicates: int
    findings: list[CspmFindingResult]


@router.post("/cspm/scan", response_model=CspmScanResponse)
async def run_cspm_scan(
    payload: CspmScanRequest,
    db: AsyncSession = Depends(get_db),
):
    """Evaluate assets against CIS-style rules and create Vulnerability records."""
    asset_repo = AssetRepository(db)

    if payload.asset_ids:
        assets = []
        for aid in payload.asset_ids:
            a = await asset_repo.get_by_id(aid)
            if not a:
                raise HTTPException(status_code=404, detail=f"Asset {aid} not found")
            assets.append(a)
    else:
        result = await db.execute(select(Asset))
        assets = list(result.scalars().all())

    results: list[CspmFindingResult] = []
    new_count = 0
    skip_count = 0

    for asset in assets:
        findings = evaluate_asset(asset)
        for finding in findings:
            cve_id = f"CSPM-{finding.rule_id}"
            # Idempotent: skip if this exact rule already exists for this asset
            existing = await db.execute(
                select(Vulnerability).where(
                    Vulnerability.asset_id == asset.id,
                    Vulnerability.cve_id == cve_id,
                    Vulnerability.status != VulnStatus.RESOLVED,
                )
            )
            if existing.scalar_one_or_none():
                skip_count += 1
                results.append(CspmFindingResult(
                    asset_id=asset.id, asset_name=asset.name,
                    rule_id=finding.rule_id, cve_id=cve_id,
                    title=finding.title, severity=finding.severity, created=False,
                ))
                continue

            vuln = Vulnerability(
                asset_id=asset.id,
                title=finding.title,
                description=finding.description,
                severity=VulnSeverity(finding.severity),
                cve_id=cve_id,
                status=VulnStatus.OPEN,
                remediation="Review the flagged configuration and remediate per CIS benchmark guidance.",
            )
            db.add(vuln)
            new_count += 1
            results.append(CspmFindingResult(
                asset_id=asset.id, asset_name=asset.name,
                rule_id=finding.rule_id, cve_id=cve_id,
                title=finding.title, severity=finding.severity, created=True,
            ))

    await db.commit()
    return CspmScanResponse(
        scanned_assets=len(assets),
        new_findings=new_count,
        skipped_duplicates=skip_count,
        findings=results,
    )
