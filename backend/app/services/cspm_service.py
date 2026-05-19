"""CSPM mock — evaluates assets against CIS-style rules and generates Vulnerability records."""

from dataclasses import dataclass
from app.models.asset import Asset, AssetType, Environment


@dataclass
class CspmFinding:
    rule_id: str      # used as cve_id prefix: "CSPM-{rule_id}"
    title: str
    description: str
    severity: str     # critical | high | medium | low


def evaluate_asset(asset: Asset) -> list[CspmFinding]:
    """Run all CSPM rules against a single asset and return triggered findings."""
    findings: list[CspmFinding] = []

    def _add(rule_id: str, title: str, desc: str, severity: str) -> None:
        findings.append(CspmFinding(rule_id=rule_id, title=title, description=desc, severity=severity))

    env = asset.environment.value if asset.environment else ""
    atype = asset.asset_type.value if asset.asset_type else ""
    name_lower = asset.name.lower()

    # CSPM-001: Production asset with no owner assigned
    if env == "production" and not asset.owner_email:
        _add(
            "001",
            f"Unowned production asset: {asset.name}",
            "Production assets must have an owner email for accountability and incident response.",
            "medium",
        )

    # CSPM-002: S3 bucket with "public" in name or description
    if atype == "s3_bucket" and ("public" in name_lower or (asset.description and "public" in asset.description.lower())):
        _add(
            "002",
            f"Potentially public S3 bucket: {asset.name}",
            "S3 bucket name or description suggests public access. Verify bucket ACLs and block public access settings.",
            "high",
        )

    # CSPM-003: Production database with no cloud_provider set (unknown hosting)
    if env == "production" and atype == "database" and not asset.cloud_provider:
        _add(
            "003",
            f"Production database with unknown hosting: {asset.name}",
            "Production databases should have a documented cloud provider or on-premise designation.",
            "low",
        )

    # CSPM-004: Production asset with high risk score (>= 75) already flagged
    if env == "production" and asset.risk_score and asset.risk_score >= 75:
        _add(
            "004",
            f"High-risk production asset: {asset.name}",
            f"Asset has a risk score of {asset.risk_score}/100 in production. Immediate review required.",
            "high",
        )

    # CSPM-005: Production API with no description (undocumented exposure)
    if env == "production" and atype == "api" and not asset.description:
        _add(
            "005",
            f"Undocumented production API: {asset.name}",
            "Production API endpoints must be documented to understand attack surface and access controls.",
            "medium",
        )

    # CSPM-006: Asset named with dev/test keywords but in production environment
    if env == "production" and any(kw in name_lower for kw in ["test", "dev", "demo", "sandbox", "poc"]):
        _add(
            "006",
            f"Dev/test asset in production environment: {asset.name}",
            "Asset name suggests it is a non-production resource but is classified as production. Verify environment classification.",
            "high",
        )

    # CSPM-007: Production server or container with no region set
    if env == "production" and atype in ("server", "container") and not asset.region:
        _add(
            "007",
            f"Production {atype} with no region set: {asset.name}",
            "Production compute resources should have a region documented for disaster recovery planning.",
            "low",
        )

    # CSPM-008: Production workstation with no owner
    if env == "production" and atype == "workstation" and not asset.owner_email:
        _add(
            "008",
            f"Unowned production workstation: {asset.name}",
            "Production workstations must be assigned to a specific user for access control and audit purposes.",
            "medium",
        )

    # CSPM-009: Domain asset in production with no description (no security contact documented)
    if env == "production" and atype == "domain" and not asset.description:
        _add(
            "009",
            f"Undocumented production domain: {asset.name}",
            "Production domains should document purpose, owner, and certificate renewal contacts.",
            "low",
        )

    # CSPM-010: Repository in production with high risk score
    if atype == "repository" and asset.risk_score and asset.risk_score >= 60:
        _add(
            "010",
            f"High-risk code repository: {asset.name}",
            f"Repository has a risk score of {asset.risk_score}/100. Review secrets scanning, dependency vulnerabilities, and access controls.",
            "medium",
        )

    return findings
